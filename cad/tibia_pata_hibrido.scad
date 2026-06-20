// Tibia Híbrida (Pie recto simplificado estilo SP-8)
// Adaptada para acoplarse al horn del servo de rodilla (Knee Pitch).
// Cuerpo recto que desciende verticalmente y termina en punta esférica antideslizante.

$fn = 30;

tibia_h = 65.0;
tibia_t = 6.0;

module tibia_hibrida() {
    difference() {
        union() {
            hull() {
                cylinder(r = 9, h = tibia_t, center=true);
                translate([0, -15, 0])
                    cylinder(r = 5, h = tibia_t, center=true);
            }
            hull() {
                translate([0, -15, 0])
                    cylinder(r = 5, h = tibia_t, center=true);
                translate([0, -40, 0])
                    cylinder(r = 4.5, h = tibia_t, center=true);
            }
            hull() {
                translate([0, -40, 0])
                    cylinder(r = 4.5, h = tibia_t, center=true);
                translate([0, -tibia_h, 0])
                    cylinder(r = 5.5, h = tibia_t, center=true);
            }
            translate([0, -tibia_h, 0])
                sphere(r = 5.5);
        }

        // 1. Acople para el horn del servo de Rodilla en (0,0) a Z=1.8
        translate([0, 0, 1.8]) {
            cylinder(r = 4.0, h = 2.6, center=true);
            translate([0, -8.0, 0])
                cube([5.2, 16.0, 2.6], center=true);
            cylinder(r = 1.2, h = 10, center=true);
        }
    }
}

tibia_hibrida();
