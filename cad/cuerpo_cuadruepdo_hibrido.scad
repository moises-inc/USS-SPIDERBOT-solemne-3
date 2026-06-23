// Cuerpo Central Híbrido (USS SpiderBot + SP-8)
// Placas base/superior con cuna de protoboard 400 ptos, XL6009E1, pasacables y HC-SR04.
// Los brackets de cadera son robustos de 36mm con bolsillos de doble profundidad.

$fn = 50;

cuerpo_r = 65.0;
cuerpo_t = 3.0;
spacer_r = 55.0;

module soporte_servo_cadera() {
    difference() {
        translate([0, 0, 7.5])
            cube([36, 28, 15], center=true);
        translate([0, 0, 2.9])
            cube([30.0, 24.2, 4.2], center=true);
        translate([0, 0, 9.5])
            cube([25.0, 24.2, 9.0], center=true);
        translate([0, 5.5, 7.5])
            cube([34.5, 3.2, 13.5], center=true);
        translate([-14.25, 0, 7.5])
            rotate([90, 0, 0])
                cylinder(r=1.0, h=35, center=true);
        translate([14.25, 0, 7.5])
            rotate([90, 0, 0])
                cylinder(r=1.0, h=35, center=true);
        translate([5.5, 12.0, 7.5])
            rotate([90, 0, 0])
                cylinder(r=6.2, h=15, center=true);
        translate([6.5, 12.0, 7.5])
            cube([23, 5, 16], center=true);
        // 6. Agujero para paso de cables en el piso y pared posterior (local Y = -12, X = 0)
        translate([0, -12, 7.5])
            cylinder(r=5.0, h=16, center=true);
    }
}

module placa_base_cuadruepodo() {
    difference() {
        cylinder(r = cuerpo_r, h = cuerpo_t, center=true);
        for (a = [0, 90, 180, 270]) {
            rotate([0, 0, a])
                translate([spacer_r, 0, 0])
                    cylinder(r=1.6, h=cuerpo_t+2, center=true);
        }
        translate([-20, -10, 0]) cube([4, 15, cuerpo_t + 2], center=true);
        translate([20, -10, 0]) cube([4, 15, cuerpo_t + 2], center=true);
        translate([-20, 10, 0]) cube([4, 15, cuerpo_t + 2], center=true);
        translate([20, 10, 0]) cube([4, 15, cuerpo_t + 2], center=true);
        translate([0, -25, 0]) {
            translate([-28, -10, 0]) cylinder(r=1.5, h=cuerpo_t+2, center=true);
            translate([28, -10, 0]) cylinder(r=1.5, h=cuerpo_t+2, center=true);
            translate([-28, 10, 0]) cylinder(r=1.5, h=cuerpo_t+2, center=true);
            translate([28, 10, 0]) cylinder(r=1.5, h=cuerpo_t+2, center=true);
        }
        // Agujeros para pasar los cables de los servos en la parte trasera de cada bracket (radio 46mm)
        for (a = [45, 135, 225, 315]) {
            rotate([0, 0, a])
                translate([46, 0, 0])
                    cylinder(r=5.0, h=cuerpo_t+2, center=true);
        }
    }
    for (a = [45, 135, 225, 315]) {
        rotate([0, 0, a])
            translate([cuerpo_r - 7, 0, cuerpo_t/2])
                rotate([0, 0, -90])
                    soporte_servo_cadera();
    }
}

module placa_superior() {
    difference() {
        union() {
            cylinder(r = cuerpo_r, h = cuerpo_t, center=true);
            
            // Cuna para Protoboard de 400 puntos en el centro (0,0) (enlarged by 2mm: 86.0mm x 58.0mm)
            translate([0, 0, cuerpo_t/2 + 1.5]) {
                difference() {
                    cube([90.0, 62.0, 3.0], center=true);
                    cube([86.0, 58.0, 3.1], center=true);
                }
            }
            
            // Cuna para Regulador XL6009E1 desplazado al área trasera (X = 0, Y = -42) (enlarged by 2mm: 45.6mm x 23.6mm)
            translate([0, -42, cuerpo_t/2 + 1.5]) {
                difference() {
                    cube([49.6, 27.6, 3.0], center=true);
                    cube([45.6, 23.6, 3.1], center=true);
                }
            }
            
            translate([0, cuerpo_r - 1.25, 11]) {
                cube([47.0, 2.5, 22.0], center=true);
            }
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
        for (a = [0, 90, 180, 270]) {
            rotate([0, 0, a])
                translate([spacer_r, 0, 0])
                    cylinder(r=1.6, h=30, center=true);
        }
        translate([-13, cuerpo_r - 1.25, 11])
            rotate([90, 0, 0])
                cylinder(r=8.25, h=10, center=true);
        translate([13, cuerpo_r - 1.25, 11])
            rotate([90, 0, 0])
                cylinder(r=8.25, h=10, center=true);
        
        // 3. Orificios de paso de cables (wire routing) en las 4 esquinas de la cuna (shifted outward to clear cuna)
        for (x = [-43, 43]) {
            for (y = [-40, 40]) {
                translate([x, y, 0])
                    cylinder(r=7.0, h=30, center=true);
            }
        }
    }
}

placa_base_cuadruepodo();
