// Chasis Principal del Robot de Orugas (USS Thermal Rescue Bot)
// Taller de Programación I - Solemne 3

$fn = 40;

// Parámetros del Chasis
chasis_w = 120.0; // Ancho total
chasis_l = 150.0; // Largo total
chasis_t = 3.0;   // Grosor de la base
wall_h = 25.0;    // Altura de paredes laterales

// Parámetros de los Motores TT (DC amarillos)
motor_w = 22.5;   // Ancho del motor
motor_l = 70.0;   // Largo del motor
motor_h = 19.0;   // Altura del motor

module placa_base() {
    difference() {
        // Base plana con esquinas redondeadas
        hull() {
            translate([-chasis_w/2+5, -chasis_l/2+5, 0]) cylinder(r=5, h=chasis_t);
            translate([chasis_w/2-5, -chasis_l/2+5, 0]) cylinder(r=5, h=chasis_t);
            translate([-chasis_w/2+5, chasis_l/2-5, 0]) cylinder(r=5, h=chasis_t);
            translate([chasis_w/2-5, chasis_l/2-5, 0]) cylinder(r=5, h=chasis_t);
        }
        
        // Ranuras de ventilación y reducción de peso
        for (i = [-30:15:30]) {
            translate([i, 0, -1])
                cube([8, chasis_l - 40, chasis_t + 2], center=true);
        }
    }
}

module soportes_motores() {
    // Soportes traseros para motores DC TT
    translate([-chasis_w/2 + 2, -chasis_l/2 + 10, chasis_t]) {
        difference() {
            cube([15, motor_w + 6, motor_h + 4]);
            // Espacio interior del motor
            translate([2, 3, 2]) cube([14, motor_w, motor_h + 5]);
            // Eje de salida
            translate([-5, (motor_w+6)/2, motor_h/2 + 2]) rotate([0, 90, 0]) cylinder(r=4, h=25);
        }
    }
    
    translate([chasis_w/2 - 17, -chasis_l/2 + 10, chasis_t]) {
        difference() {
            cube([15, motor_w + 6, motor_h + 4]);
            // Espacio interior del motor
            translate([-1, 3, 2]) cube([14, motor_w, motor_h + 5]);
            // Eje de salida
            translate([-5, (motor_w+6)/2, motor_h/2 + 2]) rotate([0, 90, 0]) cylinder(r=4, h=25);
        }
    }
}

// Ensamblado
placa_base();
soportes_motores();
