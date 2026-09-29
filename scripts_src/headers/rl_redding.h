/*
   rl_redding.h - Redding: Die Schlacke (Phase 2 Abschnitt 2.3, Phase 3
   Abschnitte 2.3 und 4.2, Phase 4 Abschnitt 4.2). Umsetzung 8.

   "Ascortis Lizenz": Ascortis Schreiber sitzt in der leeren Schlacke und
   verkauft die Lizenz. Vier Wege:
     Paket         1.000 $ (Barter 60: 600 $), danach 75 $/Woche
     Aufschlag     Speech 70: kein Paketpreis, dafuer 125 $/Woche
     Blossstellen  Steal 60 oder Lockpick 60 (Ascortis Kassenbuch) und
                   Speech 60 bei Marion: Marion wird Schutzherr (Sicherheit
                   +10), kein Schmiergeld, Ascorti wird Feind
     Einschuechtern Unarmed 60 oder ST 7: kein Paketpreis, kein Schmiergeld,
                   H +20, Marion wird wachsam
   Mit der Lizenz gehoert die Schlacke dem Spieler (E Redding mindestens 20).

   Die gezinkte Waage (Sondermodul): Preis +15 %, Karma -2/Woche, H +10.
   Jede Woche kann Marion sie finden: Revolte der Kumpel, 3 Wochen
   geschlossen, Ascorti verlangt das Doppelte (Phase 4, Razzia in Redding).

   Der Malamute Saloon (Phase 3, 4.2) wird ueber Nell geloest: Beteiligung,
   Preiskrieg, Sabotage oder Uebernahme.

   Wird am Ende von rotlicht.h eingebunden.
*/
#ifndef RL_REDDING_H
#define RL_REDDING_H

#define RL_LIZENZ_KEINE             (0)
#define RL_LIZENZ_PAKET             (1)
#define RL_LIZENZ_AUFSCHLAG         (2)
#define RL_LIZENZ_MARION            (3)
#define RL_LIZENZ_DROHUNG           (4)

#define RL_MARION_NEUTRAL           (0)
#define RL_MARION_SCHUTZ            (1)     // Schutzherr: Sicherheit +10 in Redding, nimmt kein Geld
#define RL_MARION_WACHSAM           (2)     // beobachtet den Spieler
#define RL_MARION_FEIND             (3)

#define RL_MALAMUTE_OFFEN           (0)
#define RL_MALAMUTE_BETEILIGUNG     (1)
#define RL_MALAMUTE_PREISKRIEG      (2)     // laeuft, bis vier Wochen Ramsch-Preise erreicht sind
#define RL_MALAMUTE_SABOTAGE        (3)
#define RL_MALAMUTE_UEBERNAHME      (4)

#define RL_LIZENZ_PREIS             (1000)
#define RL_LIZENZ_RABATT            (600)
#define RL_AUFSCHLAG_MEHR           (50)    // 125 statt 75 $/Woche
#define RL_LIZENZ_WOCHE             (75)
#define RL_NELL_FUEHRUNG            (50)
#define RL_OHNE_NELL_FUEHRUNG       (30)
#define RL_MALAMUTE_ANTEIL_PREIS    (1500)
#define RL_MALAMUTE_ANTEIL_WOCHE    (60)
#define RL_MALAMUTE_KAUFPREIS       (3000)
#define RL_PREISKRIEG_WOCHEN        (4)
#define RL_WAAGE_PREIS              (15)    // Umsatz +15 %
#define RL_WAAGE_KARMA              (2)
#define RL_REVOLTE_WOCHEN           (3)

procedure rl_red_besitz(variable haus);
procedure rl_red_lizenz(variable haus, variable welt, variable weg);
procedure rl_red_marion_schutz(variable haus, variable welt);
procedure rl_red_marion_feind(variable haus, variable welt);
procedure rl_red_revolte(variable haus, variable welt);
procedure rl_red_waage_chance(variable haus, variable welt);
procedure rl_red_entzug(variable haus);
procedure rl_red_figuren(variable haus, variable welt);

procedure rl_red_besitz(variable haus) begin
   return haus[rl_idx(RL_REDDING, RL_F_BESITZ)];
end

/* Die Lizenz ist da: Die Schlacke gehoert dem Spieler. */
procedure rl_red_lizenz(variable haus, variable welt, variable weg) begin
   variable h := RL_REDDING;
   if (welt[RL_W_RED_LIZENZ] != RL_LIZENZ_KEINE) then return;
   welt[RL_W_RED_LIZENZ] := weg;
   call rl_haus_uebernehmen(haus, welt, h);
   haus[rl_idx(h, RL_F_FUEHRUNG)] := RL_NELL_FUEHRUNG;
   haus[rl_idx(h, RL_F_EINFLUSS)] := rl_max(haus[rl_idx(h, RL_F_EINFLUSS)], 20);
   if (weg == RL_LIZENZ_AUFSCHLAG) then
      haus[rl_idx(h, RL_F_BESTECHUNG_MOD)] := RL_AUFSCHLAG_MEHR;
   else if (weg == RL_LIZENZ_MARION) then begin
      haus[rl_idx(h, RL_F_BESTECHUNG_MOD)] := -RL_LIZENZ_WOCHE;
      welt[RL_W_ASCORTI] := 1;
      call rl_red_marion_schutz(haus, welt);
   end else if (weg == RL_LIZENZ_DROHUNG) then begin
      haus[rl_idx(h, RL_F_BESTECHUNG_MOD)] := -RL_LIZENZ_WOCHE;
      call rl_haus_plus(haus, h, RL_F_HITZE, 20);
      if (welt[RL_W_MARION] == RL_MARION_NEUTRAL) then welt[RL_W_MARION] := RL_MARION_WACHSAM;
   end
   // Ein Schutzherr aus der Zeit vor der Lizenz (Wanamingo-Mine) zaehlt jetzt
   if ((welt[RL_W_MARION] == RL_MARION_SCHUTZ) and (welt[RL_W_MARION_BONUS] == 0)) then begin
      haus[rl_idx(h, RL_F_SICHERHEIT)] := haus[rl_idx(h, RL_F_SICHERHEIT)] + 10;
      welt[RL_W_MARION_BONUS] := 1;
   end
end

/* Marion wird Schutzherr: Sicherheit +10, sobald die Schlacke dem Spieler gehoert */
procedure rl_red_marion_schutz(variable haus, variable welt) begin
   if (welt[RL_W_MARION] == RL_MARION_FEIND) then return;
   welt[RL_W_MARION] := RL_MARION_SCHUTZ;
   if (rl_red_besitz(haus) and (welt[RL_W_MARION_BONUS] == 0)) then begin
      haus[rl_idx(RL_REDDING, RL_F_SICHERHEIT)] := haus[rl_idx(RL_REDDING, RL_F_SICHERHEIT)] + 10;
      welt[RL_W_MARION_BONUS] := 1;
   end
end

procedure rl_red_marion_feind(variable haus, variable welt) begin
   welt[RL_W_MARION] := RL_MARION_FEIND;
   if (welt[RL_W_MARION_BONUS]) then begin
      haus[rl_idx(RL_REDDING, RL_F_SICHERHEIT)] := rl_max(0, haus[rl_idx(RL_REDDING, RL_F_SICHERHEIT)] - 10);
      welt[RL_W_MARION_BONUS] := 0;
   end
end

/* Marion findet die gezinkte Waage: Revolte der Kumpel (Phase 4, 4.2) */
procedure rl_red_revolte(variable haus, variable welt) begin
   variable h := RL_REDDING;
   haus[rl_idx(h, RL_F_MODULE)]     := haus[rl_idx(h, RL_F_MODULE)] - RL_MOD_WAAGE_GEZINKT;
   haus[rl_idx(h, RL_F_PREISMOD)]   := haus[rl_idx(h, RL_F_PREISMOD)] - RL_WAAGE_PREIS;
   haus[rl_idx(h, RL_F_GESCHLOSSEN)] := RL_REVOLTE_WOCHEN;
   call rl_haus_plus(haus, h, RL_F_MORAL, -10);
   call rl_haus_plus(haus, h, RL_F_RUF, -15);
   call rl_haus_plus(haus, h, RL_F_EINFLUSS, -10);
   // Wer Ascorti bezahlt, zahlt jetzt das Doppelte
   if ((welt[RL_W_RED_LIZENZ] == RL_LIZENZ_PAKET) or (welt[RL_W_RED_LIZENZ] == RL_LIZENZ_AUFSCHLAG)) then
      haus[rl_idx(h, RL_F_BESTECHUNG_MOD)] := haus[rl_idx(h, RL_F_BESTECHUNG_MOD)] + RL_LIZENZ_WOCHE;
   if (welt[RL_W_MARION] == RL_MARION_SCHUTZ) then
      call rl_red_marion_feind(haus, welt);
   else if (welt[RL_W_MARION] == RL_MARION_NEUTRAL) then
      welt[RL_W_MARION] := RL_MARION_WACHSAM;
end

// Chance je Woche, dass Marion die Waage findet: 5 % + Hitze / 5, doppelt, wenn er wachsam ist
procedure rl_red_waage_chance(variable haus, variable welt) begin
   variable c := 5 + haus[rl_idx(RL_REDDING, RL_F_HITZE)] / 5;
   if ((welt[RL_W_MARION] == RL_MARION_WACHSAM) or (welt[RL_W_MARION] == RL_MARION_FEIND)) then c := c * 2;
   return c;
end

// Die Entzugsstube ist gebaut (nicht nur gekauft): Stoff-Ereignisse halbiert
procedure rl_red_entzug(variable haus) begin
   variable id := RL_M_RED_ENTZUGSSTUBE;
   return ((haus[rl_idx(RL_REDDING, RL_F_GEKAUFT)] bwand rl_bit(id))
           and (haus[rl_idx(RL_REDDING, RL_F_BAU_ID)] != id + 1));
end

/* Figuren in der Schlacke: vor der Lizenz Ascortis Schreiber, danach Nell */
procedure rl_red_figuren(variable haus, variable welt) begin
   if (not rl_red_besitz(haus)) then
      call rl_figur(PID_AVERAGE_PEASANT_MALE, rl_haus_platz(RL_REDDING, RL_PLATZ_GAST1), SCRIPT_RLSCHREIBER);
   else if (welt[RL_W_RED_TOTE] == 0) then
      call rl_figur(PID_AVERAGE_PEASANT_FEMALE, rl_haus_platz(RL_REDDING, RL_PLATZ_MADAME), SCRIPT_RLNELL);
end

#endif
