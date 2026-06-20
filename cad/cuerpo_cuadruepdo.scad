// Cuerpo Central del Cuadrúpedo (USS SpiderBot)
// Diseño de Doble Deck (Placa Superior e Inferior) en Configuración Pitch-Pitch
// Taller de Programación I - Solemne 3

$fn = 50;

cuerpo_r = 65.0;    // Radio del chasis circular
cuerpo_t = 3.0;     // Grosor de las placas
spacer_r = 55.0;    // Radio para pilares espaciadores

module soporte_servo_cadera() {
    difference() {
        // Bloque estructural principal (ensanchado a 28mm)
        translate([0, 0, 7.5])
            cube([36, 28, 15], center=true);
        
        // 1. Cavidad ensanchada para el cuerpo del servo SG90
        // Holgura ajustada para impresión FDM (tolerancia ~2.2mm de largo y ~1.4mm de alto)
        translate([0, 0, 7.5])
            cube([25.0, 24.2, 13.4], center=true);
            
        // 2. Ranura ensanchada para las orejas/bridas del servo (Y = 5.5)
        translate([0, 5.5, 7.5])
            cube([34.5, 3.2, 13.5], center=true);
            
        // 3. Agujeros para los tornillos M2 (pasantes en Y)
        translate([-14.25, 0, 7.5])
            rotate([90, 0, 0])
                cylinder(r=1.0, h=35, center=true);
        translate([14.25, 0, 7.5])
            rotate([90, 0, 0])
                cylinder(r=1.0, h=35, center=true);
                  
        // 4. Abertura delantera (Y+) para corona de salida del servo (trasladada a Y=12.0)
        translate([5.5, 12.0, 7.5])
            rotate([90, 0, 0])
                cylinder(r=6.2, h=15, center=true);
                
        // 5. Rebaje frontal-derecho para rotación libre del fémur (trasladado a Y=12.0)
        translate([6.5, 12.0, 7.5])
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
    // Traslación corregida a cuerpo_r - 7 para compensar el ensanchamiento a 28mm
    for (a = [45, 135, 225, 315]) {
        rotate([0, 0, a])
            translate([cuerpo_r - 7, 0, cuerpo_t/2])
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
            
            // Cuna para Protoboard de 400 puntos en el centro (0,0)
            // Dimensiones internas: 84.0mm x 56.0mm. Altura: 3.0mm. Paredes: 2.0mm.
            translate([0, 0, cuerpo_t/2 + 1.5]) {
                difference() {
                    cube([88.0, 60.0, 3.0], center=true);
                    cube([84.0, 56.0, 3.1], center=true);
                }
            }
            
            // Cuna para Regulador XL6009E1 desplazado al área trasera (X = 0, Y = -42)
            // Dimensiones internas: 43.6mm x 21.6mm. Altura: 3.0mm. Paredes: 2.0mm.
            translate([0, -42, cuerpo_t/2 + 1.5]) {
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
        
        // 2. Orificios para los transductores ("ojos") del HC-SR04 (16.5mm diámetro, espaciados 26mm)
        translate([-13, cuerpo_r - 1.25, 11])
            rotate([90, 0, 0])
                cylinder(r=8.25, h=10, center=true);
        translate([13, cuerpo_r - 1.25, 11])
            rotate([90, 0, 0])
                cylinder(r=8.25, h=10, center=true);
                
        // 3. Orificios de paso de cables (wire routing) en las 4 esquinas de la protoboard (r=7.0)
        // Permite pasar los cables Dupont desde los servos y PCA9685 al deck superior
        for (x = [-40, 40]) {
            for (y = [-39, 39]) {
                translate([x, y, 0])
                    cylinder(r=7.0, h=30, center=true);
            }
        }
    }
}

placa_base_cuadruepodo();
