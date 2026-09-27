/*
   rl_karten.h - Kartenpositionen, ERZEUGT von tools/bau_karten.py.
   Nicht von Hand aendern: Die Werte stehen dort in GOSSE und RLDEN01.
*/
#ifndef RL_KARTEN_H
#define RL_KARTEN_H

// Eingang der Gosse auf Den Business 2 (zur Laufzeit gesetzt, siehe gl_rotlicht.ssl)
#define RL_GOSSE_TREPPE_PID         (33554788)   // Treppe (stway.frm)
#define RL_GOSSE_TREPPE_HEX         (18458)
#define RL_GOSSE_TREPPE_EBENE       (0)
#define RL_GOSSE_ANKUNFT_HEX        (18658)   // nach dem Rueckweg

// Innenkarte der Gosse
#define RL_KARTE_GOSSE              "rlden01.map"
#define RL_GOSSE_EINGANG_HEX        (17066)

#endif
