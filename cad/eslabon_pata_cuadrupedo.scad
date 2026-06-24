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
                // Transición al bloque del servo (alineado a Z=-3 para base plana)
                translate([link_len/2, -3, 1])
                    cube([12, 12, 8], center=true);
            }
            // Bloque que aloja el servo de rodilla (al final del fémur, centrado simétricamente con el bolsillo para mayor grosor de pared)
            translate([link_len - 6.5, -11.25, 0])
                cube([42, 32, link_t], center=true);
        }
        
        // 1. Acople para el horn del servo Cadera (Hip Pitch) en el origen (X=0, Z = -1.8)
        // Tallado en la cara inferior (Z-) que mira hacia el cuerpo del robot
        translate([0, 0, -1.8]) {
            cylinder(r=4.0, h=2.6, center=true);
            translate([8.0, 0, 0])
                cube([16.0, 5.2, 2.6], center=true);
            cylinder(r=1.2, h=10, center=true);
        }
        
        // 2. Bolsillo (pocket) para el servo de Rodilla (Knee Pitch) (dual-depth para cables y soporte de tornillos, abierto hacia atrás Y- para inserción)
        // Se coloca de forma que el eje del servo coincida exactamente con X = link_len (55)
        translate([link_len - 5.5, -11.25, 0]) {
            // Parte inferior ensanchada a 30.0mm para cables (Z = -7.5 a -2.5, extendida en Y- para cortar la cara posterior)
            translate([0, -5.4, -5.0])
                cube([30.0, 35.0, 5.0], center=true);
            // Parte superior estrecha a 25.0mm para soporte roscado (Z = -2.5 to 7.5, extendida en Y- para cortar la cara posterior)
            translate([0, -5.4, 2.5])
                cube([25.0, 35.0, 10.0], center=true);
            
            // Ranura para orejas/bridas (paralela a XZ, extendida en Y- desde el soporte de la oreja hasta atrás)
            translate([0, -5.4, 0])
                cube([34.5, 25.0, 13.5], center=true);
                
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
                cylinder(r=6, h=35, center=true);
                
        // 4. Alivios de peso estéticos triangulares en el brazo
        translate([18, -2, 0])
            rotate([0, 0, 30])
                cylinder(r=3.5, h=10, $fn=3, center=true);
    }
}

eslabon_completo();
