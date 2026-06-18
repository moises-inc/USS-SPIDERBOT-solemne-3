// Eslabón de la Oruga para Impresión 3D
// Taller de Programación I - Solemne 3

$fn = 30;

eslabon_w = 15.0; // Ancho del eslabón (mismo ancho de rueda)
eslabon_l = 20.0; // Largo de eslabón
eslabon_t = 2.0;  // Grosor de base
pin_r = 1.0;      // Radio del pasador de unión

module eslabon() {
    difference() {
        union() {
            // Base del eslabón
            cube([eslabon_l, eslabon_w, eslabon_t], center=true);
            
            // Diente de tracción central (encastra en la rueda)
            translate([0, 0, eslabon_t/2 + 2])
                cube([6, 6, 4], center=true);
                
            // Bisagra lado A (hembra)
            translate([-eslabon_l/2, -eslabon_w/2 + 2.5, 0])
                rotate([90, 0, 0]) cylinder(r = 3, h = 5, center=true);
            translate([-eslabon_l/2, eslabon_w/2 - 2.5, 0])
                rotate([90, 0, 0]) cylinder(r = 3, h = 5, center=true);
                
            // Bisagra lado B (macho central)
            translate([eslabon_l/2, 0, 0])
                rotate([90, 0, 0]) cylinder(r = 3, h = eslabon_w - 6, center=true);
        }
        
        // Agujero de bisagra lado A (agujero para pasador)
        translate([-eslabon_l/2, 0, 0])
            rotate([90, 0, 0]) cylinder(r = pin_r, h = eslabon_w + 2, center=true);
            
        // Agujero de bisagra lado B
        translate([eslabon_l/2, 0, 0])
            rotate([90, 0, 0]) cylinder(r = pin_r, h = eslabon_w + 2, center=true);
    }
}

eslabon();
