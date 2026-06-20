// Tibia (Lower Leg) para USS SpiderBot
// Diseñado para acoplarse directamente al horn del servo de rodilla (Knee Pitch)
// Taller de Programación I - Solemne 3

$fn = 30;

tibia_h = 65.0;    // Altura vertical de la tibia
tibia_t = 6.0;     // Grosor de la pieza

module tibia() {
    difference() {
        // Estructura curvada principal
        union() {
            hull() {
                // Junta superior de la rodilla (acople al horn del servo)
                cylinder(r = 9, h = tibia_t, center=true);
                // Cuerpo medio superior
                translate([4, -15, 0])
                    cylinder(r = 5, h = tibia_t, center=true);
            }
            hull() {
                // Cuerpo medio superior
                translate([4, -15, 0])
                    cylinder(r = 5, h = tibia_t, center=true);
                // Cuerpo medio inferior
                translate([10, -35, 0])
                    cylinder(r = 4.5, h = tibia_t, center=true);
            }
            hull() {
                // Cuerpo medio inferior
                translate([10, -35, 0])
                    cylinder(r = 4.5, h = tibia_t, center=true);
                // Tobillo/Pie
                translate([12, -tibia_h, 0])
                    cylinder(r = 5.5, h = tibia_t, center=true);
            }
            // Pie de bola antideslizante
            translate([12, -tibia_h, 0])
                sphere(r=5.5);
        }
        
        // 1. Acople para el horn del servo de Rodilla (Knee Pitch) en el origen (0,0)
        translate([0, 0, 1.8]) {
            cylinder(r = 4.0, h = 2.6, center=true);
            translate([0, -8.0, 0])
                cube([5.2, 16.0, 2.6], center=true);
            cylinder(r = 1.2, h = 10, center=true);
        }
        
        // 2. Alivios de peso triangulares estéticos (Truss style)
        // Triángulo 1
        translate([3, -18, 0])
            rotate([0, 0, 45])
                cylinder(r = 3, h = tibia_t + 2, $fn=3, center=true);
                
        // Triángulo 2
        translate([7, -38, 0])
            rotate([0, 0, -45])
                cylinder(r = 3, h = tibia_t + 2, $fn=3, center=true);
    }
}

tibia();
