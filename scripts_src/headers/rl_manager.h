/*
   rl_manager.h - Gemeinsame Dialogknoten aller Manager (Phase 4/5, Umsetzung 1)

   Jede Madame und jeder Manager nutzt dieselben Knoten, aber mit eigenen
   Texten in der eigenen .msg-Datei:
     100-199  Bericht, Kasse, Preise, Anteil, Moral, Krisen
     460-477  Ausbau-Menue
     480-499  Personal und Anwerber (Umsetzung 3), Pferch und Metzger (Umsetzung 4)
     400-422  Modulnamen, 500-522 Moduleffekte (aus _rl_module.inc)
     430-439  Namen der Sondermodule, 530-539 ihre Wirkung (rl_sonder.h)
     174-177  Metzgers Vergeltung (Krise), 188 ihr Text
     600-619  Die Route nach Sueden (Ketten, Akt 3, Umsetzung 5)

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
procedure RLM_Personal;
procedure RLM_Werben;
procedure RLM_Zwingen;
procedure RLM_AnwerberWeg;
procedure RLM_DebugZimmer;
procedure RLM_MetzgerWare;
procedure rlm_bezahlen(variable kosten);
procedure rlm_metzger_preis;
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
procedure rlm_modul_name(variable id);
procedure rlm_modul_effekt(variable id);
procedure rlm_modul_kosten(variable id);
procedure rlm_modul_wochen(variable id);
procedure rlm_sonder_frei(variable sm);
procedure RLM_Route;
procedure RLM_RoutePerception;
procedure RLM_RouteStart;
procedure RLM_VergeltungKampf;
procedure RLM_VergeltungRangers;

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
   NOption(118, RLM_Personal, 004);
   NOption(117, RLM_Ausbau, 004);
   if (haus[rl_idx(h, RL_F_KRISE)] != RL_EV_KEINS) then
      NOption(114, RLM_Krise, 004);
   // Ketten, Akt 3 im Fluchtzweig: die Route nach Sueden (Umsetzung 5)
   if ((h == RL_DEN) and (welt[RL_W_KETTEN_ZWEIG] == RL_KETTEN_ZWEIG_FLUCHT)
       and (((welt[RL_W_KETTEN] >= RL_KETTEN_KETTE) and (welt[RL_W_KETTEN] <= RL_KETTEN_STURM))
            or (welt[RL_W_KETTEN] == RL_KETTEN_STILLER_KRIEG))) then
      NOption(600, RLM_Route, 004);
#ifdef RL_DEBUG
   NOption(195, RLM_DebugZimmer, 001);
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
      // Metzgers Vergeltung im stillen Krieg (Phase 4, Abschnitt 4.3)
      if (haus[rl_idx(h, RL_F_KRISE)] == RL_EV_VERGELTUNG) then begin
         if (rl_max(rl_max(has_skill(dude_obj, SKILL_SMALL_GUNS), has_skill(dude_obj, SKILL_MELEE)),
                    has_skill(dude_obj, SKILL_UNARMED_COMBAT)) >= 60) then
            NOption(174, RLM_VergeltungKampf, 004);
         if (welt[RL_W_RANGERS] >= RL_RANGERS_KONTAKT) then
            GOption(175, RLM_VergeltungRangers, 004);
      end
   end
   NOption(172, RLM_Ende, 004);
end

procedure RLM_VergeltungKampf begin
   call rlm_krise_loesen;
   call rl_haus_plus(haus, h, RL_F_HITZE, 10);
   Reply(176);
   NOption(123, RLM_Start, 004);
end

procedure RLM_VergeltungRangers begin
   call rlm_krise_loesen;
   Reply(177);
   NOption(123, RLM_Start, 004);
end

/* ------------------------------------------------------------------ */
/* Ketten, Akt 3 im Fluchtzweig: die Route nach Sueden (Umsetzung 5)   */
/* ------------------------------------------------------------------ */
procedure RLM_Route begin
   if (welt[RL_W_RANGERS] == RL_RANGERS_UNBEKANNT) then begin
      Reply(601);
      if (dude_perception >= 7) then
         NOption(602, RLM_RoutePerception, 004);
   end else if ((haus[rl_idx(h, RL_F_MODULE)] bwand RL_MOD_ZUFLUCHT) == 0) then begin
      Reply(603);
   end else if (welt[RL_W_AUFTRAG] != RL_AUFTRAG_KEINER) then begin
      Reply(604);
   end else begin
      Reply(mstr(605) + welt[RL_W_TRANSPORTE] + mstr(606));
      NOption(mstr(607) + rl_transport_chance(welt) + mstr(608), RLM_RouteStart, 004);
   end
   NOption(609, RLM_Start, 004);
end

procedure RLM_RoutePerception begin
   welt[RL_W_RANGERS] := RL_RANGERS_KONTAKT;
   Reply(610);
   NOption(123, RLM_Route, 004);
end

procedure RLM_RouteStart begin
   call rl_auftrag_starten(welt, RL_AUFTRAG_SUEDEN, rl_transport_chance(welt));
   Reply(611);
   NOption(123, RLM_Start, 004);
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
   call rl_personal_verlust(haus, h, RL_VERLUST_ABGANG);
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
/* Personal und Anwerber (Umsetzung 3, Phase 4 Abschnitt 2.2)          */
/* ------------------------------------------------------------------ */
procedure RLM_Personal begin
   variable methode := haus[rl_idx(h, RL_F_ANWERBER)];
   variable text;
   text := mstr(480) + haus[rl_idx(h, RL_F_ZIMMER)] + mstr(481) + haus[rl_idx(h, RL_F_PERSONAL)]
           + mstr(482) + " " + mstr(483 + methode);
   if (methode and (haus[rl_idx(h, RL_F_PERSONAL)] >= haus[rl_idx(h, RL_F_ZIMMER)])) then
      text := text + " " + mstr(493);
   if (haus[rl_idx(h, RL_F_ZWANG)] > 0) then
      text := text + " " + mstr(494) + haus[rl_idx(h, RL_F_ZWANG)] + mstr(495);
   Reply(text);
   // Metzger liefert nach, solange die Gilde steht (Phase 4, Abschnitt 2.3)
   if ((haus[rl_idx(h, RL_F_MODULE)] bwand RL_MOD_RIEGEL_AUSSEN) and (not rl_metzger_tot)
       and (welt[RL_W_METZGER] != RL_METZGER_FEIND)
       and (haus[rl_idx(h, RL_F_PERSONAL)] < haus[rl_idx(h, RL_F_ZIMMER)])
       and rlm_bezahlbar(rlm_metzger_preis)) then
      BOption(mstr(496) + rlm_metzger_preis + mstr(497), RLM_MetzgerWare, 004);
   if (methode != RL_ANWERBER_WERBEN) then
      GOption(486, RLM_Werben, 004);
   if (methode != RL_ANWERBER_ZWINGEN) then
      BOption(487, RLM_Zwingen, 004);
   if (methode != RL_ANWERBER_KEINER) then
      NOption(488, RLM_AnwerberWeg, 004);
   NOption(489, RLM_Start, 004);
end

procedure RLM_Werben begin
   call rl_anwerber_setzen(haus, h, RL_ANWERBER_WERBEN);
   Reply(490);
   NOption(123, RLM_Start, 004);
end

procedure RLM_Zwingen begin
   call rl_anwerber_setzen(haus, h, RL_ANWERBER_ZWINGEN);
   Reply(491);
   NOption(123, RLM_Start, 004);
end

procedure RLM_AnwerberWeg begin
   call rl_anwerber_setzen(haus, h, RL_ANWERBER_KEINER);
   Reply(492);
   NOption(123, RLM_Start, 004);
end

procedure RLM_MetzgerWare begin
   call rlm_bezahlen(rlm_metzger_preis);
   call rl_zwang_dazu(haus, h, 1);
   Reply(498);
   NOption(123, RLM_Start, 004);
end

// Debug: zwei leere Zimmer, damit sich die Anwerbung ohne Ausbau testen laesst
procedure RLM_DebugZimmer begin
   haus[rl_idx(h, RL_F_ZIMMER)] := haus[rl_idx(h, RL_F_ZIMMER)] + 2;
   call RLM_Personal;
end

/* ------------------------------------------------------------------ */
/* Ausbau (Phase 2): drei Gruppen, je hoechstens vier Angebote         */
/* ------------------------------------------------------------------ */
procedure RLM_Ausbau begin
   variable id := haus[rl_idx(h, RL_F_BAU_ID)] - 1;
   if (id >= 0) then begin
      Reply(mstr(472) + rlm_modul_name(id) + mstr(473) + haus[rl_idx(h, RL_F_BAU_WOCHEN)] + mstr(474));
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

// Zeigt pro Kette (z. B. Einrichtung I-III) nur die naechste freie Stufe.
// In Gruppe 2 kommen die Sondermodule der Stadt dazu (rl_sonder.h).
procedure RLM_Gruppe begin
   variable id := 0, slot := 0, frei;
   rlm_slot1 := -1; rlm_slot2 := -1; rlm_slot3 := -1; rlm_slot4 := -1;
   while ((id < RL_SONDER_BASIS + RL_SM_ANZAHL) and (slot < 4)) do begin
      frei := 0;
      if (id < RL_MODULE_ANZAHL) then
         frei := ((rl_modul(id, RL_MK_GRUPPE) == rlm_aktive_gruppe) and rlm_modul_frei(id));
      else if ((id >= RL_SONDER_BASIS) and (rlm_aktive_gruppe == 2)) then
         frei := rlm_sonder_frei(id - RL_SONDER_BASIS);
      if (frei) then begin
         slot := slot + 1;
         if (slot == 1) then rlm_slot1 := id;
         else if (slot == 2) then rlm_slot2 := id;
         else if (slot == 3) then rlm_slot3 := id;
         else rlm_slot4 := id;
      end
      id := id + 1;
      if (id == RL_MODULE_ANZAHL) then id := RL_SONDER_BASIS;
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
   variable text := rlm_modul_name(id) + " ($" + rlm_modul_kosten(id) + ")";
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
   variable kosten := rlm_modul_kosten(rlm_gewaehlt);
   Reply(rlm_modul_effekt(rlm_gewaehlt) + " " + mstr(466) + kosten + mstr(467)
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
   call rlm_bezahlen(rlm_modul_kosten(rlm_gewaehlt));
   if (rlm_gewaehlt < RL_SONDER_BASIS) then
      haus[rl_idx(h, RL_F_GEKAUFT)] := haus[rl_idx(h, RL_F_GEKAUFT)] bwor rl_bit(rlm_gewaehlt);
   haus[rl_idx(h, RL_F_BAU_ID)]     := rlm_gewaehlt + 1;
   haus[rl_idx(h, RL_F_BAU_WOCHEN)] := rlm_modul_wochen(rlm_gewaehlt);
   Reply(mstr(475) + rlm_modul_wochen(rlm_gewaehlt) + mstr(476));
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
   // Riegel innen und Riegel aussen schliessen sich aus (Phase 2)
   if ((id == RL_M_DEN_RIEGEL_INNEN) and (haus[rl_idx(h, RL_F_MODULE)] bwand RL_MOD_RIEGEL_AUSSEN)) then return 0;
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
   if (gruppe == 2) then begin
      id := 0;
      while (id < RL_SM_ANZAHL) do begin
         if (rlm_sonder_frei(id)) then return 1;
         id := id + 1;
      end
   end
   return 0;
end

// Katalog- und Sondermodule einheitlich (Sondermodule ab RL_SONDER_BASIS)
procedure rlm_modul_name(variable id) begin
   if (id >= RL_SONDER_BASIS) then return mstr(RL_MSG_SONDER_NAME + id - RL_SONDER_BASIS);
   return mstr(RL_MSG_MODUL_NAME + id);
end

procedure rlm_modul_effekt(variable id) begin
   if (id >= RL_SONDER_BASIS) then return mstr(RL_MSG_SONDER_EFFEKT + id - RL_SONDER_BASIS);
   return mstr(RL_MSG_MODUL_EFFEKT + id);
end

procedure rlm_modul_kosten(variable id) begin
   if (id >= RL_SONDER_BASIS) then return rl_sonder_kosten(id - RL_SONDER_BASIS);
   return rl_modul(id, RL_MK_KOSTEN);
end

procedure rlm_modul_wochen(variable id) begin
   if (id >= RL_SONDER_BASIS) then return rl_sonder_wochen(id - RL_SONDER_BASIS);
   return rl_modul(id, RL_MK_WOCHEN);
end

/* Sondermodule: nur in ihrer Stadt, nur einmal, mit ihren Bedingungen */
procedure rlm_sonder_frei(variable sm) begin
   variable module := haus[rl_idx(h, RL_F_MODULE)];
   if (module bwand rl_sonder_flag(sm)) then return 0;
   if (haus[rl_idx(h, RL_F_BAU_ID)] == RL_SONDER_BASIS + sm + 1) then return 0;
   if (sm == RL_SM_ZUFLUCHT) then begin
      // Die Zuflucht schliesst den Riegel aussen aus (Phase 2). Frei, sobald Mara
      // versteckt ist oder die Route nach Sueden laeuft (Ketten, Akt 2/3).
      if ((h != RL_DEN) or (module bwand RL_MOD_RIEGEL_AUSSEN)) then return 0;
      return ((welt[RL_W_MARA_WEG] == RL_MARA_VERSTECKT)
              or ((welt[RL_W_KETTEN_ZWEIG] == RL_KETTEN_ZWEIG_FLUCHT) and (welt[RL_W_KETTEN] >= RL_KETTEN_KETTE)));
   end
   return 0;
end

procedure rlm_bezahlbar(variable kosten) begin
   return (rl_max(0, haus[rl_idx(h, RL_F_KASSE)]) + dude_caps >= kosten);
end

// Zuerst aus der Kasse des Hauses, der Rest aus der Tasche des Spielers
procedure rlm_bezahlen(variable kosten) begin
   variable aus_kasse := rl_min(rl_max(0, haus[rl_idx(h, RL_F_KASSE)]), kosten);
   haus[rl_idx(h, RL_F_KASSE)] := haus[rl_idx(h, RL_F_KASSE)] - aus_kasse;
   if (kosten > aus_kasse) then
      item_caps_adjust(dude_obj, -(kosten - aus_kasse));
end

// Metzgers Preis je Person; dem "Seelenverkaeufer" 20 % billiger (Phase 6)
procedure rlm_metzger_preis begin
   if (global_var(GVAR_RL_TITEL_SEELE)) then return RL_METZGER_KOPFPREIS * 80 / 100;
   return RL_METZGER_KOPFPREIS;
end

#endif
