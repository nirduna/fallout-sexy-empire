/*
   rl_manager.h - Gemeinsame Dialogknoten aller Manager (Phase 4/5, Umsetzung 1)

   Jede Madame und jeder Manager nutzt dieselben Knoten, aber mit eigenen
   Texten in der eigenen .msg-Datei:
     100-199  Bericht, Kasse, Preise, Anteil, Moral, Krisen
     460-477  Ausbau-Menue
     400-422  Modulnamen, 500-522 Moduleffekte (aus _rl_module.inc)

   Das einbindende Skript stellt bereit:
     variable haus, welt, h   (Haus-Array, Welt-Array, Hausnummer)
     NAME                     (Skriptindex, fuer die .msg-Datei)
   und ruft nach end_dialogue das Makro RLM_NACH_DIALOG auf.

   Einstieg in das Manager-Menue: call RLM_Start;
*/
#ifndef RL_MANAGER_H
#define RL_MANAGER_H

variable rlm_aktive_gruppe;
variable rlm_slot1, rlm_slot2, rlm_slot3, rlm_slot4;
variable rlm_gewaehlt;
variable rlm_zeige_abspann := 0;

// Nach end_dialogue: Debug-Abspann starten (nur mit RL_DEBUG gesetzt)
#define RLM_NACH_DIALOG      if (rlm_zeige_abspann) then begin    \
                                rlm_zeige_abspann := 0;             \
                                endgame_slideshow;            \
                             end

procedure RLM_Start;
procedure RLM_Kasse;
procedure RLM_Preise;
procedure RLM_PreisRamsch;
procedure RLM_PreisStandard;
procedure RLM_PreisGehoben;
procedure RLM_Anteil;
procedure RLM_AnteilAusbeuterisch;
procedure RLM_AnteilUeblich;
procedure RLM_AnteilFair;
procedure RLM_Moral;
procedure RLM_Krise;
procedure RLM_StoffDoctor;
procedure RLM_StoffBezahlen;
procedure RLM_StoffLeine;
procedure RLM_StoffRauswurf;
procedure RLM_KriseGeld;
procedure RLM_Abspann;
procedure RLM_Ausbau;
procedure RLM_Gruppe0;
procedure RLM_Gruppe1;
procedure RLM_Gruppe2;
procedure RLM_Gruppe;
procedure RLM_Wahl1;
procedure RLM_Wahl2;
procedure RLM_Wahl3;
procedure RLM_Wahl4;
procedure RLM_Bestaetigen;
procedure RLM_Kaufen;
procedure RLM_Ende;
procedure rlm_krise_loesen;
procedure rlm_gekauft(variable id);
procedure rlm_modul_frei(variable id);
procedure rlm_gruppe_hat_module(variable gruppe);
procedure rlm_bezahlbar(variable kosten);
procedure rlm_option_modul(variable id, variable knoten);

/* ------------------------------------------------------------------ */
/* Hauptmenue                                                          */
/* ------------------------------------------------------------------ */
procedure RLM_Start begin
   Reply(mstr(100) + " " + mstr(101) + haus[rl_idx(h, RL_F_KUNDEN)]
         + mstr(102) + haus[rl_idx(h, RL_F_GEWINN)]
         + mstr(103) + haus[rl_idx(h, RL_F_KASSE)] + mstr(104));

   if (haus[rl_idx(h, RL_F_KASSE)] > 0) then
      NOption(110, RLM_Kasse, 004);
   NOption(111, RLM_Preise, 004);
   NOption(112, RLM_Anteil, 004);
   NOption(113, RLM_Moral, 004);
   NOption(117, RLM_Ausbau, 004);
   if (haus[rl_idx(h, RL_F_KRISE)] != RL_EV_KEINS) then
      NOption(114, RLM_Krise, 004);
#ifdef RL_DEBUG
   NOption(194, RLM_Abspann, 001);
#endif
   NOption(115, RLM_Ende, 004);
   NLowOption(116, RLM_Kasse);
end

procedure RLM_Kasse begin
   variable betrag := haus[rl_idx(h, RL_F_KASSE)];
   if (betrag > 0) then begin
      item_caps_adjust(dude_obj, betrag);
      haus[rl_idx(h, RL_F_KASSE)] := 0;
      Reply(mstr(120) + betrag + mstr(121));
   end else begin
      Reply(122);
   end
   NOption(123, RLM_Start, 004);
   NOption(124, RLM_Ende, 004);
   NLowOption(124, RLM_Ende);
end

/* ------------------------------------------------------------------ */
/* Preise und Anteil                                                   */
/* ------------------------------------------------------------------ */
procedure RLM_Preise begin
   Reply(mstr(130) + " " + mstr(135 + haus[rl_idx(h, RL_F_PREISSTUFE)]));
   NOption(131, RLM_PreisRamsch, 004);
   NOption(132, RLM_PreisStandard, 004);
   // Gehoben erst ab Ausstattung 40 und Moral 50 (Phase 1, Abschnitt 3.6)
   if ((haus[rl_idx(h, RL_F_AUSSTATTUNG)] >= 40) and (haus[rl_idx(h, RL_F_MORAL)] >= 50)) then
      NOption(133, RLM_PreisGehoben, 004);
   NOption(134, RLM_Start, 004);
end

procedure RLM_PreisRamsch begin
   haus[rl_idx(h, RL_F_PREISSTUFE)] := RL_PREIS_RAMSCH;
   Reply(139);
   NOption(123, RLM_Start, 004);
end

procedure RLM_PreisStandard begin
   haus[rl_idx(h, RL_F_PREISSTUFE)] := RL_PREIS_STANDARD;
   Reply(139);
   NOption(123, RLM_Start, 004);
end

procedure RLM_PreisGehoben begin
   haus[rl_idx(h, RL_F_PREISSTUFE)] := RL_PREIS_GEHOBEN;
   Reply(139);
   NOption(123, RLM_Start, 004);
end

procedure RLM_Anteil begin
   Reply(mstr(140) + get_array([25, 35, 45], haus[rl_idx(h, RL_F_ANTEIL)]) + mstr(141));
   BOption(142, RLM_AnteilAusbeuterisch, 004);
   NOption(143, RLM_AnteilUeblich, 004);
   GOption(144, RLM_AnteilFair, 004);
   NOption(148, RLM_Start, 004);
end

procedure RLM_AnteilAusbeuterisch begin
   haus[rl_idx(h, RL_F_ANTEIL)] := RL_ANTEIL_AUSBEUTERISCH;
   Reply(145);
   NOption(123, RLM_Start, 004);
end

procedure RLM_AnteilUeblich begin
   haus[rl_idx(h, RL_F_ANTEIL)] := RL_ANTEIL_BRANCHENUEBLICH;
   Reply(146);
   NOption(123, RLM_Start, 004);
end

procedure RLM_AnteilFair begin
   haus[rl_idx(h, RL_F_ANTEIL)] := RL_ANTEIL_FAIR;
   Reply(147);
   NOption(123, RLM_Start, 004);
end

procedure RLM_Moral begin
   variable moral := haus[rl_idx(h, RL_F_MORAL)];
   if (moral >= 70) then
      Reply(150);
   else if (moral >= 40) then
      Reply(151);
   else if (moral >= RL_FLUCHT_MORAL) then
      Reply(152);
   else
      Reply(153);
   NOption(123, RLM_Start, 004);
end

/* ------------------------------------------------------------------ */
/* Krisen (Phase 4, Abschnitt 4.2)                                     */
/* ------------------------------------------------------------------ */
procedure RLM_Krise begin
   if (haus[rl_idx(h, RL_F_KRISE)] == RL_EV_STOFF) then begin
      Reply(160);
      if (has_skill(dude_obj, SKILL_DOCTOR) >= 60) then
         GOption(161, RLM_StoffDoctor, 004);
      if (dude_caps >= 200) then
         NOption(162, RLM_StoffBezahlen, 004);
      BOption(163, RLM_StoffLeine, 004);
      BOption(164, RLM_StoffRauswurf, 004);
   end else begin
      Reply(mstr(170) + " " + mstr(180 + haus[rl_idx(h, RL_F_KRISE)]));
      if (dude_caps >= 300) then
         NOption(171, RLM_KriseGeld, 004);
   end
   NOption(172, RLM_Ende, 004);
end

procedure RLM_StoffDoctor begin
   call rlm_krise_loesen;
   haus[rl_idx(h, RL_F_MORAL)] := rl_min(100, haus[rl_idx(h, RL_F_MORAL)] + 5);
   Reply(165);
   NOption(123, RLM_Start, 004);
end

procedure RLM_StoffBezahlen begin
   item_caps_adjust(dude_obj, -200);
   call rlm_krise_loesen;
   Reply(166);
   NOption(123, RLM_Start, 004);
end

// Tyrannen-Variante: dauerhaft Moral hoechstens 40, Karma -3 pro Woche
procedure RLM_StoffLeine begin
   call rlm_krise_loesen;
   haus[rl_idx(h, RL_F_MODULE)] := haus[rl_idx(h, RL_F_MODULE)] bwor RL_MOD_LEINE;
   haus[rl_idx(h, RL_F_MORAL)] := rl_min(40, haus[rl_idx(h, RL_F_MORAL)]);
   Reply(167);
   NOption(123, RLM_Start, 004);
end

procedure RLM_StoffRauswurf begin
   call rlm_krise_loesen;
   haus[rl_idx(h, RL_F_PERSONAL)] := rl_max(0, haus[rl_idx(h, RL_F_PERSONAL)] - 1);
   haus[rl_idx(h, RL_F_MORAL)] := rl_max(0, haus[rl_idx(h, RL_F_MORAL)] - 10);
   Reply(168);
   NOption(123, RLM_Start, 004);
end

procedure RLM_KriseGeld begin
   item_caps_adjust(dude_obj, -300);
   call rlm_krise_loesen;
   Reply(173);
   NOption(123, RLM_Start, 004);
end

procedure RLM_Abspann begin
   rlm_zeige_abspann := 1;
end

/* ------------------------------------------------------------------ */
/* Ausbau (Phase 2): drei Gruppen, je hoechstens vier Angebote         */
/* ------------------------------------------------------------------ */
procedure RLM_Ausbau begin
   variable id := haus[rl_idx(h, RL_F_BAU_ID)] - 1;
   if (id >= 0) then begin
      Reply(mstr(472) + mstr(RL_MSG_MODUL_NAME + id) + mstr(473) + haus[rl_idx(h, RL_F_BAU_WOCHEN)] + mstr(474));
      NOption(477, RLM_Start, 004);
      return;
   end
   Reply(460);
   if (rlm_gruppe_hat_module(0)) then NOption(461, RLM_Gruppe0, 004);
   if (rlm_gruppe_hat_module(1)) then NOption(462, RLM_Gruppe1, 004);
   if (rlm_gruppe_hat_module(2)) then NOption(463, RLM_Gruppe2, 004);
   NOption(477, RLM_Start, 004);
end

procedure RLM_Gruppe0 begin
   rlm_aktive_gruppe := 0;
   call RLM_Gruppe;
end

procedure RLM_Gruppe1 begin
   rlm_aktive_gruppe := 1;
   call RLM_Gruppe;
end

procedure RLM_Gruppe2 begin
   rlm_aktive_gruppe := 2;
   call RLM_Gruppe;
end

// Zeigt pro Kette (z. B. Einrichtung I-III) nur die naechste freie Stufe
procedure RLM_Gruppe begin
   variable id := 0, slot := 0;
   rlm_slot1 := -1; rlm_slot2 := -1; rlm_slot3 := -1; rlm_slot4 := -1;
   while ((id < RL_MODULE_ANZAHL) and (slot < 4)) do begin
      if ((rl_modul(id, RL_MK_GRUPPE) == rlm_aktive_gruppe) and rlm_modul_frei(id)) then begin
         slot := slot + 1;
         if (slot == 1) then rlm_slot1 := id;
         else if (slot == 2) then rlm_slot2 := id;
         else if (slot == 3) then rlm_slot3 := id;
         else rlm_slot4 := id;
      end
      id := id + 1;
   end

   if (slot == 0) then
      Reply(465);
   else
      Reply(464);
   if (rlm_slot1 >= 0) then call rlm_option_modul(rlm_slot1, 1);
   if (rlm_slot2 >= 0) then call rlm_option_modul(rlm_slot2, 2);
   if (rlm_slot3 >= 0) then call rlm_option_modul(rlm_slot3, 3);
   if (rlm_slot4 >= 0) then call rlm_option_modul(rlm_slot4, 4);
   NOption(477, RLM_Ausbau, 004);
end

procedure rlm_option_modul(variable id, variable knoten) begin
   variable text := mstr(RL_MSG_MODUL_NAME + id) + " ($" + rl_modul(id, RL_MK_KOSTEN) + ")";
   if (knoten == 1) then NOption(text, RLM_Wahl1, 004);
   else if (knoten == 2) then NOption(text, RLM_Wahl2, 004);
   else if (knoten == 3) then NOption(text, RLM_Wahl3, 004);
   else NOption(text, RLM_Wahl4, 004);
end

procedure RLM_Wahl1 begin
   rlm_gewaehlt := rlm_slot1;
   call RLM_Bestaetigen;
end

procedure RLM_Wahl2 begin
   rlm_gewaehlt := rlm_slot2;
   call RLM_Bestaetigen;
end

procedure RLM_Wahl3 begin
   rlm_gewaehlt := rlm_slot3;
   call RLM_Bestaetigen;
end

procedure RLM_Wahl4 begin
   rlm_gewaehlt := rlm_slot4;
   call RLM_Bestaetigen;
end

procedure RLM_Bestaetigen begin
   variable kosten := rl_modul(rlm_gewaehlt, RL_MK_KOSTEN);
   Reply(mstr(RL_MSG_MODUL_EFFEKT + rlm_gewaehlt) + " " + mstr(466) + kosten + mstr(467)
         + rl_max(0, haus[rl_idx(h, RL_F_KASSE)]) + mstr(468) + dude_caps + mstr(469));
   if (rlm_bezahlbar(kosten)) then begin
      NOption(470, RLM_Kaufen, 004);
      NOption(477, RLM_Gruppe, 004);
   end else begin
      NOption(471, RLM_Gruppe, 004);
   end
end

// Bezahlt wird zuerst aus der Kasse des Hauses, der Rest aus der Tasche des Spielers
procedure RLM_Kaufen begin
   variable kosten := rl_modul(rlm_gewaehlt, RL_MK_KOSTEN);
   variable aus_kasse := rl_min(rl_max(0, haus[rl_idx(h, RL_F_KASSE)]), kosten);
   haus[rl_idx(h, RL_F_KASSE)] := haus[rl_idx(h, RL_F_KASSE)] - aus_kasse;
   if (kosten > aus_kasse) then
      item_caps_adjust(dude_obj, -(kosten - aus_kasse));
   haus[rl_idx(h, RL_F_GEKAUFT)]    := haus[rl_idx(h, RL_F_GEKAUFT)] bwor rl_bit(rlm_gewaehlt);
   haus[rl_idx(h, RL_F_BAU_ID)]     := rlm_gewaehlt + 1;
   haus[rl_idx(h, RL_F_BAU_WOCHEN)] := rl_modul(rlm_gewaehlt, RL_MK_WOCHEN);
   Reply(mstr(475) + rl_modul(rlm_gewaehlt, RL_MK_WOCHEN) + mstr(476));
   NOption(123, RLM_Start, 004);
end

procedure RLM_Ende begin
end

/* ------------------------------------------------------------------ */
/* Hilfsfunktionen                                                     */
/* ------------------------------------------------------------------ */
procedure rlm_krise_loesen begin
   haus[rl_idx(h, RL_F_KRISE)] := RL_EV_KEINS;
   haus[rl_idx(h, RL_F_KRISENWOCHEN)] := 0;
end

procedure rlm_gekauft(variable id) begin
   return ((haus[rl_idx(h, RL_F_GEKAUFT)] bwand rl_bit(id)) != 0);
end

procedure rlm_modul_frei(variable id) begin
   variable voraus := rl_modul(id, RL_MK_VORAUS);
   if (rlm_gekauft(id)) then return 0;
   if ((rl_modul(id, RL_MK_STAEDTE) bwand rl_bit(h)) == 0) then return 0;
   if ((voraus >= 0) and not rlm_gekauft(voraus)) then return 0;
   if ((rl_modul(id, RL_MK_BEDINGUNG) == 1) and (welt[RL_W_SHI_GEFALLEN] == 0)) then return 0;
   return 1;
end

procedure rlm_gruppe_hat_module(variable gruppe) begin
   variable id := 0;
   while (id < RL_MODULE_ANZAHL) do begin
      if ((rl_modul(id, RL_MK_GRUPPE) == gruppe) and rlm_modul_frei(id)) then return 1;
      id := id + 1;
   end
   return 0;
end

procedure rlm_bezahlbar(variable kosten) begin
   return (rl_max(0, haus[rl_idx(h, RL_F_KASSE)]) + dude_caps >= kosten);
end

#endif
