/*
   rl_karten.h - Kartenpositionen, ERZEUGT von tools/bau_karten.py.
   Nicht von Hand aendern: Die Werte stehen dort in GOSSE, RLDEN01 und HAEUSER.
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
#define RL_GOSSE_ESSIE_HEX          (17866)
#define RL_GOSSE_KOLBE_HEX          (17270)
#define RL_GOSSE_MARA_HEX           (18466)
#define RL_GOSSE_DEKE_HEX           (17466)
#define RL_GOSSE_ANGREIFER1_HEX     (16866)
#define RL_GOSSE_ANGREIFER2_HEX     (17264)

// Das Silberne Strumpfband: Eingang auf newr1 (MAP_NEW_RENO_1), Innenkarte rlren01.map
#define RL_STRUMPF_TREPPE_PID       (33554788)
#define RL_STRUMPF_TREPPE_HEX       (23296)
#define RL_STRUMPF_TREPPE_EBENE     (0)
#define RL_STRUMPF_ANKUNFT_HEX      (23496)
#define RL_STRUMPF_STADTKARTE       (MAP_NEW_RENO_1)
#define RL_KARTE_STRUMPF            "rlren01.map"
#define RL_STRUMPF_EINGANG_HEX      (23093)
#define RL_STRUMPF_MADAME_HEX       (23699)
#define RL_STRUMPF_GAST1_HEX        (25699)
#define RL_STRUMPF_GAST2_HEX        (24703)
#define RL_STRUMPF_GAST3_HEX        (24900)
#define RL_STRUMPF_GAST4_HEX        (23106)
#define RL_STRUMPF_ANGREIFER1_HEX   (23300)
#define RL_STRUMPF_ANGREIFER2_HEX   (24098)

// Die Schlacke: Eingang auf redment (MAP_REDDING_MINE_ENT), Innenkarte rlred01.map
#define RL_SCHLACKE_TREPPE_PID      (33554788)
#define RL_SCHLACKE_TREPPE_HEX      (16483)
#define RL_SCHLACKE_TREPPE_EBENE    (0)
#define RL_SCHLACKE_ANKUNFT_HEX     (16683)
#define RL_SCHLACKE_STADTKARTE      (MAP_REDDING_MINE_ENT)
#define RL_KARTE_SCHLACKE           "rlred01.map"
#define RL_SCHLACKE_EINGANG_HEX     (11075)
#define RL_SCHLACKE_MADAME_HEX      (9674)
#define RL_SCHLACKE_GAST1_HEX       (9459)
#define RL_SCHLACKE_GAST2_HEX       (12459)
#define RL_SCHLACKE_GAST3_HEX       (13679)
#define RL_SCHLACKE_GAST4_HEX       (9088)
#define RL_SCHLACKE_ANGREIFER1_HEX  (10674)
#define RL_SCHLACKE_ANGREIFER2_HEX  (10676)

// Die Kloake: Eingang auf vctyctyd (MAP_VAULTCITY_COURTYARD), Innenkarte rlvct01.map
#define RL_KLOAKE_TREPPE_PID        (33554788)
#define RL_KLOAKE_TREPPE_HEX        (15671)
#define RL_KLOAKE_TREPPE_EBENE      (0)
#define RL_KLOAKE_ANKUNFT_HEX       (15871)
#define RL_KLOAKE_STADTKARTE        (MAP_VAULTCITY_COURTYARD)
#define RL_KARTE_KLOAKE             "rlvct01.map"
#define RL_KLOAKE_EINGANG_HEX       (12683)
#define RL_KLOAKE_MADAME_HEX        (13884)
#define RL_KLOAKE_GAST1_HEX         (12679)
#define RL_KLOAKE_GAST2_HEX         (14683)
#define RL_KLOAKE_GAST3_HEX         (14680)
#define RL_KLOAKE_GAST4_HEX         (13678)
#define RL_KLOAKE_ANGREIFER1_HEX    (12284)
#define RL_KLOAKE_ANGREIFER2_HEX    (13483)

// Die Traenke: Eingang auf ncrent (MAP_NCR_BAZAAR), Innenkarte rlncr01.map
#define RL_TRAENKE_TREPPE_PID       (33554788)
#define RL_TRAENKE_TREPPE_HEX       (24947)
#define RL_TRAENKE_TREPPE_EBENE     (0)
#define RL_TRAENKE_ANKUNFT_HEX      (25147)
#define RL_TRAENKE_STADTKARTE       (MAP_NCR_BAZAAR)
#define RL_KARTE_TRAENKE            "rlncr01.map"
#define RL_TRAENKE_EINGANG_HEX      (20756)
#define RL_TRAENKE_MADAME_HEX       (21958)
#define RL_TRAENKE_GAST1_HEX        (21344)
#define RL_TRAENKE_GAST2_HEX        (23758)
#define RL_TRAENKE_GAST3_HEX        (20748)
#define RL_TRAENKE_GAST4_HEX        (22758)
#define RL_TRAENKE_ANGREIFER1_HEX   (21157)
#define RL_TRAENKE_ANGREIFER2_HEX   (20754)

// Die Bilge: Eingang auf sfdock (MAP_SAN_FRAN_DOCK), Innenkarte rlsfr01.map
#define RL_BILGE_TREPPE_PID         (33554788)
#define RL_BILGE_TREPPE_HEX         (25075)
#define RL_BILGE_TREPPE_EBENE       (0)
#define RL_BILGE_ANKUNFT_HEX        (25076)
#define RL_BILGE_STADTKARTE         (MAP_SAN_FRAN_DOCK)
#define RL_KARTE_BILGE              "rlsfr01.map"
#define RL_BILGE_EINGANG_HEX        (22682)
#define RL_BILGE_MADAME_HEX         (22290)
#define RL_BILGE_GAST1_HEX          (22098)
#define RL_BILGE_GAST2_HEX          (21091)
#define RL_BILGE_GAST3_HEX          (21894)
#define RL_BILGE_GAST4_HEX          (21690)
#define RL_BILGE_ANGREIFER1_HEX     (22885)
#define RL_BILGE_ANGREIFER2_HEX     (22488)

#endif
