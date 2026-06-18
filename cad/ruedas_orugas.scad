// Ruedas: Sprocket (Motriz) e Idler (Loca) para el Robot de Orugas
// Taller de Programación I - Solemne 3

$fn = 60;

// Parámetros de Rueda
rueda_r = 30.0;      // Radio exterior
rueda_w = 15.0;      // Ancho de la rueda
eje_r = 2.0;         // Agujero del eje del motor (eje TT semiplano)
num_dientes = 10;    // Dientes para engranar la oruga

module rueda_sprocket() {
    difference() {
        union() {
            // Cilindro base
            cylinder(r = rueda_r - 2, h = rueda_w, center=true);
            
            // Dientes para la oruga
            for (i = [0:360/num_dientes:360]) {
                rotate([0, 0, i])
                    translate([rueda_r - 2, 0, 0])
                        cylinder(r = 3, h = rueda_w, center=true);
            }
        }
        
        // Agujero para acople de eje chato de motor TT
        intersection() {
            cylinder(r=2.7, h=rueda_w + 2, center=true);
            cube([3.7, 10, rueda_w + 4], center=true);
        }
        
        // Rebajes para aligerar la rueda (agujeros decorativos)
        for (i = [0:60:360]) {
            rotate([0, 0, i])
                translate([15, 0, 0])
                    cylinder(r=5, h=rueda_w + 2, center=true);
        }
    }
}

module rueda_idler() {
    difference() {
        // Cilindro base libre
        cylinder(r = rueda_r - 2, h = rueda_w, center=true);
        
        // Rodamiento central (tornillo M3)
        cylinder(r = 1.6, h = rueda_w + 2, center=true);
        
        // Rebajes para aligerar
        for (i = [0:60:360]) {
            rotate([0, 0, i])
                translate([15, 0, 0])
                    cylinder(r=5, h=rueda_w + 2, center=true);
        }
    }
}

// Visualización (Descomenta una para exportar por separado)
translate([-rueda_r - 10, 0, 0]) rueda_sprocket();
translate([rueda_r + 10, 0, 0]) rueda_idler();
