// Ensamble Visual Híbrido (USS SpiderBot + Patas SP-8)
// Configuración Pitch-Pitch con horquillas estilo SP-8.

use <cuerpo_cuadruepdo_hibrido.scad>
use <eslabon_pata_hibrido.scad>
use <tibia_pata_hibrido.scad>

$fn = 20;

cuerpo_r = 65.0;
deck_spacing = 22.0;

module dummy_servo() {
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

module pata_hibrida_articulada(angulo_cadera=0, angulo_rodilla=0) {
    translate([0, 0, 7.5])
        rotate([90, 180, 90])
            dummy_servo();

    translate([5.5, 14.0, 7.5]) {
        rotate([0, angulo_cadera, 0]) {
            rotate([90, 0, 0]) {
                color("DarkSlateGray")
                    eslabon_hibrido();

                translate([55, 0, 0])
                    rotate([90, 180, 90])
                        dummy_servo();

                translate([55, 0, 0]) {
                    rotate([0, angulo_rodilla, 0]) {
                        rotate([90, 0, 0]) {
                            color("Black")
                                tibia_hibrida();
                        }
                    }
                }
            }
        }
    }
}

module ensamble_completo_hibrido() {
    color("Black") placa_base_cuadruepodo();

    for (a = [0, 90, 180, 270]) {
        rotate([0, 0, a])
            translate([55, 0, deck_spacing/2])
                pilar_espaciador();
    }

    color("Black")
        translate([0, 0, deck_spacing])
            placa_superior();

    color("LightGray")
        translate([0, 0, deck_spacing + 6.0])
            cube([84.0, 56.0, 9.0], center=true);

    color("Silver")
        translate([0, 0, deck_spacing + 10.5 + 2.0])
            cube([28.0, 51.5, 4], center=true);

    color("DarkBlue")
        translate([-20, 10, deck_spacing + 10.5 + 1.5])
            cube([21.2, 16.4, 3], center=true);

    color("Navy")
        translate([0, -42, deck_spacing + 5.5])
            cube([43.0, 21.0, 8], center=true);

    color("CadetBlue")
        translate([0, cuerpo_r - 2.5, deck_spacing + 11])
            rotate([90, 0, 0])
                cube([45.0, 20.0, 2], center=true);
    color("Silver") {
        translate([-13, cuerpo_r - 7.5, deck_spacing + 11])
            rotate([90, 0, 0])
                cylinder(r=8.0, h=10, center=true);
        translate([13, cuerpo_r - 7.5, deck_spacing + 11])
            rotate([90, 0, 0])
                cylinder(r=8.0, h=10, center=true);
    }

    for (a = [45, 135, 225, 315]) {
        rotate([0, 0, a])
            translate([cuerpo_r - 7, 0, 1.5])
                rotate([0, 0, -90])
                    pata_hibrida_articulada(15, -45);
    }
}

ensamble_completo_hibrido();
