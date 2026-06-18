// Eslabón de Pata (Fémur) para USS SpiderBot
// Diseñado para albergar el servo de rodilla (Knee Pitch) horizontalmente
// Taller de Programación I - Solemne 3

$fn = 30;

link_len = 55.0; // Longitud entre la cadera y la rodilla
link_h = 25.0;   // Altura en el extremo de la rodilla para sostener el servo
link_t = 16.0;   // Grosor del bloque del servo rodilla (brinda soporte lateral)

// Dimensiones del servo SG90
servo_w = 23.0;
servo_t = 12.5;
servo_h = 22.5;
ear_dist = 28.5;

module eslabon_completo() {
    difference() {
        // Estructura principal del fémur
        union() {
            // Brazo conector desde la cadera
            hull() {
                // Junta de cadera (acople al horn del servo cadera)
                cylinder(r = 9, h = 6, center=true);
                // Transición al bloque del servo
                translate([link_len/2, -3, 0])
                    cube([12, 12, 8], center=true);
            }
            // Bloque que aloja el servo de rodilla (al final del fémur)
            translate([link_len - 12, -4, 0])
                cube([30, 26, link_t], center=true);
        }
        
        // 1. Acople para el horn del servo Cadera (Hip Pitch) en el origen (X=0, Z = +1.8)
        // Desplazado para que el bolsillo de profundidad 2.5mm corte limpiamente la cara exterior (Z=3.0) sin dejar paredes fantasma
        translate([0, 0, 1.8]) {
            cylinder(r=6.2, h=2.6, center=true);
            cylinder(r=1.2, h=10, center=true);
        }
        
        // 2. Bolsillo (pocket) para el servo de Rodilla (Knee Pitch)
        // Se coloca de forma que el eje del servo coincida exactamente con X = link_len (55)
        // Tolerancia de 0.3mm total (0.15mm por lado) para un calce a presión firme y sin oscilaciones
        translate([link_len - 5.5, -11.25, 0]) {
            // Bolsillo del cuerpo del servo
            cube([23.3, 22.8, 12.8], center=true);
            
            // Ranura para orejas/bridas (paralela a XZ, en Y = 5.5)
            translate([0, 5.5, 0])
                cube([33.0, 2.8, 13.5], center=true);
                
            // Agujeros para tornillos de orejas (paso estandar de 28.5mm)
            translate([-14.25, 0, 0])
                rotate([90, 0, 0])
                    cylinder(r=1.0, h=30, center=true);
            translate([14.25, 0, 0])
                rotate([90, 0, 0])
                    cylinder(r=1.0, h=30, center=true);
        }
        
        // 3. Abertura delantera (Y+) para que sobresalga el engranaje del servo de rodilla (en X=55)
        translate([link_len, 0, 0])
            rotate([90, 0, 0])
                cylinder(r=6, h=30, center=true);
                
        // 4. Alivios de peso estéticos triangulares en el brazo
        translate([18, -2, 0])
            rotate([0, 0, 30])
                cylinder(r=3.5, h=10, $fn=3, center=true);
    }
}

eslabon_completo();
