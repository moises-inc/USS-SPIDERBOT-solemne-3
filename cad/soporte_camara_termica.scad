// Soporte de Cámara Térmica AMG8833 para Servo SG90
// USS Taller de Programación I - Solemne 3

$fn = 50; // Resolución de cilindros

// Parámetros Cámara AMG8833
board_w = 20.0;   // Ancho de la placa
board_h = 20.0;   // Alto de la placa
board_t = 1.6;    // Grosor de la placa
hole_dist = 15.0; // Distancia entre centros de agujeros
hole_r = 1.1;     // Radio del agujero del tornillo (M2)

// Parámetros Acople Servo SG90 (Horn circular)
horn_r = 4.0;     // Radio del encastre del servo horn
horn_h = 2.0;     // Profundidad del encastre
shaft_r = 1.5;    // Radio del agujero del eje del servo

module base_placa() {
    difference() {
        // Cuerpo principal
        cube([board_w + 4, board_h + 4, 3], center = true);
        
        // Agujeros de montaje de la placa
        translate([-hole_dist/2, -hole_dist/2, -2])
            cylinder(r = hole_r, h = 6);
        translate([hole_dist/2, -hole_dist/2, -2])
            cylinder(r = hole_r, h = 6);
        translate([-hole_dist/2, hole_dist/2, -2])
            cylinder(r = hole_r, h = 6);
        translate([hole_dist/2, hole_dist/2, -2])
            cylinder(r = hole_r, h = 6);
            
        // Hueco central para soldaduras/componentes traseros de la placa
        cube([board_w - 4, board_h - 4, 4], center = true);
    }
}

module acople_servo() {
    difference() {
        // Cilindro exterior de acople
        cylinder(r = horn_r + 2, h = horn_h + 2);
        // Hueco del horn
        translate([0, 0, 2])
            cylinder(r = horn_r, h = horn_h + 0.1);
        // Agujero para tornillo del eje
        translate([0, 0, -1])
            cylinder(r = shaft_r, h = horn_h + 4);
    }
}

// Ensamblar soporte
union() {
    translate([0, 0, 1.5]) base_placa();
    translate([0, 0, -2.0]) acople_servo();
}
