// Cuerpo Central del Cuadrúpedo (USS SpiderBot)
// Diseño de Doble Deck (Placa Superior e Inferior) en Configuración Pitch-Pitch
// Taller de Programación I - Solemne 3

$fn = 50;

cuerpo_r = 65.0;    // Radio del chasis circular
cuerpo_t = 3.0;     // Grosor de las placas
spacer_r = 55.0;    // Radio para pilares espaciadores

module soporte_servo_cadera() {
    // Soporte perimetral integrado para el servo horizontal de cadera (Hip Pitch)
    // Dimensionado para ajuste exacto sin juego mecánico
    difference() {
        // Bloque estructural principal (Y=26mm para cubrir la altura del servo)
        translate([0, 0, 7.5])
            cube([36, 26, 15], center=true);
        
        // 1. Cavidad ajustada para el cuerpo del servo SG90
        // Tolerancia de 0.3mm total (0.15mm por lado) para ajuste a presión (snug fit)
        translate([0, 0, 7.5])
            cube([23.3, 22.8, 12.8], center=true);
            
        // 2. Ranura para las orejas/bridas del servo (paralela a XZ, en Y = 5.5)
        translate([0, 5.5, 7.5])
            cube([33.0, 2.8, 13.5], center=true);
            
        // 3. Agujeros para los tornillos M2 de fijación (pasantes en Y)
        translate([-14.25, 0, 7.5])
            rotate([90, 0, 0])
                cylinder(r=1.0, h=30, center=true);
        translate([14.25, 0, 7.5])
            rotate([90, 0, 0])
                cylinder(r=1.0, h=30, center=true);
                 
        // 4. Abertura delantera (Y+) para que sobresalga la corona de salida del servo
        // Desplazada a X=5.5 para alinearse con el eje real del servo SG90
        translate([5.5, 11, 7.5])
            rotate([90, 0, 0])
                cylinder(r=6.2, h=10, center=true);
                
        // 5. Rebaje frontal-derecho para evitar la sobreposición/colisión con el fémur al rotar
        // El corte va desde X=-5 hasta X=18 y reduce la pared frontal a Y=8.5 (dejando 1.6mm de pared en el slot)
        translate([6.5, 11, 7.5])
            cube([23, 5, 16], center=true);
    }
}

module placa_base_cuadruepodo() {
    difference() {
        // Placa inferior sólida
        cylinder(r = cuerpo_r, h = cuerpo_t, center=true);
        
        // Agujeros para los 4 pilares espaciadores M3
        for (a = [0, 90, 180, 270]) {
            rotate([0, 0, a])
                translate([spacer_r, 0, 0])
                    cylinder(r=1.6, h=cuerpo_t+2, center=true);
        }
        
        // Ranuras para amarras de velcro para la batería Li-ion 2S
        translate([-20, -10, 0]) cube([4, 15, cuerpo_t + 2], center=true);
        translate([20, -10, 0]) cube([4, 15, cuerpo_t + 2], center=true);
        translate([-20, 10, 0]) cube([4, 15, cuerpo_t + 2], center=true);
        translate([20, 10, 0]) cube([4, 15, cuerpo_t + 2], center=true);
        
        // Agujeros de montaje para el driver PCA9685 (56mm x 20mm)
        translate([0, -25, 0]) {
            translate([-28, -10, 0]) cylinder(r=1.5, h=cuerpo_t+2, center=true);
            translate([28, -10, 0]) cylinder(r=1.5, h=cuerpo_t+2, center=true);
            translate([-28, 10, 0]) cylinder(r=1.5, h=cuerpo_t+2, center=true);
            translate([28, 10, 0]) cylinder(r=1.5, h=cuerpo_t+2, center=true);
        }
    }
    
    // Añadir los 4 soportes de servo de cadera en la periferia (orientados tangencialmente, eje hacia afuera)
    for (a = [45, 135, 225, 315]) {
        rotate([0, 0, a])
            translate([cuerpo_r - 6, 0, cuerpo_t/2])
                rotate([0, 0, -90])
                    soporte_servo_cadera();
    }
}

module placa_superior() {
    difference() {
        cylinder(r = cuerpo_r, h = cuerpo_t, center=true);
        
        // Agujeros para pilares espaciadores M3
        for (a = [0, 90, 180, 270]) {
            rotate([0, 0, a])
                translate([spacer_r, 0, 0])
                    cylinder(r=1.6, h=cuerpo_t+2, center=true);
        }
        
        // Agujeros para ESP32 DevKit V1 (48.5mm x 25.5mm)
        translate([0, 0, 0]) {
            translate([-12.75, -24.25, 0]) cylinder(r=1.5, h=cuerpo_t+2, center=true);
            translate([12.75, -24.25, 0]) cylinder(r=1.5, h=cuerpo_t+2, center=true);
            translate([-12.75, 24.25, 0]) cylinder(r=1.5, h=cuerpo_t+2, center=true);
            translate([12.75, 24.25, 0]) cylinder(r=1.5, h=cuerpo_t+2, center=true);
        }
        
        // Alivios estéticos triangulares (Truss design)
        for (a = [30, 150, 270]) {
            rotate([0, 0, a]) {
                translate([25, 13, 0])
                    rotate([0, 0, 30])
                        cylinder(r=8, h=cuerpo_t+2, $fn=3, center=true);
                translate([25, -13, 0])
                    rotate([0, 0, -30])
                        cylinder(r=8, h=cuerpo_t+2, $fn=3, center=true);
            }
        }
    }
}

placa_base_cuadruepodo();
