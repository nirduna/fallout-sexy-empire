/*
   rl_manager.h - Gemeinsame Dialogknoten aller Manager (Phase 4/5, Umsetzung 1)

   Jede Madame und jeder Manager nutzt dieselben Knoten, aber mit eigenen
   Texten in der eigenen .msg-Datei:
     100-199  Bericht, Kasse, Preise, Anteil, Moral, Krisen
              (105-109: die zwei Untermenues "Fuehrung" und "Draussen")
     460-477  Ausbau-Menue
     480-499  Personal und Anwerber (Umsetzung 3), Pferch und Metzger (Umsetzung 4)
     400-422  Modulnamen, 500-522 Moduleffekte (aus _rl_module.inc)
     430-439  Namen der Sondermodule, 530-539 ihre Wirkung (rl_sonder.h)
     174-177  Metzgers Vergeltung (Krise), 188 ihr Text
     600-619  Die Route nach Sueden (Ketten, Akt 3, Umsetzung 5)
     620-639  Die anderen Staedte (nur in der Gosse, Umsetzung 6)
     950-999  Talente (Umsetzung 13, _rl_talente.inc, bei allen Madames gleich)
    1000-1059  Jobs und Laeuferroute (Umsetzung 14, _rl_jobs.inc, bei allen gleich)
    1100-1249  Krisen und ihre Loesungswege (Umsetzung 15, _rl_krisen.inc)

   Das einbindende Skript stellt bereit:
     variable haus, welt, h   (Haus-Array, Welt-Array, Hausnummer)
     NAME                     (Skriptindex, fuer die .msg-Datei)
   und ruft nach end_dialogue das Makro RLM_NACH_DIALOG auf.
   Optional: RLM_EXTRA_OPTIONEN, eigene Optionen im Hauptmenue (Umsetzung 7),
   RLM_DRAUSSEN_OPTIONEN, eigene Optionen im Menue "Draussen" (Umsetzung 14).

   Madames ohne eigene Stimme fuer alles binden _rl_manager.inc ein (die
   neutralen Texte) und schreiben nur ihre eigenen Saetze selbst.

   Einstieg in das Manager-Menue: call RLM_Start;

   Das Optionsfenster der Engine fasst etwa acht einzeilige Optionen; was
   darueber hinausgeht, zeigt sie nicht an (game_dialog.cc, _gdProcessUpdate).
   Deshalb hat das Hauptmenue zwei Untermenues: "Fuehrung" (Preise, Anteil,
   Moral, Personal, Ausbau) und "Draussen" (Talente, Jobs, andere Staedte).
   Das Pruefwerkzeug meldet jedes Menue, das nicht ins Fenster passt.
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
procedure RLM_Fuehrung;
procedure RLM_Draussen;
procedure RLM_Jobs;
procedure rlm_tyler_weg;
procedure rlm_job_fertig(variable text);
procedure RLM_TylerZahlen;
procedure RLM_TylerStopp;
procedure RLM_PolizeiZahlen;
procedure RLM_PolizeiStopp;
procedure RLM_Totengraeber;
procedure RLM_McClure;
procedure RLM_SchutzAn;
procedure RLM_SchutzAus;
procedure RLM_Abfangen;
procedure RLM_Buecher;
procedure RLM_BuchVerkaufen;
procedure RLM_Klinik;
procedure RLM_Rangers;
procedure rlm_laeufer_da;
procedure RLM_Laeufer;
procedure RLM_MarcusReden;
procedure RLM_MarcusGeld;
procedure RLM_MarcusAnstand;
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
procedure rlm_krise_fertig(variable text);
procedure RLM_SoldatenZahlen;
procedure RLM_SoldatenTrinken;
procedure RLM_SoldatenRuestung;
procedure RLM_SoldatenLassen;
procedure RLM_SoldatenReden;
procedure RLM_SoldatenWerben;
procedure RLM_SoldatenKampf;
procedure RLM_StoffHeilen;
procedure RLM_RazziaVerstecken;
procedure RLM_RazziaWachen;
procedure RLM_RazziaSelbst;
procedure RLM_RazziaWaage;
procedure RLM_RazziaSchutzgeld;
procedure RLM_FreierSelbst;
procedure RLM_FreierVerbot;
procedure RLM_SeucheDoctor;
procedure RLM_SeucheArzt;
procedure RLM_SeucheSchliessen;
procedure RLM_KasseBuecher;
procedure RLM_KasseBeschatten;
procedure RLM_KasseLassen;
procedure RLM_FluchtLassen;
procedure RLM_FluchtHolen;
procedure RLM_TodBeerdigen;
procedure RLM_TodSchweigen;
procedure RLM_TodRache;
procedure RLM_GeheimnisAkte;
procedure RLM_GeheimnisVerkaufen;
procedure RLM_GeheimnisVergessen;
procedure RLM_AbwerbungHalten;
procedure RLM_AbwerbungLassen;
procedure RLM_UeberfallSpur;
procedure RLM_UeberfallAbschreiben;
procedure RLM_GhulRaus;
procedure RLM_GhulReden;
procedure RLM_GhulLassen;
procedure RLM_RichterHeilen;
procedure RLM_RichterBlossstellen;
procedure RLM_RichterGift;
procedure RLM_BunkerAusliefern;
procedure RLM_BunkerVerstecken;
procedure RLM_BunkerWeg;
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
procedure RLM_Staedte;
procedure RLM_StadtNR;
procedure RLM_StadtRed;
procedure RLM_StadtVC;
procedure RLM_StadtNCR;
procedure RLM_StadtSF;
procedure rlm_stadt_erzaehlt(variable stadt);
procedure RLM_Route;
procedure RLM_RoutePerception;
procedure RLM_RouteStart;
procedure RLM_VergeltungKampf;
procedure RLM_VergeltungRangers;
procedure rlm_talente_da;
procedure RLM_Talente;
procedure RLM_Vesper;
procedure RLM_VesperAuftrag;
procedure RLM_VesperFrage;
procedure RLM_VesperEhrlich;
procedure RLM_VesperLuege;
procedure RLM_Julian;
procedure RLM_JulianBarter;
procedure RLM_JulianGambling;
procedure RLM_JulianStar;
procedure RLM_JulianTyrann;
procedure RLM_JulianEntzug;
procedure RLM_JulianClean;
procedure RLM_JulianRetten;
procedure RLM_JulianGerettet;
procedure RLM_Abigail;
procedure RLM_AbigailBuergerin;
procedure RLM_AbigailAkte;
procedure RLM_AbigailErpressen;
procedure RLM_Talus;
procedure RLM_TalusWahrheit;
procedure RLM_TalusAusbruch;
procedure RLM_TalusLesen;
procedure rlm_julian_frei(variable weg, variable text);
procedure rlm_abigail_da(variable weg, variable loyal, variable text);

/* ------------------------------------------------------------------ */
/* Hauptmenue                                                          */
/* ------------------------------------------------------------------ */
procedure RLM_Start begin
   Reply(mstr(100) + " " + mstr(101) + haus[rl_idx(h, RL_F_KUNDEN)]
         + mstr(102) + haus[rl_idx(h, RL_F_GEWINN)]
         + mstr(103) + haus[rl_idx(h, RL_F_KASSE)] + mstr(104));

   if (haus[rl_idx(h, RL_F_KASSE)] > 0) then
      NOption(110, RLM_Kasse, 004);
   NOption(106, RLM_Fuehrung, 004);
   if (haus[rl_idx(h, RL_F_KRISE)] != RL_EV_KEINS) then
      NOption(114, RLM_Krise, 004);
   // Ketten, Akt 3 im Fluchtzweig: die Route nach Sueden (Umsetzung 5)
   if ((h == RL_DEN) and (welt[RL_W_KETTEN_ZWEIG] == RL_KETTEN_ZWEIG_FLUCHT)
       and (((welt[RL_W_KETTEN] >= RL_KETTEN_KETTE) and (welt[RL_W_KETTEN] <= RL_KETTEN_STURM))
            or (welt[RL_W_KETTEN] == RL_KETTEN_STILLER_KRIEG))) then
      NOption(600, RLM_Route, 004);
   NOption(107, RLM_Draussen, 004);
#ifdef RLM_EXTRA_OPTIONEN
   RLM_EXTRA_OPTIONEN
#endif
   NOption(115, RLM_Ende, 004);
   NLowOption(116, RLM_Kasse);
end

// Wie das Haus gefuehrt wird: Preise, Anteil, Moral, Personal, Ausbau
procedure RLM_Fuehrung begin
   Reply(105);
   NOption(111, RLM_Preise, 004);
   NOption(112, RLM_Anteil, 004);
   NOption(113, RLM_Moral, 004);
   NOption(118, RLM_Personal, 004);
   NOption(117, RLM_Ausbau, 004);
#ifdef RL_DEBUG
   NOption(195, RLM_DebugZimmer, 001);
   NOption(194, RLM_Abspann, 001);
#endif
   NOption(109, RLM_Start, 004);
end

// Geschaefte ausserhalb des Hauses: andere Staedte, Talente, Jobs, Laeuferroute
procedure RLM_Draussen begin
   Reply(108);
   // Die Gosse kennt die anderen Staedte (Umsetzung 6)
   if (h == RL_DEN) then
      NOption(620, RLM_Staedte, 004);
   if (rlm_talente_da) then
      NOption(950, RLM_Talente, 004);
   NOption(1000, RLM_Jobs, 004);
   if (rlm_laeufer_da) then
      NOption(1040, RLM_Laeufer, 004);
#ifdef RLM_DRAUSSEN_OPTIONEN
   RLM_DRAUSSEN_OPTIONEN
#endif
   NOption(109, RLM_Start, 004);
end

/* ------------------------------------------------------------------ */
/* Jobs (Umsetzung 14, Phase 3 Abschnitt 5, rl_jobs.h)                 */
/* ------------------------------------------------------------------ */
procedure rlm_tyler_weg begin
   return (rl_tyler_tot or (welt[RL_W_TYLER] == RL_TYLER_BESIEGT) or (welt[RL_W_TYLER] == RL_TYLER_TOT));
end

procedure RLM_Jobs begin
   variable bit := rl_schutz_bit(h);
   Reply(1001);
   // Bestechung (5.1)
   if ((h == RL_DEN) and not rlm_tyler_weg) then begin
      if (welt[RL_W_JOBS] bwand RL_JOB_TYLER) then NOption(1003, RLM_TylerStopp, 004);
      else NOption(1002, RLM_TylerZahlen, 004);
   end
   if (h == RL_NCR) then begin
      if (welt[RL_W_JOBS] bwand RL_JOB_POLIZEI) then NOption(1005, RLM_PolizeiStopp, 004);
      else NOption(1004, RLM_PolizeiZahlen, 004);
   end
   if ((h == RL_NEW_RENO) and (welt[RL_W_GEWALT_HAUS] > 0) and rlm_bezahlbar(RL_TOTENGRAEBER_PREIS)) then
      NOption(1006, RLM_Totengraeber, 004);
   if ((h == RL_VAULT_CITY) and ((welt[RL_W_JOBS] bwand RL_JOB_MCCLURE) == 0) and rl_gecko_offen
       and rlm_bezahlbar(RL_MCCLURE_SPENDE)) then
      NOption(1007, RLM_McClure, 004);
   // Schutzgeld (5.2)
   if (bit) then begin
      if (welt[RL_W_JOBS] bwand bit) then
         NOption(1009, RLM_SchutzAus, 004);
      else if ((has_skill(dude_obj, SKILL_UNARMED_COMBAT) >= 60) or (dude_strength >= 7)
               or (has_skill(dude_obj, SKILL_SPEECH) >= 60)) then
         BOption(1008, RLM_SchutzAn, 004);
   end
   // Sabotage (5.3): einmal in vier Wochen, nur gegen einen Rivalen in dieser Stadt
   if ((rl_woche_jetzt >= welt[RL_W_JOB_WOCHE]) and rl_rivale_da(welt, h)) then begin
      if ((has_skill(dude_obj, SKILL_SNEAK) >= 60) or (rl_kampfwert >= 60)) then
         NOption(1010, RLM_Abfangen, 004);
      if ((welt[RL_W_ERPRESSUNG] == 0)
          and ((has_skill(dude_obj, SKILL_STEAL) >= 60) or (has_skill(dude_obj, SKILL_LOCKPICK) >= 60))) then
         NOption(1011, RLM_Buecher, 004);
   end
   if (welt[RL_W_ERPRESSUNG] > 0) then
      NOption(1012, RLM_BuchVerkaufen, 004);
   // Gefaelligkeiten (5.3)
   if ((h == RL_DEN) and ((welt[RL_W_JOBS] bwand RL_JOB_KLINIK) == 0) and rlm_bezahlbar(RL_KLINIK_SPENDE)) then
      GOption(1013, RLM_Klinik, 004);
   if ((h == RL_NCR) and ((welt[RL_W_JOBS] bwand RL_JOB_RANGERS) == 0) and rlm_bezahlbar(RL_RANGERS_SPENDE)
       and not rl_seelenverkaeufer) then
      GOption(1014, RLM_Rangers, 004);
   NOption(109, RLM_Draussen, 004);
end

procedure rlm_job_fertig(variable text) begin
   Reply(text);
   NOption(123, RLM_Start, 004);
end

procedure RLM_TylerZahlen begin
   call rl_job_bestechung(haus, welt, RL_JOB_TYLER, 1);
   call rlm_job_fertig(mstr(1020));
end

procedure RLM_TylerStopp begin
   call rl_job_bestechung(haus, welt, RL_JOB_TYLER, 0);
   call rlm_job_fertig(mstr(1021));
end

procedure RLM_PolizeiZahlen begin
   call rl_job_bestechung(haus, welt, RL_JOB_POLIZEI, 1);
   call rlm_job_fertig(mstr(1022));
end

procedure RLM_PolizeiStopp begin
   call rl_job_bestechung(haus, welt, RL_JOB_POLIZEI, 0);
   call rlm_job_fertig(mstr(1023));
end

// Der Totengraeber von Golgotha: Die Leichen verschwinden, die Fragen auch
procedure RLM_Totengraeber begin
   call rlm_bezahlen(RL_TOTENGRAEBER_PREIS);
   call rl_haus_plus(haus, welt[RL_W_GEWALT_HAUS] - 1, RL_F_HITZE, -15);
   welt[RL_W_GEWALT_HAUS] := 0;
   call rlm_job_fertig(mstr(1024));
end

procedure RLM_McClure begin
   call rlm_bezahlen(RL_MCCLURE_SPENDE);
   welt[RL_W_JOBS] := welt[RL_W_JOBS] bwor RL_JOB_MCCLURE;
   call rl_haus_plus(haus, RL_VAULT_CITY, RL_F_EINFLUSS, 10);
   call rlm_job_fertig(mstr(1025));
end

// In Redding nimmt Sheriff Marion das persoenlich
procedure RLM_SchutzAn begin
   welt[RL_W_JOBS] := welt[RL_W_JOBS] bwor rl_schutz_bit(h);
   if (h == RL_REDDING) then begin
      call rl_red_marion_feind(haus, welt);
      call rlm_job_fertig(mstr(1027));
   end else
      call rlm_job_fertig(mstr(1026));
end

procedure RLM_SchutzAus begin
   welt[RL_W_JOBS] := welt[RL_W_JOBS] - rl_schutz_bit(h);
   call rlm_job_fertig(mstr(1028));
end

procedure RLM_Abfangen begin
   welt[RL_W_JOB_WOCHE] := rl_woche_jetzt + RL_SABOTAGE_ABSTAND;
   call rl_haus_plus(haus, h, RL_F_EINFLUSS, 5);
   call rl_haus_plus(haus, h, RL_F_HITZE, 5);
   call rlm_job_fertig(mstr(1029));
end

procedure RLM_Buecher begin
   welt[RL_W_JOB_WOCHE] := rl_woche_jetzt + RL_SABOTAGE_ABSTAND;
   welt[RL_W_ERPRESSUNG] := 1;
   call rl_haus_plus(haus, h, RL_F_HITZE, 5);
   call rlm_job_fertig(mstr(1030));
end

procedure RLM_BuchVerkaufen begin
   welt[RL_W_ERPRESSUNG] := 0;
   item_caps_adjust(dude_obj, RL_BUECHER_PREIS);
   call rlm_job_fertig(mstr(1031));
end

procedure RLM_Klinik begin
   call rlm_bezahlen(RL_KLINIK_SPENDE);
   welt[RL_W_JOBS] := welt[RL_W_JOBS] bwor RL_JOB_KLINIK;
   rl_karma(10);
   call rl_haus_plus(haus, RL_DEN, RL_F_EINFLUSS, 5);
   call rlm_job_fertig(mstr(1032));
end

procedure RLM_Rangers begin
   call rlm_bezahlen(RL_RANGERS_SPENDE);
   welt[RL_W_JOBS] := welt[RL_W_JOBS] bwor RL_JOB_RANGERS;
   call rl_haus_plus(haus, RL_NCR, RL_F_EINFLUSS, 5);
   call rl_haus_plus(haus, RL_NCR, RL_F_HITZE, -10);
   call rlm_job_fertig(mstr(1033));
end

/* ------------------------------------------------------------------ */
/* Die Laeuferroute durch Broken Hills (Phase 3, Abschnitt 6)          */
/* ------------------------------------------------------------------ */
// Nur wo Laeufer durch Broken Hills gehen: ab dem Hauptquartier, in NR, Redding, VC, NCR
procedure rlm_laeufer_da begin
   if (haus[rl_idx(RL_NEW_RENO, RL_F_BESITZ)] == 0) then return 0;
   return ((h == RL_NEW_RENO) or (h == RL_REDDING) or (h == RL_VAULT_CITY) or (h == RL_NCR));
end

procedure RLM_Laeufer begin
   variable m := welt[RL_W_MARCUS], text := mstr(1041 + welt[RL_W_MARCUS]);
   variable besucht := ((welt[RL_W_JOBS] bwand RL_JOB_BH_BESUCHT) != 0);
   variable geld := ((welt[RL_W_JOBS] bwand RL_JOB_MARCUS_GELD) != 0);
   if ((not besucht) and (m < RL_MARCUS_ESKORTE)) then text := text + " " + mstr(1045);
   Reply(text);
   if (besucht and (m == RL_MARCUS_KEIN)) then begin
      // Dem Seelenverkaeufer hoert Marcus nicht zu; dem anstaendigen Haus eher (Phase 6, 3.1)
      if ((has_skill(dude_obj, SKILL_SPEECH) >= 70 + 10 * geld - rl_titel_bonus) and not rl_seelenverkaeufer) then
         GOption(1046, RLM_MarcusReden, 004);
      if (not geld) then
         BOption(1047, RLM_MarcusGeld, 004);
   end
   if (besucht and (m <= RL_MARCUS_RELAIS) and (global_var(GVAR_PLAYER_REPUTATION) >= RL_KARMA_GUT)
       and (rl_anstaendige_haeuser(haus) >= 3)) then
      GOption(1048, RLM_MarcusAnstand, 004);
   NOption(109, RLM_Draussen, 004);
end

procedure RLM_MarcusReden begin
   welt[RL_W_MARCUS] := RL_MARCUS_RELAIS;
   call rlm_job_fertig(mstr(1049));
end

procedure RLM_MarcusGeld begin
   welt[RL_W_JOBS] := welt[RL_W_JOBS] bwor RL_JOB_MARCUS_GELD;
   call rlm_job_fertig(mstr(1050));
end

procedure RLM_MarcusAnstand begin
   welt[RL_W_MARCUS] := RL_MARCUS_ESKORTE;
   call rlm_job_fertig(mstr(1051));
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
/* Das Krisenmenue (Phase 4, Abschnitte 4.2 und 4.3; Umsetzung 15): je Art die
   Loesungswege. Die Beschreibung der Kern-Krisen spricht die Madame selbst
   (180 + Art), die weiteren erzaehlt _rl_krisen.inc (1100 + Art). */
procedure RLM_Krise begin
   variable k := haus[rl_idx(h, RL_F_KRISE)], kampf := rl_kampfwert;
   if (k == RL_EV_STOFF) then begin
      Reply(160);
      if (has_skill(dude_obj, SKILL_DOCTOR) >= 60) then
         GOption(161, RLM_StoffDoctor, 004);
      if (haus[rl_idx(h, RL_F_MODULE)] bwand RL_MOD_KRANKENSTUBE) then
         GOption(1140, RLM_StoffHeilen, 004);
      else if (dude_caps >= 200) then
         NOption(162, RLM_StoffBezahlen, 004);
      if (haus[rl_idx(RL_REDDING, RL_F_BESITZ)] and rl_red_entzug(haus)) then
         GOption(1141, RLM_StoffHeilen, 004);
      if (obj_is_carrying_obj_pid(dude_obj, PID_JET_ANTIDOTE)) then
         GOption(1142, RLM_StoffHeilen, 004);
      BOption(163, RLM_StoffLeine, 004);
      BOption(164, RLM_StoffRauswurf, 004);
   end else if (k == RL_EV_SOLDATEN) then begin
      Reply(mstr(170) + " " + mstr(181));
      if (rlm_bezahlbar(RL_SOLDATEN_PREIS)) then NOption(1130, RLM_SoldatenZahlen, 004);
      if (rl_bar2_hier(haus, h) and (has_skill(dude_obj, SKILL_BARTER) >= 50)) then
         NOption(1131, RLM_SoldatenTrinken, 004);
      if (has_skill(dude_obj, SKILL_SPEECH) >= 70) then GOption(1135, RLM_SoldatenReden, 004);
      if ((has_skill(dude_obj, SKILL_SPEECH) >= 90) or (dude_charisma >= 8)) then
         GOption(1136, RLM_SoldatenWerben, 004);
      if ((h == rl_talus_haus(welt)) or (kampf >= 80)) then BOption(1137, RLM_SoldatenKampf, 004);
   end else if ((k == RL_EV_RAZZIA) and rl_razzia_stadt(h)) then begin
      // Die angekuendigte Razzia: eine Woche, um die Beweise verschwinden zu lassen
      Reply(1120 + h);
      if ((h == RL_DEN) and (rl_razzia_beweise(haus, welt, h) bwand RL_BEWEIS_FLUECHTLINGE)
          and ((has_skill(dude_obj, SKILL_SNEAK) >= 60) or (has_skill(dude_obj, SKILL_OUTDOORSMAN) >= 60))) then
         GOption(1125, RLM_RazziaVerstecken, 004);
      if ((h == RL_NEW_RENO) and ((welt[RL_W_RAZZIA_VERSTECKT] bwand rl_bit(h)) == 0)) then begin
         if (rlm_bezahlbar(200)) then NOption(1126, RLM_RazziaWachen, 004);
         if (kampf >= 60) then BOption(1127, RLM_RazziaSelbst, 004);
      end
      if ((h == RL_REDDING) and (haus[rl_idx(h, RL_F_MODULE)] bwand RL_MOD_WAAGE_GEZINKT)) then
         GOption(1128, RLM_RazziaWaage, 004);
      if ((h == RL_REDDING) and (welt[RL_W_JOBS] bwand RL_JOB_SCHUTZ_RED)) then
         GOption(1129, RLM_RazziaSchutzgeld, 004);
      if ((h == RL_NCR) and (rl_razzia_beweise(haus, welt, h) bwand RL_BEWEIS_ZWANG)
          and (has_skill(dude_obj, SKILL_SNEAK) >= 60)) then
         GOption(1138, RLM_RazziaVerstecken, 004);
   end else if (k == RL_EV_FREIER) then begin
      Reply(mstr(170) + " " + mstr(184));
      if (has_skill(dude_obj, SKILL_UNARMED_COMBAT) >= 50) then BOption(1150, RLM_FreierSelbst, 004);
      NOption(1151, RLM_FreierVerbot, 004);
   end else if (k == RL_EV_SEUCHE) then begin
      Reply(mstr(170) + " " + mstr(185));
      if (has_skill(dude_obj, SKILL_DOCTOR) >= 60) then GOption(1152, RLM_SeucheDoctor, 004);
      if (dude_caps >= 300) then NOption(1153, RLM_SeucheArzt, 004);
      NOption(1154, RLM_SeucheSchliessen, 004);
   end else if (k == RL_EV_KASSE) then begin
      Reply(mstr(170) + " " + mstr(186));
      if (dude_iq >= 7) then GOption(1155, RLM_KasseBuecher, 004);
      if (has_skill(dude_obj, SKILL_SNEAK) >= 50) then NOption(1156, RLM_KasseBeschatten, 004);
      NOption(1157, RLM_KasseLassen, 004);
   end else if (k == RL_EV_FLUCHT) then begin
      Reply(mstr(170) + " " + mstr(187));
      NOption(1158, RLM_FluchtLassen, 004);
      if ((has_skill(dude_obj, SKILL_OUTDOORSMAN) >= 60) or (kampf >= 60)) then
         BOption(1159, RLM_FluchtHolen, 004);
   end else if (k == RL_EV_TOD) then begin
      Reply(1109);
      if (rlm_bezahlbar(RL_BEERDIGUNG_PREIS)) then GOption(1160, RLM_TodBeerdigen, 004);
      BOption(1161, RLM_TodSchweigen, 004);
      if (welt[RL_W_TOD_GEWALT] bwand rl_bit(h)) then NOption(1162, RLM_TodRache, 004);
   end else if (k == RL_EV_STAMMKUNDE) then begin
      Reply(1110);
      NOption(1163, RLM_GeheimnisAkte, 004);
      BOption(1164, RLM_GeheimnisVerkaufen, 004);
      GOption(1165, RLM_GeheimnisVergessen, 004);
   end else if (k == RL_EV_ABWERBUNG) then begin
      Reply(1112);
      if ((has_skill(dude_obj, SKILL_BARTER) >= 60) and rlm_bezahlbar(RL_ABWERBUNG_GEGENANGEBOT)) then
         NOption(1166, RLM_AbwerbungHalten, 004);
      NOption(1167, RLM_AbwerbungLassen, 004);
   end else if (k == RL_EV_UEBERFALL) then begin
      Reply(mstr(1113) + welt[RL_W_UEBERFALL_BETRAG] + mstr(1119));
      if (has_skill(dude_obj, SKILL_OUTDOORSMAN) >= 60) then NOption(1168, RLM_UeberfallSpur, 004);
      NOption(1169, RLM_UeberfallAbschreiben, 004);
   end else if (k == RL_EV_GHUL) then begin
      Reply(1114);
      if ((has_skill(dude_obj, SKILL_UNARMED_COMBAT) >= 60) or (kampf >= 60)) then
         NOption(1170, RLM_GhulRaus, 004);
      if (has_skill(dude_obj, SKILL_SPEECH) >= 60) then GOption(1171, RLM_GhulReden, 004);
      BOption(1172, RLM_GhulLassen, 004);
   end else if (k == RL_EV_RICHTER) then begin
      Reply(1115);
      GOption(1173, RLM_RichterHeilen, 004);
      NOption(1174, RLM_RichterBlossstellen, 004);
      BOption(1175, RLM_RichterGift, 004);
   end else if (k == RL_EV_BUNKER) then begin
      Reply(1116);
      NOption(1176, RLM_BunkerAusliefern, 004);
      if (has_skill(dude_obj, SKILL_SNEAK) >= 60) then NOption(1177, RLM_BunkerVerstecken, 004);
      if (kampf >= 80) then BOption(1178, RLM_BunkerWeg, 004);
   end else begin
      Reply(mstr(170) + " " + mstr(180 + rl_min(8, k)));
      if (dude_caps >= 300) then
         NOption(171, RLM_KriseGeld, 004);
      // Metzgers Vergeltung im stillen Krieg (Phase 4, Abschnitt 4.3)
      if (k == RL_EV_VERGELTUNG) then begin
         if (rl_max(rl_max(has_skill(dude_obj, SKILL_SMALL_GUNS), has_skill(dude_obj, SKILL_MELEE)),
                    has_skill(dude_obj, SKILL_UNARMED_COMBAT)) >= 60) then
            NOption(174, RLM_VergeltungKampf, 004);
         if ((welt[RL_W_RANGERS] >= RL_RANGERS_KONTAKT) and (welt[RL_W_RANGERS] != RL_RANGERS_FEIND)
             and not rl_seelenverkaeufer) then
            GOption(175, RLM_VergeltungRangers, 004);
      end
   end
   NOption(172, RLM_Ende, 004);
end

procedure rlm_krise_fertig(variable text) begin
   call rlm_krise_loesen;
   Reply(text);
   NOption(123, RLM_Start, 004);
end

// Soldaten ohne Krieg (Phase 4, 4.2)
procedure RLM_SoldatenZahlen begin
   call rlm_bezahlen(RL_SOLDATEN_PREIS);
   if (random(1, 100) <= 50) then begin                 // sie kommen vielleicht wieder
      welt[RL_W_SOLDATEN_HAUS] := h + 1;
      welt[RL_W_SOLDATEN_WOCHE] := rl_woche_jetzt + RL_SOLDATEN_WIEDER;
   end
   call rlm_krise_fertig(mstr(1180));
end

procedure RLM_SoldatenTrinken begin
   Reply(1132);
   BOption(1133, RLM_SoldatenRuestung, 004);
   NOption(1134, RLM_SoldatenLassen, 004);
end

procedure RLM_SoldatenRuestung begin
   variable ruestung := create_object(PID_POWERED_ARMOR, 0, 0);
   add_obj_to_inven(dude_obj, ruestung);
   rl_karma(-5);
   call rlm_krise_fertig(mstr(1181));
end

procedure RLM_SoldatenLassen begin
   call rlm_krise_fertig(mstr(1182));
end

procedure RLM_SoldatenReden begin
   call rlm_krise_fertig(mstr(1183));
end

// Ein Deserteur bleibt als Rausschmeisser; die Brotherhood sucht ihn
procedure RLM_SoldatenWerben begin
   haus[rl_idx(h, RL_F_SICHERHEIT)] := haus[rl_idx(h, RL_F_SICHERHEIT)] + RL_DESERTEUR_SICHERHEIT;
   welt[RL_W_DESERTEUR] := h + 1;
   welt[RL_W_DESERTEUR_WOCHE] := rl_woche_jetzt;
   call rlm_krise_fertig(mstr(1184));
end

// Kampf: Die Teile der Ruestungen bringen Geld; die Leichen bringen Hitze (Totengraeber)
procedure RLM_SoldatenKampf begin
   item_caps_adjust(dude_obj, 300);
   call rl_haus_plus(haus, h, RL_F_HITZE, 20);
   welt[RL_W_GEWALT_HAUS] := h + 1;
   call rlm_krise_fertig(mstr(1185));
end

// Der Stoff: behandeln mit Krankenstube, Entzugsstube oder Antidot
procedure RLM_StoffHeilen begin
   haus[rl_idx(h, RL_F_MORAL)] := rl_min(100, haus[rl_idx(h, RL_F_MORAL)] + 5);
   call rlm_krise_fertig(mstr(1186));
end

// Die angekuendigte Razzia: Beweise verschwinden lassen
procedure RLM_RazziaVerstecken begin
   welt[RL_W_RAZZIA_VERSTECKT] := welt[RL_W_RAZZIA_VERSTECKT] bwor rl_bit(h);
   Reply(1187);
   NOption(123, RLM_Start, 004);
end

procedure RLM_RazziaWachen begin
   call rlm_bezahlen(200);
   welt[RL_W_RAZZIA_VERSTECKT] := welt[RL_W_RAZZIA_VERSTECKT] bwor rl_bit(h);
   Reply(1188);
   NOption(123, RLM_Start, 004);
end

procedure RLM_RazziaSelbst begin
   welt[RL_W_RAZZIA_VERSTECKT] := welt[RL_W_RAZZIA_VERSTECKT] bwor rl_bit(h);
   call rl_haus_plus(haus, h, RL_F_HITZE, 10);
   call rl_haus_plus(haus, h, RL_F_EINFLUSS, 5);
   Reply(1189);
   NOption(123, RLM_Start, 004);
end

procedure RLM_RazziaWaage begin
   haus[rl_idx(h, RL_F_MODULE)]   := haus[rl_idx(h, RL_F_MODULE)] - RL_MOD_WAAGE_GEZINKT;
   haus[rl_idx(h, RL_F_PREISMOD)] := haus[rl_idx(h, RL_F_PREISMOD)] - RL_WAAGE_PREIS;
   Reply(1190);
   NOption(123, RLM_Start, 004);
end

procedure RLM_RazziaSchutzgeld begin
   welt[RL_W_JOBS] := welt[RL_W_JOBS] - RL_JOB_SCHUTZ_RED;
   Reply(1191);
   NOption(123, RLM_Start, 004);
end

// Gewalttaetiger Freier (Phase 4, 4.3)
procedure RLM_FreierSelbst begin
   call rl_haus_plus(haus, h, RL_F_HITZE, 5);
   call rlm_krise_fertig(mstr(1192));
end

procedure RLM_FreierVerbot begin
   call rl_haus_plus(haus, h, RL_F_RUF, -2);
   call rlm_krise_fertig(mstr(1193));
end

// Seuche
procedure RLM_SeucheDoctor begin
   call rlm_krise_fertig(mstr(1194));
end

procedure RLM_SeucheArzt begin
   item_caps_adjust(dude_obj, -300);
   call rlm_krise_fertig(mstr(1195));
end

procedure RLM_SeucheSchliessen begin
   haus[rl_idx(h, RL_F_GESCHLOSSEN)] := rl_max(haus[rl_idx(h, RL_F_GESCHLOSSEN)], 2);
   call rlm_krise_fertig(mstr(1196));
end

// Griff in die Kasse
procedure RLM_KasseBuecher begin
   haus[rl_idx(h, RL_F_KASSE)] := haus[rl_idx(h, RL_F_KASSE)] + 100;
   call rlm_krise_fertig(mstr(1197));
end

procedure RLM_KasseBeschatten begin
   haus[rl_idx(h, RL_F_KASSE)] := haus[rl_idx(h, RL_F_KASSE)] + 100;
   call rl_personal_verlust(haus, h, RL_VERLUST_ABGANG);
   call rlm_krise_fertig(mstr(1198));
end

procedure RLM_KasseLassen begin
   call rlm_krise_fertig(mstr(1199));
end

// Flucht und Kuendigung
procedure RLM_FluchtLassen begin
   call rl_personal_verlust(haus, h, RL_VERLUST_FLUCHT);
   call rlm_krise_fertig(mstr(1200));
end

procedure RLM_FluchtHolen begin
   if (haus[rl_idx(h, RL_F_ZWANG)] > 0) then rl_karma(-10);
   call rlm_krise_fertig(mstr(1201));
end

// Tod im Haus
procedure RLM_TodBeerdigen begin
   call rlm_bezahlen(RL_BEERDIGUNG_PREIS);
   call rl_haus_plus(haus, h, RL_F_MORAL, 5);
   call rlm_krise_fertig(mstr(1202));
end

procedure RLM_TodSchweigen begin
   call rl_haus_plus(haus, h, RL_F_MORAL, -15);
   call rlm_krise_fertig(mstr(1203));
end

procedure RLM_TodRache begin
   call rl_haus_plus(haus, h, RL_F_HITZE, 10);
   call rl_haus_plus(haus, h, RL_F_MORAL, 5);
   call rlm_krise_fertig(mstr(1204));
end

// Stammkunde mit Geheimnis
procedure RLM_GeheimnisAkte begin
   call rl_haus_plus(haus, h, RL_F_EINFLUSS, 5);
   call rlm_krise_fertig(mstr(1205));
end

procedure RLM_GeheimnisVerkaufen begin
   item_caps_adjust(dude_obj, RL_GEHEIMNIS_PREIS);
   rl_karma(-5);
   call rlm_krise_fertig(mstr(1206));
end

procedure RLM_GeheimnisVergessen begin
   call rlm_krise_fertig(mstr(1207));
end

// Abwerbung durch Kitty
procedure RLM_AbwerbungHalten begin
   call rlm_bezahlen(RL_ABWERBUNG_GEGENANGEBOT);
   call rlm_krise_fertig(mstr(1208));
end

procedure RLM_AbwerbungLassen begin
   call rl_personal_verlust(haus, h, RL_VERLUST_ABGANG);
   call rlm_krise_fertig(mstr(1209));
end

// Ueberfall auf die Laeufer
procedure RLM_UeberfallSpur begin
   welt[RL_W_HQ_KASSE] := welt[RL_W_HQ_KASSE] + welt[RL_W_UEBERFALL_BETRAG];
   welt[RL_W_UEBERFALL_BETRAG] := 0;
   call rlm_krise_fertig(mstr(1210));
end

procedure RLM_UeberfallAbschreiben begin
   welt[RL_W_UEBERFALL_BETRAG] := 0;
   call rlm_krise_fertig(mstr(1211));
end

// Ghul im Haus (Vesper)
procedure RLM_GhulRaus begin
   welt[RL_W_VESPER_LOYAL] := rl_min(100, welt[RL_W_VESPER_LOYAL] + 5);
   call rlm_krise_fertig(mstr(1212));
end

procedure RLM_GhulReden begin
   call rlm_krise_fertig(mstr(1213));
end

procedure RLM_GhulLassen begin
   welt[RL_W_VESPER_LOYAL] := welt[RL_W_VESPER_LOYAL] - 20;
   call rlm_krise_fertig(mstr(1214));
end

// Der Richter (Abigail)
procedure RLM_RichterHeilen begin
   rl_karma(5);
   welt[RL_W_ABIGAIL_LOYAL] := rl_min(100, welt[RL_W_ABIGAIL_LOYAL] + 5);
   call rlm_krise_fertig(mstr(1215));
end

procedure RLM_RichterBlossstellen begin
   call rl_haus_plus(haus, h, RL_F_HITZE, 10);
   welt[RL_W_ABIGAIL_LOYAL] := rl_min(100, welt[RL_W_ABIGAIL_LOYAL] + 10);
   call rlm_krise_fertig(mstr(1216));
end

procedure RLM_RichterGift begin
   rl_karma(-20);
   welt[RL_W_ABIGAIL_LOYAL] := rl_min(100, welt[RL_W_ABIGAIL_LOYAL] + 10);
   call rl_haus_plus(haus, h, RL_F_HITZE, 15);
   welt[RL_W_GEWALT_HAUS] := h + 1;
   call rlm_krise_fertig(mstr(1217));
end

// Besuch aus dem Bunker (der Deserteur)
procedure RLM_BunkerAusliefern begin
   rl_karma(5);
   haus[rl_idx(h, RL_F_SICHERHEIT)] := rl_max(0, haus[rl_idx(h, RL_F_SICHERHEIT)] - RL_DESERTEUR_SICHERHEIT);
   welt[RL_W_DESERTEUR] := 0;
   call rlm_krise_fertig(mstr(1218));
end

procedure RLM_BunkerVerstecken begin
   welt[RL_W_DESERTEUR_WOCHE] := rl_woche_jetzt;
   call rlm_krise_fertig(mstr(1219));
end

procedure RLM_BunkerWeg begin
   welt[RL_W_DESERTEUR_WOCHE] := rl_woche_jetzt;
   call rl_haus_plus(haus, h, RL_F_HITZE, 20);
   call rl_haus_plus(haus, h, RL_F_EINFLUSS, 5);
   call rlm_krise_fertig(mstr(1220));
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
/* Die anderen Staedte (Umsetzung 6): wo die weiteren Haeuser liegen   */
/* ------------------------------------------------------------------ */
procedure RLM_Staedte begin
   Reply(621);
   NOption(622, RLM_StadtNR, 004);
   NOption(623, RLM_StadtRed, 004);
   NOption(624, RLM_StadtVC, 004);
   NOption(625, RLM_StadtNCR, 004);
   NOption(626, RLM_StadtSF, 004);
   NOption(627, RLM_Start, 004);
end

procedure rlm_stadt_erzaehlt(variable stadt) begin
   welt[RL_W_STAEDTE_ERZAEHLT] := welt[RL_W_STAEDTE_ERZAEHLT] bwor rl_bit(stadt);
   Reply(630 + stadt - 1);
   NOption(628, RLM_Staedte, 004);
   NOption(627, RLM_Start, 004);
end

procedure RLM_StadtNR begin
   call rlm_stadt_erzaehlt(RL_NEW_RENO);
end

procedure RLM_StadtRed begin
   call rlm_stadt_erzaehlt(RL_REDDING);
end

procedure RLM_StadtVC begin
   call rlm_stadt_erzaehlt(RL_VAULT_CITY);
end

procedure RLM_StadtNCR begin
   call rlm_stadt_erzaehlt(RL_NCR);
end

procedure RLM_StadtSF begin
   call rlm_stadt_erzaehlt(RL_SAN_FRAN);
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

/* ------------------------------------------------------------------ */
/* Talente (Umsetzung 13, Phase 4 Abschnitt 3, rl_talente.h)           */
/* ------------------------------------------------------------------ */
procedure rlm_talente_da begin
   if (welt[RL_W_JULIAN] == RL_TS_KRITISCH) then return 1;
   if (h == RL_NEW_RENO) then begin
      if ((welt[RL_W_VESPER_STAND] == RL_TS_OFFEN) and not rl_seelenverkaeufer) then return 1;
      if ((welt[RL_W_VESPER_STAND] == RL_TS_DA) and (welt[RL_W_VESPER_FRAGE] == 0)) then return 1;
      if ((welt[RL_W_JULIAN] == RL_TS_OFFEN) or (welt[RL_W_JULIAN] == RL_TS_AUFTRAG)) then return 1;
   end
   if ((h == RL_VAULT_CITY) and (welt[RL_W_ABIGAIL] == RL_TS_OFFEN)) then return 1;
   if ((h != RL_VAULT_CITY) and (welt[RL_W_TALUS] == RL_TS_OFFEN) and not rl_seelenverkaeufer) then return 1;
   if ((welt[RL_W_TALUS] == RL_TS_DA) and (welt[RL_W_TALUS_LOYAL] < 100) and (dude_iq >= 7)) then return 1;
   return 0;
end

procedure RLM_Talente begin
   Reply(951);
   if (welt[RL_W_JULIAN] == RL_TS_KRITISCH) then NOption(996, RLM_JulianRetten, 004);
   if (h == RL_NEW_RENO) then begin
      if ((welt[RL_W_VESPER_STAND] == RL_TS_OFFEN) and not rl_seelenverkaeufer) then NOption(952, RLM_Vesper, 004);
      if ((welt[RL_W_VESPER_STAND] == RL_TS_DA) and (welt[RL_W_VESPER_FRAGE] == 0)) then NOption(953, RLM_VesperFrage, 004);
      if (welt[RL_W_JULIAN] == RL_TS_OFFEN) then NOption(954, RLM_Julian, 004);
      if (welt[RL_W_JULIAN] == RL_TS_AUFTRAG) then NOption(955, RLM_JulianEntzug, 004);
   end
   if ((h == RL_VAULT_CITY) and (welt[RL_W_ABIGAIL] == RL_TS_OFFEN)) then NOption(956, RLM_Abigail, 004);
   if ((h != RL_VAULT_CITY) and (welt[RL_W_TALUS] == RL_TS_OFFEN) and not rl_seelenverkaeufer) then
      NOption(957, RLM_Talus, 004);
   if ((welt[RL_W_TALUS] == RL_TS_DA) and (welt[RL_W_TALUS_LOYAL] < 100) and (dude_iq >= 7)) then
      GOption(958, RLM_TalusLesen, 004);
   NOption(959, RLM_Draussen, 004);
end

// Vesper: Geleitschutz, Umweg oder Passierschein
procedure RLM_Vesper begin
   Reply(960);
   if (rl_kampfwert >= 60) then NOption(961, RLM_VesperAuftrag, 004);
   if (has_skill(dude_obj, SKILL_OUTDOORSMAN) >= 60) then NOption(962, RLM_VesperAuftrag, 004);
   if (has_skill(dude_obj, SKILL_SCIENCE) >= 60) then NOption(963, RLM_VesperAuftrag, 004);
   NOption(959, RLM_Talente, 004);
end

procedure RLM_VesperAuftrag begin
   welt[RL_W_VESPER_STAND] := RL_TS_AUFTRAG;
   welt[RL_W_VESPER_LOYAL] := 80;
   Reply(964);
   NOption(123, RLM_Start, 004);
end

procedure RLM_VesperFrage begin
   Reply(965);
   if (has_skill(dude_obj, SKILL_SPEECH) >= 40) then GOption(966, RLM_VesperEhrlich, 004);
   BOption(967, RLM_VesperLuege, 004);
end

procedure RLM_VesperEhrlich begin
   welt[RL_W_VESPER_FRAGE] := 1;
   Reply(968);
   NOption(123, RLM_Start, 004);
end

// Die Luege fliegt auf, sobald sie die Zimmer sieht (Loyalitaet -20)
procedure RLM_VesperLuege begin
   welt[RL_W_VESPER_FRAGE] := 1;
   welt[RL_W_VESPER_LOYAL] := welt[RL_W_VESPER_LOYAL] - 20;
   Reply(969);
   NOption(123, RLM_Start, 004);
end

// Julian Rook: den Vertrag loesen
procedure RLM_Julian begin
   Reply(970);
   if ((has_skill(dude_obj, SKILL_BARTER) >= 60) and rlm_bezahlbar(RL_JULIAN_PREIS)) then
      NOption(971, RLM_JulianBarter, 004);
   if (has_skill(dude_obj, SKILL_GAMBLING) >= 70) then NOption(972, RLM_JulianGambling, 004);
   if (global_var(GVAR_NEW_RENO_PORN_STAR) and (has_skill(dude_obj, SKILL_SPEECH) >= 50)) then
      GOption(973, RLM_JulianStar, 004);
   BOption(974, RLM_JulianTyrann, 004);
   NOption(959, RLM_Talente, 004);
end

procedure rlm_julian_frei(variable weg, variable text) begin
   welt[RL_W_JULIAN_WEG] := weg;
   welt[RL_W_JULIAN] := RL_TS_AUFTRAG;
   welt[RL_W_JULIAN_LOYAL] := 70;
   Reply(text);
   NOption(123, RLM_Start, 004);
end

procedure RLM_JulianBarter begin
   call rlm_bezahlen(RL_JULIAN_PREIS);
   call rlm_julian_frei(RL_JULIAN_BARTER, mstr(975));
end

procedure RLM_JulianGambling begin
   call rlm_julian_frei(RL_JULIAN_GAMBLING, mstr(975));
end

procedure RLM_JulianStar begin
   call rlm_julian_frei(RL_JULIAN_PORNOSTAR, mstr(975));
end

// Tyrannen-Variante: Vertrag und Stoff uebernommen. Er bleibt am Jet, Loyalitaet 30
procedure RLM_JulianTyrann begin
   rl_karma(-10);
   welt[RL_W_JULIAN_WEG] := RL_JULIAN_TYRANN;
   welt[RL_W_JULIAN] := RL_TS_DA;
   welt[RL_W_JULIAN_LOYAL] := 30;
   Reply(976);
   NOption(123, RLM_Start, 004);
end

// Vom Jet holen: Doctor 60, Myrons Antidot oder die Entzugsstube in Redding
procedure RLM_JulianEntzug begin
   Reply(977);
   if (has_skill(dude_obj, SKILL_DOCTOR) >= 60) then GOption(978, RLM_JulianClean, 004);
   if (obj_is_carrying_obj_pid(dude_obj, PID_JET_ANTIDOTE)) then GOption(979, RLM_JulianClean, 004);
   if (haus[rl_idx(RL_REDDING, RL_F_BESITZ)] and rl_red_entzug(haus)) then GOption(980, RLM_JulianClean, 004);
   NOption(959, RLM_Talente, 004);
end

procedure RLM_JulianClean begin
   welt[RL_W_JULIAN] := RL_TS_DA;
   welt[RL_W_JULIAN_LOYAL] := rl_min(100, welt[RL_W_JULIAN_LOYAL] + 10);
   Reply(981);
   NOption(123, RLM_Start, 004);
end

// Julian liegt im Sterben: eine Woche Zeit (Phase 4, Leitlinie 5)
procedure RLM_JulianRetten begin
   Reply(997);
   if (has_skill(dude_obj, SKILL_DOCTOR) >= 60) then GOption(998, RLM_JulianGerettet, 004);
   if (obj_is_carrying_obj_pid(dude_obj, PID_JET_ANTIDOTE)) then GOption(979, RLM_JulianGerettet, 004);
   NOption(959, RLM_Talente, 004);
end

procedure RLM_JulianGerettet begin
   welt[RL_W_JULIAN] := RL_TS_DA;
   welt[RL_W_JULIAN_LOYAL] := welt[RL_W_JULIAN_LOYAL] - 20;
   Reply(999);
   NOption(123, RLM_Start, 004);
end

// Abigail Kessler: Buergerschaft, Akte vernichten oder erpressen
procedure RLM_Abigail begin
   Reply(982);
   if (haus[rl_idx(RL_VAULT_CITY, RL_F_EINFLUSS)] >= 60) then
      GOption(983, RLM_AbigailBuergerin, 004);
   else if (has_skill(dude_obj, SKILL_SPEECH) >= 70) then
      GOption(984, RLM_AbigailBuergerin, 004);
   if ((has_skill(dude_obj, SKILL_SNEAK) >= 60) and (has_skill(dude_obj, SKILL_LOCKPICK) >= 60)) then
      NOption(985, RLM_AbigailAkte, 004);
   BOption(986, RLM_AbigailErpressen, 004);
   NOption(959, RLM_Talente, 004);
end

procedure rlm_abigail_da(variable weg, variable loyal, variable text) begin
   welt[RL_W_ABIGAIL] := RL_TS_DA;
   welt[RL_W_ABIGAIL_WEG] := weg;
   welt[RL_W_ABIGAIL_LOYAL] := loyal;
   call rl_talent_anwenden(haus, welt, RL_TALENT_ABIGAIL, 1);
   Reply(text);
   NOption(123, RLM_Start, 004);
end

procedure RLM_AbigailBuergerin begin
   call rlm_abigail_da(RL_ABIGAIL_BUERGERIN, 80, mstr(987));
end

procedure RLM_AbigailAkte begin
   call rl_haus_plus(haus, RL_VAULT_CITY, RL_F_HITZE, 10);
   call rlm_abigail_da(RL_ABIGAIL_AKTE, 70, mstr(988));
end

procedure RLM_AbigailErpressen begin
   rl_karma(-10);
   call rlm_abigail_da(RL_ABIGAIL_ERPRESST, 20, mstr(989));
end

// Talus: die Wahrheit finden (Vanilla) oder ausbrechen lassen. Er kommt in dieses Haus.
procedure RLM_Talus begin
   Reply(990);
   NOption(991, RLM_TalusWahrheit, 004);
   if ((has_skill(dude_obj, SKILL_LOCKPICK) >= 80) or (rl_kampfwert >= 80)) then
      BOption(992, RLM_TalusAusbruch, 004);
   NOption(959, RLM_Talente, 004);
end

procedure RLM_TalusWahrheit begin
   welt[RL_W_TALUS] := RL_TS_AUFTRAG;
   welt[RL_W_TALUS_WEG] := RL_TALUS_WAHRHEIT;
   welt[RL_W_TALUS_HAUS] := h + 1;
   welt[RL_W_TALUS_LOYAL] := 90;
   Reply(993);
   NOption(123, RLM_Start, 004);
end

procedure RLM_TalusAusbruch begin
   welt[RL_W_TALUS] := RL_TS_AUFTRAG;
   welt[RL_W_TALUS_WEG] := RL_TALUS_AUSBRUCH;
   welt[RL_W_TALUS_HAUS] := h + 1;
   welt[RL_W_TALUS_LOYAL] := 60;
   Reply(994);
   NOption(123, RLM_Start, 004);
end

procedure RLM_TalusLesen begin
   welt[RL_W_TALUS_LOYAL] := 100;
   Reply(995);
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
   // Die ehrliche und die gezinkte Waage schliessen sich aus (Phase 2)
   if ((id == RL_M_RED_GOLDWAAGE) and ((haus[rl_idx(h, RL_F_MODULE)] bwand RL_MOD_WAAGE_GEZINKT)
       or (haus[rl_idx(h, RL_F_BAU_ID)] == RL_SONDER_BASIS + RL_SM_WAAGE + 1))) then return 0;
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
   if (sm == RL_SM_JET_THEKE) then begin
      // Nur mit Mordino-Pate oder Jet-Vertrag, nie unter Wrights Segen (Phase 2)
      if (h != RL_NEW_RENO) then return 0;
      if (welt[RL_W_NR_SEGEN] == RL_SEGEN_WRIGHT) then return 0;
      return ((welt[RL_W_NR_SEGEN] == RL_SEGEN_MORDINO) or welt[RL_W_JET_VERTRAG]);
   end
   if (sm == RL_SM_WAAGE) then
      return ((h == RL_REDDING) and not rlm_gekauft(RL_M_RED_GOLDWAAGE));
   if (sm == RL_SM_AKTE) then
      return (h == RL_VAULT_CITY);
   if (sm == RL_SM_REGISTRATUR) then
      return (h == RL_NCR);
   if (sm == RL_SM_SCHMUGGEL) then
      return ((h == RL_SAN_FRAN) and welt[RL_W_SF_LAGER]);
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
