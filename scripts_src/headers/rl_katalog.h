/*
   rl_katalog.h - Modulkatalog (Phase 2), ERZEUGT von tools/gen_katalog.py.
   Nicht von Hand aendern: Werte stehen in tools/ausbau_sim.py (UPGRADES).
*/
#ifndef RL_KATALOG_H
#define RL_KATALOG_H

#define RL_MODULE_ANZAHL            (23)
#define RL_MSG_MODUL_NAME           (400)   // + Modul-ID
#define RL_MSG_MODUL_EFFEKT         (500)   // + Modul-ID (nicht 440: 460-477 sind Menuezeilen)

#define RL_M_HAUSKLASSE_2             (0)
#define RL_M_HAUSKLASSE_3             (1)
#define RL_M_EINRICHTUNG_1            (2)
#define RL_M_EINRICHTUNG_2            (3)
#define RL_M_EINRICHTUNG_3            (4)
#define RL_M_BAR_1                    (5)
#define RL_M_BAR_2                    (6)
#define RL_M_SICHERHEIT_1             (7)
#define RL_M_SICHERHEIT_2             (8)
#define RL_M_SICHERHEIT_3             (9)
#define RL_M_QUARTIERE_1              (10)
#define RL_M_QUARTIERE_2              (11)
#define RL_M_KRANKENSTUBE             (12)
#define RL_M_KONTOR                   (13)
#define RL_M_VIP_TRAKT                (14)
#define RL_M_DEN_RIEGEL_INNEN         (15)
#define RL_M_NR_SPIELTISCHE           (16)
#define RL_M_RED_GOLDWAAGE            (17)
#define RL_M_RED_ENTZUGSSTUBE         (18)
#define RL_M_VC_WARTUNGSTUNNEL        (19)
#define RL_M_NCR_KARAWANENHOF         (20)
#define RL_M_SF_ANLEGESTEG            (21)
#define RL_M_SF_SHI_SIEGEL            (22)

#define RL_MK_KOSTEN                   (0)
#define RL_MK_GRUPPE                   (1)
#define RL_MK_VORAUS                   (2)
#define RL_MK_STAEDTE                  (3)
#define RL_MK_WOCHEN                   (4)
#define RL_MK_BEDINGUNG                (5)
#define RL_MK_ZIMMER                   (6)
#define RL_MK_AUSSTATTUNG              (7)
#define RL_MK_BAR                      (8)
#define RL_MK_SICHERHEIT               (9)
#define RL_MK_MORAL                    (10)
#define RL_MK_LOEHNE                   (11)
#define RL_MK_FLAGS                    (12)
#define RL_MK_NEBEN                    (13)
#define RL_MK_STADTMOD                 (14)
#define RL_MK_TRIBUT                   (15)
#define RL_MK_KLASSE                   (16)
#define RL_MK_STUFEN                   (17)

procedure rl_modul(variable id, variable feld);

procedure rl_modul(variable id, variable feld) begin
   variable werte;
   if (feld == RL_MK_KOSTEN) then
      werte := [2000, 4000, 500, 1200, 2500, 800, 2000, 400, 1000, 2000, 700, 1500, 1000, 600, 3000, 400, 2000, 400, 1200, 2500, 1200, 1500, 1000];
   else if (feld == RL_MK_GRUPPE) then
      werte := [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 2, 2, 2, 2, 2, 2, 2, 2];
   else if (feld == RL_MK_VORAUS) then
      werte := [-1, 0, -1, 2, 3, -1, 5, -1, 7, 8, -1, 10, -1, -1, 0, -1, -1, -1, 12, -1, -1, -1, -1];
   else if (feld == RL_MK_STAEDTE) then
      werte := [63, 2, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 63, 58, 1, 2, 4, 4, 8, 16, 32, 32];
   else if (feld == RL_MK_WOCHEN) then
      werte := [2, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1];
   else if (feld == RL_MK_BEDINGUNG) then
      werte := [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1];
   else if (feld == RL_MK_ZIMMER) then
      werte := [2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0];
   else if (feld == RL_MK_AUSSTATTUNG) then
      werte := [15, 15, 10, 15, 20, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 0, 5, 0, 0, 0, 0, 0, 0];
   else if (feld == RL_MK_BAR) then
      werte := [0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
   else if (feld == RL_MK_SICHERHEIT) then
      werte := [0, 0, 0, 0, 0, 0, 0, 10, 20, 25, 0, 0, 0, 0, 0, 10, 0, 0, 0, 25, 0, 0, 10];
   else if (feld == RL_MK_MORAL) then
      werte := [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0];
   else if (feld == RL_MK_LOEHNE) then
      werte := [0, 0, 0, 0, 0, 30, 0, 0, 0, 0, 0, 0, 60, 80, 0, 0, 0, 0, 0, 0, 0, 0, 0];
   else if (feld == RL_MK_FLAGS) then
      werte := [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 4, 0, 0, 0, 0, 0, 0, 0, 0];
   else if (feld == RL_MK_NEBEN) then
      werte := [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0];
   else if (feld == RL_MK_STADTMOD) then
      werte := [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 5, 20, 15, 15, 0];
   else if (feld == RL_MK_TRIBUT) then
      werte := [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -5];
   else if (feld == RL_MK_KLASSE) then
      werte := [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
   else if (feld == RL_MK_STUFEN) then
      werte := [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1];
   else
      return 0;
   return get_array(werte, id);
end

#endif
