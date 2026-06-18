// Ensamble Visual Completo del USS SpiderBot en OpenSCAD
// Configuración Rígida Pitch-Pitch (2 Ejes de Rotación Horizontal)
// Taller de Programación I - Solemne 3

use <cuerpo_cuadruepdo.scad>
use <eslabon_pata_cuadrupedo.scad>
use <tibia_pata.scad>

$fn = 20;

deck_spacing = 22.0;

module dummy_servo() {
    // Renderizado simplificado de un servomotor SG90
    color("RoyalBlue") {
        cube([12.5, 23.0, 22.5], center=true);
        translate([0, 0, 5.5])
            cube([12.5, 32.5, 2.5], center=true);
        translate([0, 5.5, 12])
            cylinder(r=2.5, h=4, center=true);
    }
    color("White") {
        translate([0, 5.5, 14])
            cylinder(r=6, h=1.5, center=true);
    }
}

module pilar_espaciador() {
    color("Silver")
        cylinder(r=3.5, h=deck_spacing - 3, center=true);
}

module pata_articulada(angulo_cadera=0, angulo_rodilla=0) {
    // 1. Servo de cadera (Hip Pitch) - Montado horizontalmente en el soporte perimetral
    // Rotado [90, 180, 90] para meterse en la cavidad y orientar el eje a Y+ (X=5.5, Y=14.0, Z=7.5)
    translate([0, 0, 7.5])
        rotate([90, 180, 90])
            dummy_servo();
            
    // 2. Eslabón Fémur - Gira verticalmente (angulo_cadera) acoplado al eje del servo cadera
    // El eje real de la corona de salida está en X=5.5, Y=14.0, Z=7.5
    translate([5.5, 14.0, 7.5]) {
        rotate([0, angulo_cadera, 0]) {
            // Rotación correctiva del fémur de 90 en X para que apunte hacia abajo (en XZ)
            // y la tibia apunte al suelo (Z-)
            rotate([90, 0, 0]) {
                color("DarkSlateGray")
                    eslabon_completo(); // El origen del fémur está en su eje de giro
                    
                // 3. Servo de rodilla (Knee Pitch) - Montado horizontalmente dentro del fémur
                // Orientado y alineado con el eje físico de rotación en X = 55 (rodilla), Y = 2.75, Z = 0
                translate([55 - 5.5, -11.25, 0])
                    rotate([90, 180, 90])
                        dummy_servo();
                        
                // 4. Tibia - Gira verticalmente (angulo_rodilla) acoplada al horn del servo de rodilla
                translate([55, 2.75, 0]) {
                    rotate([0, angulo_rodilla, 0]) {
                        rotate([90, 0, 0]) { // Alinear la tibia verticalmente hacia abajo
                            color("Black")
                                tibia();
                        }
                    }
                }
            }
        }
    }
}

module ensamble_completo() {
    // 1. Placa Base Inferior con soportes de servo integrados
    color("Black") placa_base_cuadruepodo();
    
    // 2. Pilares espaciadores
    for (a = [0, 90, 180, 270]) {
        rotate([0, 0, a])
            translate([55, 0, deck_spacing/2])
                pilar_espaciador();
    }
    
    // 3. Placa Superior
    color("Black")
        translate([0, 0, deck_spacing])
            placa_superior();
            
    // 4. ESP32 DevKit V1
    color("Silver")
        translate([0, 0, deck_spacing + 3])
            cube([25.5, 48.5, 4], center=true);
            
    // 5. Las 4 Patas montadas en los soportes perimetrales (a 45, 135, 225, 315 grados)
    for (a = [45, 135, 225, 315]) {
        rotate([0, 0, a])
            translate([65 - 6, 0, 1.5]) // Radio del chasis cuerpo_r = 65, centrado en el soporte de servo
                rotate([0, 0, -90])     // Rotar para alinear con el bracket perimetral (eje hacia afuera)
                    pata_articulada(15, -45); // Pose de pie
    }
}

ensamble_completo();