# Guía Completa de OpenSCAD: Del Cubo al Robot Cuadrúpedo

Aprende OpenSCAD desde cero modelando paso a paso las piezas del **USS SpiderBot**, un robot cuadrúpedo de 8 grados de libertad. Todos los ejemplos reales están extraídos de los archivos fuente en `cad/` del repositorio.

---

## Introducción

**OpenSCAD** es un modelador CAD 3D basado exclusivamente en código (CSG — Constructive Solid Geometry). A diferencia de herramientas como Fusion 360 o TinkerCAD, aquí no arrastras mouse: escribes instrucciones y el programa las evalúa para generar geometría.

### ¿Por qué OpenSCAD para robótica?

- **Totalmente paramétrico**: cambias un número y todo el modelo se actualiza.
- **Versionable**: los archivos `.scad` son texto plano, ideales para Git.
- **Preciso**: las operaciones booleanas son exactas, no hay errores de manifold.
- **Gratuito y open-source**.
- **CLI headless**: puedes exportar STLs desde scripts.

### Instalación

| Sistema | Comando / Enlace |
|---------|------------------|
| Windows | Descargar installer desde [openscad.org](https://openscad.org) |
| macOS   | `brew install openscad` o descargar .dmg |
| Linux   | `sudo apt install openscad` (Debian/Ubuntu) / `sudo pacman -S openscad` (Arch) |

### Interfaz

Al abrir OpenSCAD ves tres paneles:

1. **Editor de código** (izquierda) — aquí escribes.
2. **Vista 3D** (derecha) — aquí ves el resultado.
3. **Consola** (abajo) — muestra errores, advertencias y outputs.

### Flujo de trabajo

1. Escribes código en el editor.
2. Presionas **F5** — *Preview* (vista rápida, usa OpenCSG).
3. Presionas **F6** — *Render* (cálculo CGAL completo, geometría exacta).
4. Archivo > Exportar > Exportar como STL (o **F7**) — obtienes el archivo para impresión 3D.

---

## Capítulo 1: Fundamentos Geométricos

### Formas primitivas 3D

OpenSCAD tiene cuatro formas sólidas básicas:

```openscad
// Cubo: cube([ancho, fondo, alto], center);
cube([10, 20, 30]);                    // Esquina en el origen
cube([10, 20, 30], center=true);       // Centrado en el origen

// Esfera: sphere(r);
sphere(r = 10);                        // Radio 10mm

// Cilindro: cylinder(r, h);
cylinder(r = 5, h = 20);               // Radio 5mm, altura 20mm

// Cilindro con radios distintos (cono truncado):
cylinder(r1 = 5, r2 = 3, h = 10);
```

### Sistema de coordenadas

OpenSCAD usa coordenadas cartesianas diestras:
- **Eje X**: horizontal (derecha = positivo)
- **Eje Y**: profundidad (atrás = positivo)
- **Eje Z**: vertical (arriba = positivo)

### El parámetro `center`

Por defecto, `cube()`, `cylinder()` y `sphere()` se posicionan con una esquina o base en el origen:

```openscad
// Sin center: el cubo crece desde (0,0,0) hacia (10,20,30)
cube([10, 20, 30]);

// Con center=true: el cubo se centra en (0,0,0), va de (-5,-10,-15) a (5,10,15)
cube([10, 20, 30], center=true);
```

### Resolución de curvas: `$fn`, `$fa`, `$fs`

Las formas curvas (`sphere`, `cylinder`) se aproximan con polígonos:

```openscad
// $fn controla el número de fragmentos (lados)
cylinder(r = 10, h = 20, $fn = 6);    // Hexágono — baja calidad
cylinder(r = 10, h = 20, $fn = 20);   // Aceptable
cylinder(r = 10, h = 20, $fn = 100);  // Muy suave — render lento

// También se puede definir globalmente
$fn = 50;  // Todas las curvas usarán 50 fragmentos
```

> **Regla práctica:** `$fn = 30` para preview rápido, `$fn = 50-80` para exportación a STL.

### 🕷️ Caso Real: Primitivas en el SpiderBot

En `cad/cuerpo_cuadruepdo.scad`, la placa base se define con `cylinder()`:

```openscad
// Archivo: cad/cuerpo_cuadruepdo.scad
$fn = 50;

cuerpo_r = 65.0;    // Radio del chasis circular
cuerpo_t = 3.0;     // Grosor de las placas

module placa_base_cuadruepodo() {
    difference() {
        // Placa inferior sólida: un cilindro de 65mm de radio, 3mm de grosor
        cylinder(r = cuerpo_r, h = cuerpo_t, center=true);

        // Agujeros para los 4 pilares espaciadores M3
        for (a = [0, 90, 180, 270]) {
            rotate([0, 0, a])
                translate([spacer_r, 0, 0])
                    cylinder(r=1.6, h=cuerpo_t+2, center=true);  // Agujero pasante
        }
    }
}
```

El chasis completo se construye a partir de dos cilindros concéntricos (placa base y placa superior). Observa cómo `cylinder()` con `center=true` facilita la simetría vertical.

---

## Capítulo 2: Transformaciones Geométricas

Las transformaciones mueven, rotan y escalan objetos. **No crean geometría nueva**, sino que modifican la existente.

### `translate([x, y, z])`

Desplaza el objeto hijo en el espacio:

```openscad
// Mueve un cubo 20mm en X, 10mm en Y, 5mm en Z
translate([20, 10, 5])
    cube([10, 10, 10]);
```

### `rotate([x, y, z])`

Rota alrededor del origen en grados, orden de ejes: X → Y → Z:

```openscad
// Rota 45° alrededor de Z
rotate([0, 0, 45])
    cube([20, 5, 5]);

// Rota 90° alrededor de X (pone el cubo vertical)
rotate([90, 0, 0])
    cube([20, 5, 5]);
```

### `scale([x, y, z])`

Escala en cada eje. `scale(v)` con un solo valor escala uniformemente:

```openscad
// No uniforme: estira en X
scale([2, 1, 1])
    sphere(r = 10);

// Uniforme: agranda todo al doble
scale(2)
    sphere(r = 10);
```

### Composición: se lee de adentro hacia afuera

Las transformaciones se aplican en orden inverso al que se escriben:

```openscad
// 1. Se crea el cubo en el origen
// 2. Se rota 45° en Z
// 3. Se traslada a (30, 0, 0)
translate([30, 0, 0])
    rotate([0, 0, 45])
        cube([10, 10, 10]);
```

### 🕷️ Caso Real: Rotaciones y traslaciones de los soportes de servo

En `cad/cuerpo_cuadruepdo.scad`, los 4 soportes de cadera se posicionan con una cadena de transformaciones:

```openscad
// Archivo: cad/cuerpo_cuadruepdo.scad — placa_base_cuadruepodo(), líneas 77-82

for (a = [45, 135, 225, 315]) {
    rotate([0, 0, a])                     // 2. Rota al ángulo de la pata
        translate([cuerpo_r - 7, 0, cuerpo_t/2])  // 1. Desplaza al borde del chasis
            rotate([0, 0, -90])           // 3. Orienta el bracket tangencialmente
                soporte_servo_cadera();   // 4. Instancia el bracket
}
```

Lee la cadena de adentro hacia afuera:
1. Se crea `soporte_servo_cadera()` en el origen.
2. Se rota -90° en Z para que quede tangente al círculo.
3. Se traslada al radio del chasis.
4. Se rota al ángulo de cada pata (45°, 135°, 225°, 315°).

---

## Capítulo 3: Operaciones Booleanas (El Corazón del Diseño)

Las operaciones booleanas combinan sólidos para crear formas complejas.

### `union()`

Fusiona todos los hijos en un solo sólido:

```openscad
union() {
    cube([10, 10, 10]);
    translate([5, 5, 0])
        cylinder(r = 5, h = 10);
}
```

### `difference()`

Resta los hijos subsiguientes del primero:

```openscad
difference() {
    // Objeto principal: un cubo
    cube([20, 20, 10], center=true);

    // Objetos a restar: un cilindro (hace un agujero)
    translate([0, 0, -1])
        cylinder(r = 3, h = 12);
}
```

### `intersection()`

Devuelve solo el volumen compartido por todos los hijos:

```openscad
intersection() {
    sphere(r = 10);
    cube([10, 10, 10], center=true);
}
```

### Anidamiento

Las booleanas se anidan sin límite:

```openscad
difference() {
    union() {
        // Cuerpo principal
        cylinder(r = 20, h = 5);
        // Pestaña lateral
        translate([15, 0, 0])
            cube([10, 10, 5], center=true);
    }
    // Agujero pasante
    cylinder(r = 3, h = 10, center=true);
}
```

### 🕷️ Caso Real: El soporte de servo — análisis línea a línea

El módulo `soporte_servo_cadera()` en `cad/cuerpo_cuadruepdo.scad` es un ejemplo magistral de `difference()`:

```openscad
// Archivo: cad/cuerpo_cuadruepdo.scad — soporte_servo_cadera(), líneas 11-46

module soporte_servo_cadera() {
    difference() {
        // ── SÓLIDO BASE ──────────────────────────────────────────────
        // Bloque estructural de 36mm x 28mm x 15mm centrado en Z=7.5
        translate([0, 0, 7.5])
            cube([36, 28, 15], center=true);

        // ── SUSTRACCIONES ────────────────────────────────────────────

        // 1. Cavidad para el servo SG90 (dual-depth)
        //    - Parte inferior: 30mm de ancho (para cables)
        translate([0, 0, 2.9])
            cube([30.0, 24.2, 4.2], center=true);
        //    - Parte superior: 25mm de ancho (soporte roscado para tornillos M2)
        translate([0, 0, 9.5])
            cube([25.0, 24.2, 9.0], center=true);

        // 2. Ranura para las orejas/bridas del servo
        translate([0, 5.5, 7.5])
            cube([34.5, 3.2, 13.5], center=true);

        // 3. Agujeros pasantes para tornillos M2 (perforan en Y)
        translate([-14.25, 0, 7.5])
            rotate([90, 0, 0])
                cylinder(r=1.0, h=35, center=true);
        translate([14.25, 0, 7.5])
            rotate([90, 0, 0])
                cylinder(r=1.0, h=35, center=true);

        // 4. Abertura para la corona de salida del servo
        translate([5.5, 12.0, 7.5])
            rotate([90, 0, 0])
                cylinder(r=6.2, h=15, center=true);

        // 5. Rebaje para rotación libre del fémur
        translate([6.5, 12.0, 7.5])
            cube([23, 5, 16], center=true);
    }
}
```

**Concepto clave — Dual-depth pocket:** La cavidad del servo tiene dos anchos diferentes. La zona inferior (donde van los cables) es más ancha (30mm), mientras que la superior es más estrecha (25mm) para que los tornillos M2 tengan rosca dónde agarrar. Esto se logra con dos `cube()` en posiciones Z diferentes dentro del mismo `difference()`.

---

## Capítulo 4: Variables y Parámetros

### Declaración y asignación

En OpenSCAD las variables se asignan con `=` y son **inmutables** (no puedes reasignar):

```openscad
// Variables básicas
ancho = 20;
profundidad = 30;
alto = 10;

cube([ancho, profundidad, alto]);
```

### Variables paramétricas: diseño reconfigurable

El poder real aparece cuando defines todas las medidas como variables al inicio:

```openscad
// ═══ PARÁMETROS DEL DISEÑO ═══════════════════════════
longitud = 50;
ancho    = 20;
altura   = 10;
pared    = 2.0;
tornillo_r = 1.5;

// ═══ GEOMETRÍA ═══════════════════════════════════════
difference() {
    cube([longitud, ancho, altura]);
    translate([pared, pared, -1])
        cube([longitud - 2*pared, ancho - 2*pared, altura + 2]);
}
// Cambia 'longitud' de 50 a 80 y todo se reescala automáticamente
```

### Operador ternario

Útil para alternar entre configuraciones:

```openscad
usar_agujeros = true;  // Cambia a false para sólido

difference() {
    cube([30, 20, 10], center=true);
    if (usar_agujeros) {
        cylinder(r = 3, h = 12, center=true);
    }
}

// Alternativa con operador ternario (para valores, no bloques)
resolucion = (usar_agujeros ? 50 : 20);
```

### Constantes especiales

- `PI` = 3.14159...
- `undef` = valor indefinido (cuando una variable no se ha asignado)

```openscad
radio = 10;
circunferencia = 2 * PI * radio;  // 62.8318
echo(circunferencia);
```

### 🕷️ Caso Real: Variables paramétricas del SpiderBot

En `cad/eslabon_pata_cuadrupedo.scad`, las variables definen toda la cinemática de la pata:

```openscad
// Archivo: cad/eslabon_pata_cuadrupedo.scad — líneas 7-15

$fn = 30;

link_len = 55.0; // Longitud entre la cadera y la rodilla
link_h = 25.0;   // Altura en el extremo de la rodilla
link_t = 16.0;   // Grosor del bloque del servo rodilla

// Dimensiones del servo SG90
servo_w = 23.0;
servo_t = 12.5;
servo_h = 22.5;
ear_dist = 28.5;
```

**Ejercicio mental:** Si cambias `link_len = 55` a `link_len = 70`:
- La distancia entre cadera y rodilla aumenta de 55mm a 70mm.
- El bolsillo del servo de rodilla se desplaza automáticamente porque usa `link_len` en su `translate()`.
- El robot entero se reconfigura sin tocar ninguna otra línea.

```openscad
// El bolsillo del servo usa link_len:
translate([link_len - 5.5, -11.25, 0]) { ... }
// La abertura del engranaje también:
translate([link_len, 0, 0])
    rotate([90, 0, 0])
        cylinder(r=6, h=35, center=true);
```

---

## Capítulo 5: Módulos — Funciones del Diseño Paramétrico

Los módulos son equivalentes a funciones en los lenguajes de programación. Encapsulan geometría reutilizable.

### Sintaxis básica

```openscad
module nombre(param1, param2 = valor_defecto) {
    // Geometría aquí
}
```

### Ejemplo: un tornillo paramétrico

```openscad
module tornillo(longitud, diametro = 4) {
    radio = diametro / 2;
    cylinder(r = radio, h = longitud);
    translate([0, 0, longitud])
        cylinder(r = radio * 1.5, h = 3);
}

// Uso
tornillo(20);            // L=20, D=4 (usa valor por defecto)
tornillo(30, 6);         // L=30, D=6
tornillo(diametro=5, longitud=15);  // Argumentos nombrados
```

### DRY en CAD

El principio Don't Repeat Yourself se aplica directamente:

```openscad
// MAL: código duplicado
cube([10, 20, 5]);
translate([15, 0, 0]) cube([10, 20, 5]);
translate([30, 0, 0]) cube([10, 20, 5]);

// BIEN: con módulo
module bloque() {
    cube([10, 20, 5]);
}
bloque();
translate([15, 0, 0]) bloque();
translate([30, 0, 0]) bloque();
```

### 🕷️ Caso Real: Los 4 módulos del SpiderBot

El robot se construye con estos módulos reutilizables:

```openscad
// 1. Soporte de cadera (en cuerpo_cuadruepdo.scad, línea 11)
module soporte_servo_cadera() { ... }

// 2. Placa base (en cuerpo_cuadruepdo.scad, línea 48)
module placa_base_cuadruepodo() {
    // Llama a soporte_servo_cadera() 4 veces en un for
    for (a = [45, 135, 225, 315]) {
        rotate([0, 0, a])
            translate([cuerpo_r - 7, 0, cuerpo_t/2])
                rotate([0, 0, -90])
                    soporte_servo_cadera();
    }
}

// 3. Placa superior (en cuerpo_cuadruepdo.scad, línea 85)
module placa_superior() {
    // Cuna para protoboard, soporte para HC-SR04, gussets
    // Creada con union() anidada dentro de difference()
}

// 4. Fémur completo (en eslabon_pata_cuadrupedo.scad, línea 17)
module eslabon_completo() { ... }

// 5. Tibia (en tibia_pata.scad, línea 10)
module tibia() { ... }
```

La composición final ocurre en `cad/ensamble_cuadruepodo.scad`:

```openscad
// La pata completa articulada
module pata_articulada(angulo_cadera=0, angulo_rodilla=0) {
    // 1. Servo de cadera
    dummy_servo();
    // 2. Fémur (rotado según angulo_cadera)
    rotate([0, angulo_cadera, 0])
        eslabon_completo();
    // 3. Tibia (rotada según angulo_rodilla)
    translate([55, 2.75, 0])
        rotate([0, angulo_rodilla, 0])
            tibia();
}

// El ensamble completo instancia 4 patas
module ensamble_completo() {
    placa_base_cuadruepodo();
    placa_superior();
    for (a = [45, 135, 225, 315]) {
        pata_articulada(15, -45);
    }
}
```

---

## Capítulo 6: Iteración y Simetría — El Bucle `for`

El bucle `for` permite repetir geometría sin copiar y pegar código.

### Sintaxis

```openscad
// Rango inclusivo [inicio : incremento : fin]
for (i = [0 : 1 : 5]) {
    translate([i * 10, 0, 0])
        cube([5, 5, 5]);
}

// Rango simple [inicio : fin] (incremento = 1)
for (i = [0 : 5]) { ... }

// Lista explícita de valores
for (i = [10, 20, 30, 50]) { ... }
```

### Distribución radial con `for` + `rotate()`

El patrón más usado en robótica: distribuir objetos simétricamente alrededor de un círculo:

```openscad
// 6 agujeros equidistantes en un círculo de radio 40mm
for (angulo = [0 : 60 : 300]) {
    rotate([0, 0, angulo])
        translate([40, 0, 0])
            cylinder(r = 2, h = 10, center=true);
}
```

### Cuadrícula con `for` anidado

```openscad
// Matriz 4×3 de agujeros
for (x = [-30, -10, 10, 30]) {
    for (y = [-20, 0, 20]) {
        translate([x, y, 0])
            cylinder(r = 1.5, h = 10, center=true);
    }
}
```

### 🕷️ Caso Real: Las 4 patas del SpiderBot

En `cad/cuerpo_cuadruepdo.scad`, una sola línea con `for` instancia los 4 soportes de servo:

```openscad
// Archivo: cad/cuerpo_cuadruepdo.scad — líneas 77-82

// Distribuye 4 soportes en 45°, 135°, 225°, 315°
// (las diagonales del cuadrado, no los ejes)
for (a = [45, 135, 225, 315]) {
    rotate([0, 0, a])              // Gira al cuadrante de la pata
        translate([cuerpo_r - 7, 0, cuerpo_t/2])  // Lleva al borde
            rotate([0, 0, -90])    // Orienta tangencialmente
                soporte_servo_cadera();
}
```

En `cad/cuerpo_cuadruepdo.scad`, también se usa `for` para los agujeros de los pilares:

```openscad
// Archivo: cad/cuerpo_cuadruepdo.scad — líneas 54-58

for (a = [0, 90, 180, 270]) {
    rotate([0, 0, a])
        translate([spacer_r, 0, 0])
            cylinder(r=1.6, h=cuerpo_t+2, center=true);
}
```

Y en la placa superior, un `for` anidado crea los 4 agujeros pasacables:

```openscad
// Archivo: cad/cuerpo_cuadruepdo.scad — líneas 149-154

for (x = [-40, 40]) {
    for (y = [-39, 39]) {
        translate([x, y, 0])
            cylinder(r=7.0, h=30, center=true);
    }
}
```

---

## Capítulo 7: Operaciones Avanzadas — `hull()`, `minkowski()` y `linear_extrude()`

### `hull()` — Envolvente convexa

`hull()` crea el volumen convexo mínimo que engloba todos sus hijos. Es ideal para crear formas orgánicas y de transición suave:

```openscad
// Crea un cuerpo alargado y aerodinámico
hull() {
    sphere(r = 10);
    translate([30, 0, 0])
        sphere(r = 8);
}
```

### `linear_extrude()` — Extrusión de 2D a 3D

Toma un perfil 2D y lo extruye verticalmente:

```openscad
linear_extrude(height = 10) {
    circle(r = 5);     // Círculo 2D → cilindro
}

linear_extrude(height = 10) {
    square([20, 10]);  // Cuadrado 2D → cuboide
}

// Con twist (torsión)
linear_extrude(height = 20, twist = 90) {
    square([10, 10]);
}
```

### `polygon()` — Perfiles 2D arbitrarios

```openscad
// Triángulo
polygon(points = [[0, 0], [10, 0], [5, 10]]);

// Se usa con linear_extrude para crear cuñas, gussets, etc.
linear_extrude(height = 3) {
    polygon(points = [[0, 0], [20, 0], [0, 10]]);
}
```

### `rotate_extrude()` — Revolución

Gira un perfil 2D alrededor del eje Z para crear formas de revolución:

```openscad
rotate_extrude(angle = 360, convexity = 10) {
    translate([20, 0, 0])
        circle(r = 5);
}
// Resultado: una dona (toroide)
```

### 🕷️ Caso Real: El fémur con `hull()`

El módulo `eslabon_completo()` en `cad/eslabon_pata_cuadrupedo.scad` usa `hull()` para conectar orgánicamente la junta de la cadera con el bloque del servo de rodilla:

```openscad
// Archivo: cad/eslabon_pata_cuadrupedo.scad — líneas 20-28

union() {
    // Brazo conector: hull() crea la transición suave
    hull() {
        // Junta de cadera (cilindro que se acopla al horn del servo)
        cylinder(r = 9, h = 6, center=true);

        // Transición hacia el bloque del servo de rodilla
        translate([link_len/2, -3, 1])
            cube([12, 12, 8], center=true);
    }

    // Bloque que aloja el servo de rodilla
    translate([link_len - 12, -8, 0])
        cube([30, 28, link_t], center=true);
}
```

**Visualiza:** `hull()` envuelve un cilindro y un cubo separados, creando un brazo de fémur sólido y aerodinámico sin necesidad de modelar manualmente la transición.

También se usa `polygon()` con `linear_extrude()` para los gussets (refuerzos triangulares) del soporte del sonar:

```openscad
// Archivo: cad/cuerpo_cuadruepdo.scad — líneas 118-127

// Gusset triangular de refuerzo
translate([-22.25, cuerpo_r - 5.0, 5.5]) {
    rotate([0, -90, 0])          // Rotar para que quede vertical
        linear_extrude(height = 2.0)
            polygon(points = [[0, 0], [11, 0], [0, 5]]);
}
```

---

## Capítulo 8: Archivos Múltiples — `use` e `include`

Para proyectos reales, divides el modelo en varios archivos y los combinas.

### `use <archivo.scad>`

Importa **solo los módulos** del archivo. El código de nivel superior (como las llamadas a módulos fuera de `module`) **no se ejecuta**:

```openscad
// main.scad
use <tornillo.scad>

tornillo(20);  // Funciona — el módulo está disponible
```

### `include <archivo.scad>`

Importa **todo** el contenido: módulos **y** código de nivel superior. Es menos usado porque puede ejecutar código no deseado:

```openscad
// main.scad
include <tornillo.scad>
// Todo el código de tornillo.scad se ejecuta aquí también
```

### Organización de proyectos

```
robot/
├── cuerpo.scad         // Chasis y soportes
├── femur.scad          // Eslabón de pata
├── tibia.scad          // Pierna inferior
└── ensamble.scad       // Ensamble completo (solo use)
```

### 🕷️ Caso Real: El ensamble del SpiderBot

`cad/ensamble_cuadruepodo.scad` importa los 3 archivos de componentes con `use`:

```openscad
// Archivo: cad/ensamble_cuadruepodo.scad — líneas 5-7

use <cuerpo_cuadruepdo.scad>     // Módulos: soporte_servo_cadera(),
                                 //          placa_base_cuadruepodo(),
                                 //          placa_superior()

use <eslabon_pata_cuadrupedo.scad>  // Módulo: eslabon_completo()

use <tibia_pata.scad>               // Módulo: tibia()
```

Gracias a `use`, los módulos están disponibles pero el `placa_base_cuadruepodo()` de la línea 158 de `cuerpo_cuadruepdo.scad` **no se ejecuta** al hacer `use`. Solo se ejecuta cuando el ensamble lo invoca explícitamente.

Además, observa que el ensamble **redefine** variables como `$fn` sin conflictos:

```openscad
// cuerpo_cuadruepdo.scad tiene $fn = 50
// ensamble_cuadruepodo.scad tiene $fn = 20
$fn = 20;  // Prevalece para el render del ensamble (más rápido)
```

También hay archivos "instanciadores" que exportan piezas individuales a STL:

```openscad
// Archivo: cad/placa_base_inferior.scad (3 líneas)
use <cuerpo_cuadruepdo.scad>
placa_base_cuadruepodo();  // Esto SÍ se ejecuta al abrir este archivo
```

---

## Capítulo 9: Renderizado y Exportación a STL

### Preview (F5) vs Render (F6)

| Aspecto | Preview (F5) | Render (F6) |
|---------|-------------|-------------|
| Motor | OpenCSG (GPU) | CGAL (CPU) |
| Velocidad | Instantáneo | Puede tomar minutos |
| Precisión | Aproximada (superficies pueden verse rotas en booleanas complejas) | Exacta (geometría manifold válida) |
| Exportable a STL | No | Sí |

**Flujo típico:** Usa F5 mientras desarrollas (iteración rápida) → F6 antes de exportar (geometría final).

### Exportar a STL (F7)

Con el modelo renderizado (F6):

1. Archivo > Exportar > Exportar como STL
2. O presiona **F7** directamente.
3. Nombra el archivo y listo para laminar.

### CLI de OpenSCAD — Exportación por lotes

Ideal para pipelines automatizados:

```bash
# Exportar una pieza individual
openscad -o placa_base.stl cad/placa_base_inferior.scad

# Con parámetros personalizados desde terminal
openscad -o femur_largo.stl -D "link_len=70" cad/eslabon_pata_cuadrupedo.scad

# Renderizar con calidad específica
openscad -o pieza.stl -D "\$fn=100" archivo.scad
```

### Parámetros de calidad: `$fn`, `$fa`, `$fs`

| Parámetro | Control | Valor por defecto | Recomendado para STL |
|-----------|---------|-------------------|---------------------|
| `$fn` | Número de fragmentos (lados) | (automático) | 50-80 |
| `$fa` | Ángulo mínimo entre fragmentos | 12° | 6°-2° |
| `$fs` | Tamaño mínimo del fragmento | 2mm | 0.5-1mm |

La relación: `$fn` prevalece sobre `$fa` y `$fs` si se define explícitamente.

### 🕷️ Caso Real: Comandos CLI para el SpiderBot

```bash
# Exportar la placa base inferior
openscad -o placa_base_inferior.stl -D "\$fn=60" cad/placa_base_inferior.scad

# Exportar el fémur (eslabón de pata)
openscad -o femur.stl -D "\$fn=50" cad/eslabon_pata_cuadrupedo.scad

# Exportar la tibia
openscad -o tibia.stl -D "\$fn=50" cad/tibia_pata.scad

# Exportar la placa superior
openscad -o placa_superior.stl -D "\$fn=60" cad/placa_base_superior.scad

# Exportar el ensamble completo (para visualización, no para impresión)
openscad -o spiderbot_ensamble.stl -D "\$fn=30" cad/ensamble_cuadruepodo.scad
```

---

## Capítulo 10: Proyecto Final — Replica el USS SpiderBot desde Cero

Este capítulo es un ejercicio guiado. Las soluciones completas están en `cad/`. Intenta construir cada pieza siguiendo las instrucciones y luego compara con los archivos reales.

### Paso 1: El chasis circular

Crea un archivo `mi_spiderbot.scad`.

1. Define `$fn = 50`.
2. Crea las variables: `cuerpo_r = 65.0`, `cuerpo_t = 3.0`, `spacer_r = 55.0`.
3. Crea un módulo `placa_base()` que sea un cilindro de radio `cuerpo_r` y altura `cuerpo_t`.
4. Con `difference()`, agrega 4 agujeros circulares en los ejes (0°, 90°, 180°, 270°) a radio `spacer_r`, con `r=1.6` (tornillo M3).
5. Agrega 4 ranuras tipo velcro de `[4, 15, cuerpo_t+2]` en `(±20, ±10)`.
6. Renderiza con F5: deberías ver un disco circular con agujeros simétricos.

> **Referencia:** `cad/cuerpo_cuadruepdo.scad` — módulo `placa_base_cuadruepodo()`.

### Paso 2: El soporte de servo paramétrico

Crea un módulo `soporte_servo()`.

1. El sólido base debe ser un `cube([36, 28, 15], center=true)` trasladado a Z=7.5.
2. Con `difference()`, agrega la cavidad dual-depth:
   - Inferior: `cube([30.0, 24.2, 4.2], center=true)` en Z=2.9.
   - Superior: `cube([25.0, 24.2, 9.0], center=true)` en Z=9.5.
3. Agrega la ranura para bridas en Y=5.5: `cube([34.5, 3.2, 13.5], center=true)`.
4. Agrega dos agujeros pasantes para tornillos M2 con `rotate([90,0,0]) cylinder(r=1, h=35)` en X=±14.25.
5. Agrega la abertura delantera para la corona del servo: `cylinder(r=6.2, h=15)` rotado 90° en X, trasladado a (5.5, 12.0, 7.5).

> **Referencia:** `cad/cuerpo_cuadruepdo.scad` — módulo `soporte_servo_cadera()`.

### Paso 3: Integrar soportes en el chasis

Dentro de `placa_base()`, agrega un bucle `for (a = [45, 135, 225, 315])` que instancie `soporte_servo()` en la periferia:

```openscad
for (a = [45, 135, 225, 315]) {
    rotate([0, 0, a])
        translate([cuerpo_r - 7, 0, cuerpo_t/2])
            rotate([0, 0, -90])
                soporte_servo();
}
```

Renderiza con F5: ahora ves el chasis con 4 brackets en las diagonales.

> **Referencia:** `cad/cuerpo_cuadruepdo.scad` — líneas 77-82.

### Paso 4: El fémur con hull()

Crea un nuevo archivo `femur.scad`.

1. Define `link_len = 55.0`, `link_h = 25.0`, `link_t = 16.0`.
2. Crea un módulo `femur_completo()`.
3. Dentro de `union()`:
   - Crea un `hull()` que envuelva `cylinder(r=9, h=6, center=true)` y `translate([link_len/2, -3, 1]) cube([12, 12, 8], center=true)`.
   - Agrega el bloque del servo de rodilla: `translate([link_len - 12, -8, 0]) cube([30, 28, link_t], center=true)`.
4. Con `difference()`, agrega:
   - El acople del horn en el origen.
   - El bolsillo dual-depth para el servo de rodilla en `translate([link_len - 5.5, -11.25, 0])`.
   - La abertura del engranaje en `translate([link_len, 0, 0])`.
   - Los alivios triangulares.

> **Referencia:** `cad/eslabon_pata_cuadrupedo.scad`.

### Paso 5: La tibia

Crea `tibia.scad`.

1. Define `tibia_h = 65.0`, `tibia_t = 6.0`.
2. Crea un módulo `tibia_completa()`.
3. Usa tres `hull()` consecutivos para crear la curva:
   - Superior: junta de rodilla a cuerpo medio.
   - Medio: cuerpo medio a cuerpo inferior.
   - Inferior: cuerpo inferior a tobillo.
4. Agrega una `sphere(r=5.5)` al final para el pie antideslizante.
5. Con `difference()`, agrega el acople del horn y los alivios triangulares.

> **Referencia:** `cad/tibia_pata.scad`.

### Paso 6: Ensamblar todo

Crea `ensamble_final.scad`.

1. Usa `use` para importar tus 3 archivos.
2. Crea un `dummy_servo()` simple (un prisma azul).
3. Crea `pata_articulada(angulo_cadera, angulo_rodilla)` que pose el servo, el fémur y la tibia en cadena.
4. Crea `ensamble_completo()` que ponga la placa base, 4 patas en los ángulos 45/135/225/315, y la placa superior.
5. Renderiza con F6. ¡Deberías ver tu SpiderBot!

> **Referencia:** `cad/ensamble_cuadruepodo.scad`.

### Paso 7: Exportar a STL

```bash
openscad -o mi_placa_base.stl -D "\$fn=60" mi_spiderbot.scad
openscad -o mi_femur.stl -D "\$fn=50" femur.scad
openscad -o mi_tibia.stl -D "\$fn=50" tibia.scad
```

---

## Apéndice A: Hoja de Referencia Rápida (Cheat Sheet)

| Comando | Sintaxis | Descripción |
|---------|----------|-------------|
| `cube` | `cube([w, d, h], center=false)` | Cubo o prisma rectangular |
| `sphere` | `sphere(r)` | Esfera |
| `cylinder` | `cylinder(r, h)` / `cylinder(r1, r2, h)` | Cilindro o cono truncado |
| `translate` | `translate([x, y, z])` | Desplazar objeto |
| `rotate` | `rotate([x, y, z])` | Rotar objeto (grados) |
| `scale` | `scale([x, y, z])` | Escalar objeto |
| `union` | `union() { ... }` | Fusionar sólidos |
| `difference` | `difference() { A; B; }` | Restar B de A |
| `intersection` | `intersection() { ... }` | Intersección de sólidos |
| `hull` | `hull() { ... }` | Envolvente convexa |
| `minkowski` | `minkowski() { ... }` | Suma de Minkowski (redondeo) |
| `linear_extrude` | `linear_extrude(h)` | Extruir 2D a 3D |
| `rotate_extrude` | `rotate_extrude()` | Revolución de perfil 2D |
| `polygon` | `polygon(points=[...])` | Polígono 2D |
| `for` | `for (i = [inicio:fin])` | Bucle iterativo |
| `module` | `module nombre(p) { }` | Definir módulo |
| `use` | `use <archivo.scad>` | Importar módulos |
| `include` | `include <archivo.scad>` | Importar todo |
| `$fn` | `$fn = N;` | Resolución de curvas |
| `echo` | `echo(valor)` | Imprimir en consola |

---

## Apéndice B: Recursos y Documentación Oficial

- **Documentación oficial de OpenSCAD:** [https://openscad.org/documentation.html](https://openscad.org/documentation.html)
- **Cheat Sheet oficial:** [https://openscad.org/cheatsheet/](https://openscad.org/cheatsheet/)
- **Manual de usuario:** [https://en.wikibooks.org/wiki/OpenSCAD_User_Manual](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual)
- **Reddit:** [r/openscad](https://reddit.com/r/openscad)
- **GitHub:** [https://github.com/openscad/openscad](https://github.com/openscad/openscad)
- **Librería MCAD (componentes mecánicos):** [https://github.com/openscad/MCAD](https://github.com/openscad/MCAD)
- **dotSCAD (utilidades avanzadas):** [https://github.com/JustinSDK/dotSCAD](https://github.com/JustinSDK/dotSCAD)
- **Repositorio del USS SpiderBot:** [https://github.com/anomalyco/USS-SPIDERBOT](https://github.com/anomalyco/USS-SPIDERBOT) (todos los archivos `.scad` en `cad/`)

---

> *Guía generada para el proyecto USS SpiderBot — Taller de Programación I, Universidad San Sebastián. 2026.*
> *Los archivos de referencia están en `cad/` del repositorio.*
