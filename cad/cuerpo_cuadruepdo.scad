// Cuerpo Central del Cuadrúpedo (USS SpiderBot)
// Diseño de Doble Deck (Placa Superior e Inferior) en Configuración Pitch-Pitch
// Taller de Programación I - Solemne 3

$fn = 50;

cuerpo_r = 65.0;    // Radio del chasis circular
cuerpo_t = 3.0;     // Grosor de las placas
spacer_r = 55.0;    // Radio para pilares espaciadores

module soporte_servo_cadera() {
    difference() {
        // Bloque estructural principal
        translate([0, 0, 7.5])
            cube([36, 26, 15], center=true);
        
        // 1. Cavidad ensanchada para el cuerpo del servo SG90
        // Holgura ajustada para impresión FDM (tolerancia ~0.9mm de largo y ~0.9mm de ancho/alto)
        translate([0, 0, 7.5])
            cube([24.2, 23.2, 13.4], center=true);
            
        // 2. Ranura ensanchada para las orejas/bridas del servo (Y = 5.5)
        translate([0, 5.5, 7.5])
            cube([34.0, 3.2, 13.5], center=true);
            
        // 3. Agujeros para los tornillos M2 (pasantes en Y)
        translate([-14.25, 0, 7.5])
            rotate([90, 0, 0])
                cylinder(r=1.0, h=30, center=true);
        translate([14.25, 0, 7.5])
            rotate([90, 0, 0])
                cylinder(r=1.0, h=30, center=true);
                  
        // 4. Abertura delantera (Y+) para corona de salida del servo
        translate([5.5, 11, 7.5])
            rotate([90, 0, 0])
                cylinder(r=6.2, h=10, center=true);
                
        // 5. Rebaje frontal-derecho para rotación libre del fémur
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
        // ── ESTRUCTURA SÓLIDA (UNION) ─────────────────────────────────
        union() {
            // Placa superior circular principal
            cylinder(r = cuerpo_r, h = cuerpo_t, center=true);
            
            // Cuna para ESP32 DevKit V1 (38 pines) en el centro (0,0)
            // Dimensiones internas: 52.5mm x 29.0mm. Altura: 3.0mm. Paredes: 2.0mm.
            translate([0, 0, cuerpo_t/2 + 1.5]) {
                difference() {
                    cube([56.5, 33.0, 3.0], center=true);
                    cube([52.5, 29.0, 3.1], center=true);
                }
            }
            
            // Cuna para MPU6050 (GY-521) en X = -36, Y = 0
            // Dimensiones internas: 21.8mm x 17.0mm. Altura: 3.0mm. Paredes: 2.0mm.
            translate([-36, 0, cuerpo_t/2 + 1.5]) {
                difference() {
                    cube([25.8, 21.0, 3.0], center=true);
                    cube([21.8, 17.0, 3.1], center=true);
                }
            }
            
            // Cuna para Regulador XL6009E1 en X = 36, Y = 0
            // Dimensiones internas: 43.6mm x 21.6mm. Altura: 3.0mm. Paredes: 2.0mm.
            translate([36, 0, cuerpo_t/2 + 1.5]) {
                difference() {
                    cube([47.6, 25.6, 3.0], center=true);
                    cube([43.6, 21.6, 3.1], center=true);
                }
            }
            
            // Soporte integrado vertical frontal para Sonar HC-SR04
            // Colocado en el borde frontal (Y = cuerpo_r - 1.25)
            // Dimensiones: 47mm de ancho, 2.5mm de espesor, 22mm de altura.
            translate([0, cuerpo_r - 1.25, 11]) {
                cube([47.0, 2.5, 22.0], center=true);
            }
            
            // Gussets/Refuerzos triangulares de soporte lateral (en X = +/- 22.25)
            translate([-22.25, cuerpo_r - 5.0, 5.5]) {
                rotate([0, -90, 0])
                    linear_extrude(height = 2.0)
                        polygon(points = [[0, 0], [11, 0], [0, 5]]);
            }
            translate([24.25, cuerpo_r - 5.0, 5.5]) {
                rotate([0, -90, 0])
                    linear_extrude(height = 2.0)
                        polygon(points = [[0, 0], [11, 0], [0, 5]]);
            }
        }
        
        // ── AGUJEROS Y CORTES (DIFFERENCE) ───────────────────────────
        
        // 1. Agujeros para pilares espaciadores M3
        for (a = [0, 90, 180, 270]) {
            rotate([0, 0, a])
                translate([spacer_r, 0, 0])
                    cylinder(r=1.6, h=30, center=true);
        }
        
        // 2. Agujeros de montaje para la ESP32 (48.5mm x 25.5mm)
        translate([0, 0, 0]) {
            translate([-12.75, -24.25, 0]) cylinder(r=1.5, h=30, center=true);
            translate([12.75, -24.25, 0]) cylinder(r=1.5, h=30, center=true);
            translate([-12.75, 24.25, 0]) cylinder(r=1.5, h=30, center=true);
            translate([12.75, 24.25, 0]) cylinder(r=1.5, h=30, center=true);
        }
        
        // 3. Agujeros de montaje para MPU6050 (GY-521) - un agujero en X = -36, Y = 7.5
        translate([-36, 7.5, 0])
            cylinder(r=1.5, h=30, center=true);
            
        // 4. Orificios para los transductores ("ojos") del HC-SR04 (16.5mm diámetro, espaciados 26mm)
        translate([-13, cuerpo_r - 1.25, 11])
            rotate([90, 0, 0])
                cylinder(r=8.25, h=10, center=true);
        translate([13, cuerpo_r - 1.25, 11])
            rotate([90, 0, 0])
                cylinder(r=8.25, h=10, center=true);
                
        // 5. Alivios estéticos triangulares traseros (Truss design)
        // Reducidos a dos orientados a 210 y 330 grados para no tocar las cunas laterales
        for (a = [210, 330]) {
            rotate([0, 0, a]) {
                translate([32, 0, 0])
                    rotate([0, 0, 30])
                        cylinder(r=10, h=30, $fn=3, center=true);
            }
        }
    }
}

placa_base_cuadruepodo();
