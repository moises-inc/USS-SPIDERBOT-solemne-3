# ============================================================
# USS SPIDERBOT — Servidor Web Asíncrono y Dashboard Embebido
# Solemne 3 — Taller de Programación I
# Microcontrolador: ESP32
# Lenguaje: MicroPython
# ============================================================

import network
import uasyncio as asyncio
import state
import gc

def iniciar_wifi(ssid="USS_SpiderBot_AP", password=None, modo_ap=True):
    """
    Inicializa la interfaz Wi-Fi de la ESP32.
    Por defecto opera en modo Access Point (AP) para exhibición offline directa.
    """
    if modo_ap:
        print(f"Configurando Wi-Fi en modo Access Point (AP): {ssid}...")
        ap = network.WLAN(network.AP_IF)
        ap.active(True)
        # Limitar clientes a 4 para resguardar recursos de memoria en la ESP32
        ap.config(essid=ssid, max_clients=4)
        if password:
            ap.config(password=password, authmode=network.AUTH_WPA_WPA2_PSK)
        else:
            ap.config(authmode=network.AUTH_OPEN)
        
        ip = ap.ifconfig()[0]
        print(f"[OK] Red AP Lista. Conéctate a '{ssid}'")
        print(f"     Abre en tu navegador: http://{ip}/")
        return ip
    else:
        # Modo Estación (STA) - Desactivado por defecto
        # Preparado para conectar a un router externo dedicado si es necesario
        print(f"Conectando a red Wi-Fi existente (Router): {ssid}...")
        sta = network.WLAN(network.STA_IF)
        sta.active(True)
        sta.connect(ssid, password)
        
        # Esperar hasta 10 segundos por conexión
        for i in range(20):
            if sta.isconnected():
                ip = sta.ifconfig()[0]
                print(f"[OK] Conectado a red del Router. IP asignada: {ip}")
                return ip
            import time
            time.sleep_ms(500)
            
        print("[WARNING] No se pudo conectar a la red del router.")
        print("         Revirtiendo automáticamente a modo Access Point...")
        return iniciar_wifi(ssid, password, modo_ap=True)

async def serve_html_file(writer, filename):
    """Lee y sirve un archivo HTML por bloques de 512 bytes para evitar sobrecarga de memoria heap."""
    try:
        writer.write(b"HTTP/1.1 200 OK\r\n")
        writer.write(b"Content-Type: text/html\r\n")
        writer.write(b"Connection: close\r\n\r\n")
        with open(filename, "r") as f:
            while True:
                chunk = f.read(512)
                if not chunk:
                    break
                writer.write(chunk.encode('utf-8'))
    except OSError:
        writer.write(("<h1>[ERROR] Archivo %s no encontrado en la flash.</h1>" % filename).encode('utf-8'))

async def handle_client(reader, writer):
    """Procesa las peticiones HTTP entrantes de forma asíncrona y no bloqueante."""
    try:
        # Forzar recolección de basura al inicio de la petición para evitar fragmentación de RAM
        gc.collect()
        
        request_line = await reader.readline()
        if not request_line:
            return
            
        req = request_line.decode('utf-8')
        
        # Consumir el resto de las cabeceras HTTP para vaciar el buffer del socket
        while True:
            line = await reader.readline()
            if line == b'\r\n' or line == b'\n' or not line:
                break
                
        parts = req.split(' ')
        if len(parts) < 2:
            return
            
        method = parts[0]
        path = parts[1]
        
        # ── ENDPOINT: API de Control de Movimiento y Estabilización ──
        if path.startswith("/api/control"):
            # Buscar parámetro de comando: cmd=...
            if "cmd=" in path:
                cmd = path.split("cmd=")[1].split("&")[0]
                if cmd in ["forward", "backward", "left", "right", "stop", "reposo"]:
                    state.comando_actual = cmd
                    print(f"[WEB] Control recibido: {cmd}")
            
            # Buscar parámetro de estabilización: stabilize=0 o 1
            if "stabilize=" in path:
                stab = path.split("stabilize=")[1].split("&")[0]
                state.estabilizacion_activa = (stab == "1")
                print(f"[WEB] Estabilización activa set a: {state.estabilizacion_activa}")
                
            response = '{"status":"ok","comando":"%s","stabilize":%d}' % (
                state.comando_actual,
                1 if state.estabilizacion_activa else 0
            )
            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Content-Type: application/json\r\n")
            writer.write(b"Access-Control-Allow-Origin: *\r\n")
            writer.write(b"Connection: close\r\n\r\n")
            writer.write(response.encode('utf-8'))
            
        # ── ENDPOINT: API de Telemetría (Frecuencia de lectura externa ~4Hz) ──
        elif path.startswith("/telemetry"):
            response = '{"pitch":%.1f,"roll":%.1f,"distance":%.1f,"cmd":"%s","stabilize":%d}' % (
                state.pitch_actual,
                state.roll_actual,
                state.distancia_actual,
                state.comando_actual,
                1 if state.estabilizacion_activa else 0
            )
            writer.write(b"HTTP/1.1 200 OK\r\n")
            writer.write(b"Content-Type: application/json\r\n")
            writer.write(b"Access-Control-Allow-Origin: *\r\n")
            writer.write(b"Connection: close\r\n\r\n")
            writer.write(response.encode('utf-8'))
            
        # ── ENDPOINT: Servir HTML del Dashboard (Desde almacenamiento Flash) ──
        elif path == "/" or path == "/dashboard.html":
            await serve_html_file(writer, "dashboard.html")
        elif path == "/index.html":
            await serve_html_file(writer, "index.html")
                
        else:
            writer.write(b"HTTP/1.1 404 Not Found\r\n")
            writer.write(b"Content-Type: text/plain\r\n")
            writer.write(b"Connection: close\r\n\r\n")
            writer.write(b"404 Not Found")
            
        await writer.drain()
    except Exception as e:
        print("[WARNING] Error en handler HTTP:", e)
    finally:
        try:
            await writer.close()
        except:
            pass

async def start_server_task(ip):
    """Inicia el socket del servidor HTTP asíncrono en la ESP32."""
    print("Iniciando socket del servidor HTTP...")
    server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
    print(f"[OK] Servidor HTTP escuchando activamente en puerto 80.")
    while True:
        await asyncio.sleep(3600) # Mantener la corrutina viva
