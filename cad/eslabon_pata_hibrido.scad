// Eslabón de Pata Híbrido (Horquilla/Fork U-Shape estilo SP-8)
// Adaptado para configuración Pitch-Pitch con servo de rodilla horizontal.
// Dos brazos paralelos: uno abraza el servo, el otro es el punto de pivote secundario.

$fn = 30;

link_len = 55.0;
fork_arm_w = 12.0;
fork_gap = 25.0;
fork_h = 16.0;

module eslabon_hibrido() {
    difference() {
        union() {
            // Brida de acople a cadera (disco circular conector)
            cylinder(r = 9, h = fork_h, center=true);

            // Brazo superior (cuerpo del servo)
            translate([0, fork_gap/2, 0])
                cube([link_len, fork_arm_w, fork_h], center=true);

            // Brazo inferior (pivote secundario)
            translate([0, -fork_gap/2, 0])
                cube([link_len, fork_arm_w, fork_h], center=true);

            // Unión frontal (punta de la U) en X = link_len
            translate([link_len, 0, 0])
                cube([fork_arm_w, fork_gap + fork_arm_w, fork_h], center=true);
        }

        // 1. Acople para el horn del servo Cadera en (X=0, Z=-1.8)
        translate([0, 0, -1.8]) {
            cylinder(r=4.0, h=2.6, center=true);
            translate([8.0, 0, 0])
                cube([16.0, 5.2, 2.6], center=true);
            cylinder(r=1.2, h=10, center=true);
        }

        // 2. Bolsillo dual-depth para el servo de Rodilla en el brazo superior
        // El servo se monta horizontal con el eje en X = link_len
        translate([link_len - 5.5, fork_gap/2, 0]) {
            // Zona inferior para cables (30mm largo)
            translate([0, 0, -5.0])
                cube([30.0, 24.2, 5.0], center=true);
            // Zona superior para fijación con tornillos (25mm largo)
            translate([0, 0, 2.5])
                cube([25.0, 24.2, 10.0], center=true);
            // Ranura orejas/bridas
            translate([0, 5.5, 0])
                cube([34.5, 3.2, 13.5], center=true);
            // Agujeros M2
            translate([-14.25, 0, 0])
                rotate([90, 0, 0])
                    cylinder(r=1.0, h=30, center=true);
            translate([14.25, 0, 0])
                rotate([90, 0, 0])
                    cylinder(r=1.0, h=30, center=true);
        }

        // 3. Orificio pasante coaxial en X=link_len para el back shaft/pin
        translate([link_len, -fork_gap/2, 0])
            rotate([90, 0, 0])
                cylinder(r=3.0, h=30, center=true);

        // 4. Abertura delantera para engranaje del servo de rodilla
        translate([link_len, fork_gap/2, 0])
            rotate([90, 0, 0])
                cylinder(r=6.0, h=15, center=true);
    }
}

eslabon_hibrido();
