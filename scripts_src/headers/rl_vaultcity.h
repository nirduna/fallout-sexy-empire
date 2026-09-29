/*
   rl_vaultcity.h - Vault City: Die Kloake (Phase 2 Abschnitt 2.4, Phase 3
   Abschnitt 2.4, Phase 3 Abschnitt 5.1, Phase 4 Abschnitte 2.3 und 4.2).
   Umsetzung 9.

   "Ein Keller im Courtyard": Hanne Voss gewinnen (Speech 60 mit 10 % Anteil
   fuer sie, oder 1.500 $) und Papiere (Buergerschaft, Sorensen bestechen oder
   Faelschung). Beides zusammen: Die Kloake gehoert dem Spieler, Hanne fuehrt
   sie als Wirtin der Tarnung.

   Schweigegeld: 200 $/Woche je Hausklasse (mit Buergerschaft 50 $ weniger,
   mit angeworbener Wache 50 $ mehr).

   Die Razzia (Phase 4, 4.2): Die Garde holt die Haelfte des Personals ins
   Corrections Center; von dort gehen sie an die Dienstboten-Zuteilung.
   Freikaufen bei Sorensen (300 $ je Person), befreien (Sneak 70 und
   Lockpick 70, H +30) oder aufgeben (Moral -30 in allen Haeusern, Karma -10).
   Mit einer Wache am Tor oder E >= 60 kommt die Razzia eine Woche angekuendigt:
   Wer den Keller fuer die Woche schliesst, verliert niemanden.

   Die Akte (Sondermodul): E +2/Woche, H +10. Wird sie gefunden, kommt die
   Garde sofort. Mit ihr laesst sich First Citizen Lynette unter Druck setzen:
   Die Razzien enden, E +20, H +20.

   Wird am Ende von rotlicht.h eingebunden.
*/
#ifndef RL_VAULTCITY_H
#define RL_VAULTCITY_H

#define RL_HANNE_OFFEN              (0)
#define RL_HANNE_ANTEIL             (1)     // Speech 60: 10 % fuer sie
#define RL_HANNE_GEKAUFT            (2)     // 1.500 $

#define RL_PAPIERE_KEINE            (0)
#define RL_PAPIERE_BUERGER          (1)     // Buergerschaft (Vanilla): Schweigegeld -50 $
#define RL_PAPIERE_SORENSEN         (2)     // Barter 40 und 500 $
#define RL_PAPIERE_FAELSCHUNG       (3)     // Science 60, H +5

#define RL_WACHE_KEINE              (0)
#define RL_WACHE_ANGEWORBEN         (1)     // CH 6 und 50 $/Woche
#define RL_WACHE_SORENSEN           (2)     // Sorensen draengt sie; Sorensen ist erpressbar

#define RL_SORENSEN_ERPRESSBAR      (1)     // Bits in RL_W_VC_SORENSEN
#define RL_SORENSEN_TOT             (2)

#define RL_HANNE_PREIS              (1500)
#define RL_HANNE_ANTEIL_PROZENT     (10)
#define RL_SORENSEN_PREIS           (500)
#define RL_SCHWEIGEGELD_KLASSE      (200)
#define RL_BUERGER_RABATT           (50)
#define RL_WACHE_WOCHE              (50)
#define RL_FREIKAUF_PREIS           (300)
#define RL_PACHT_WOCHE              (50)    // Dienstboten-Pacht je Person (Phase 4, 2.3)
#define RL_HANNE_FUEHRUNG           (50)
#define RL_OHNE_HANNE_FUEHRUNG      (30)

procedure rl_vc_besitz(variable haus);
procedure rl_vc_buerger;
procedure rl_vc_pruefen(variable haus, variable welt);
procedure rl_vc_schweigegeld(variable haus, variable welt);
procedure rl_vc_warnung(variable haus, variable welt);
procedure rl_vc_razzia(variable haus, variable welt);
procedure rl_vc_zurueck(variable haus, variable welt);
procedure rl_vc_aufgeben(variable haus, variable welt);
procedure rl_vc_pacht(variable haus, variable n);
procedure rl_vc_figuren(variable haus, variable welt);

procedure rl_vc_besitz(variable haus) begin
   return haus[rl_idx(RL_VAULT_CITY, RL_F_BESITZ)];
end

// Buerger von Vault City (auch mit Skeeves falschen Papieren, nicht nach dem Rauswurf)
procedure rl_vc_buerger begin
   return ((global_var(GVAR_VAULT_CITIZEN) > 0) and (global_var(GVAR_VAULT_CITIZEN) < CITIZEN_KICKED_OUT));
end

/* Hanne und Papiere beisammen: Die Kloake gehoert dem Spieler. */
procedure rl_vc_pruefen(variable haus, variable welt) begin
   variable h := RL_VAULT_CITY;
   if (rl_vc_besitz(haus)) then return;
   if ((welt[RL_W_VC_HANNE] == RL_HANNE_OFFEN) or (welt[RL_W_VC_PAPIERE] == RL_PAPIERE_KEINE)) then return;
   call rl_haus_uebernehmen(haus, welt, h);
   haus[rl_idx(h, RL_F_FUEHRUNG)] := RL_HANNE_FUEHRUNG;
   haus[rl_idx(h, RL_F_EINFLUSS)] := rl_max(haus[rl_idx(h, RL_F_EINFLUSS)], 20);
   haus[rl_idx(h, RL_F_PREISSTUFE)] := RL_PREIS_GEHOBEN;       // Vault City zahlt fuer Schweigen (Phase 2)
   if (welt[RL_W_VC_HANNE] == RL_HANNE_ANTEIL) then
      haus[rl_idx(h, RL_F_TRIBUTMOD)] := haus[rl_idx(h, RL_F_TRIBUTMOD)] + RL_HANNE_ANTEIL_PROZENT;
   if (welt[RL_W_VC_PAPIERE] == RL_PAPIERE_FAELSCHUNG) then
      call rl_haus_plus(haus, h, RL_F_HITZE, 5);
   call rl_vc_schweigegeld(haus, welt);
end

// Schweigegeld: 200 $ je Hausklasse (die ersten 200 $ stehen im Stadtprofil)
procedure rl_vc_schweigegeld(variable haus, variable welt) begin
   variable h := RL_VAULT_CITY, mod;
   mod := RL_SCHWEIGEGELD_KLASSE * (rl_max(1, haus[rl_idx(h, RL_F_KLASSE)]) - 1);
   if (welt[RL_W_VC_PAPIERE] == RL_PAPIERE_BUERGER) then mod := mod - RL_BUERGER_RABATT;
   if (welt[RL_W_VC_WACHE] == RL_WACHE_ANGEWORBEN) then mod := mod + RL_WACHE_WOCHE;
   haus[rl_idx(h, RL_F_BESTECHUNG_MOD)] := mod;
end

// Wird die Razzia angekuendigt? (Wache am Tor oder E >= 60, Phase 4)
procedure rl_vc_warnung(variable haus, variable welt) begin
   return ((welt[RL_W_VC_WACHE] != RL_WACHE_KEINE) or (haus[rl_idx(RL_VAULT_CITY, RL_F_EINFLUSS)] >= 60));
end

/* Die Garde kommt und findet das Haus (Phase 4, 4.2). Gepachtete Dienstboten
   gehen als Zeugen an die Stadt zurueck, die Haelfte des Personals ins
   Corrections Center, die Akte wird beschlagnahmt, der Keller versiegelt. */
procedure rl_vc_razzia(variable haus, variable welt) begin
   variable h := RL_VAULT_CITY, n, pacht;
   pacht := haus[rl_idx(h, RL_F_ZWANG)];
   if (pacht > 0) then begin
      call rl_vc_pacht(haus, -pacht);
      call rl_haus_plus(haus, h, RL_F_HITZE, 20);
   end
   n := rl_max(1, haus[rl_idx(h, RL_F_PERSONAL)] / 2);
   n := rl_min(n, haus[rl_idx(h, RL_F_PERSONAL)]);
   haus[rl_idx(h, RL_F_PERSONAL)] := haus[rl_idx(h, RL_F_PERSONAL)] - n;
   haus[rl_idx(h, RL_F_GEZWUNGEN)] := rl_min(haus[rl_idx(h, RL_F_GEZWUNGEN)], haus[rl_idx(h, RL_F_PERSONAL)]);
   welt[RL_W_VC_GEFASST] := welt[RL_W_VC_GEFASST] + n;
   if (haus[rl_idx(h, RL_F_MODULE)] bwand RL_MOD_AKTE) then begin
      haus[rl_idx(h, RL_F_MODULE)] := haus[rl_idx(h, RL_F_MODULE)] - RL_MOD_AKTE;
      haus[rl_idx(h, RL_F_STUFEN)] := rl_max(0, haus[rl_idx(h, RL_F_STUFEN)] - 1);
   end
   haus[rl_idx(h, RL_F_GESCHLOSSEN)] := rl_max(haus[rl_idx(h, RL_F_GESCHLOSSEN)], 1);
   call rl_haus_plus(haus, h, RL_F_MORAL, -15);
   call rl_haus_plus(haus, h, RL_F_EINFLUSS, -10);
   welt[RL_W_VC_RAZZIA_WOCHE] := 0;
end

// Die Gefassten sind wieder da (freigekauft oder befreit)
procedure rl_vc_zurueck(variable haus, variable welt) begin
   haus[rl_idx(RL_VAULT_CITY, RL_F_PERSONAL)] := haus[rl_idx(RL_VAULT_CITY, RL_F_PERSONAL)] + welt[RL_W_VC_GEFASST];
   welt[RL_W_VC_GEFASST] := 0;
end

// Aufgeben: Das spricht sich in allen Haeusern herum (Phase 4, 4.2)
procedure rl_vc_aufgeben(variable haus, variable welt) begin
   variable i := 0;
   while (i < RL_ANZAHL_HAEUSER) do begin
      if (haus[rl_idx(i, RL_F_BESITZ)]) then call rl_haus_plus(haus, i, RL_F_MORAL, -30);
      i := i + 1;
   end
   rl_karma(-10);
   welt[RL_W_VC_GEFASST] := 0;
end

/* Dienstboten-Pacht (Phase 4, 2.3): n > 0 pachtet, n < 0 gibt zurueck. Die
   Gepachteten zaehlen als Zwangspersonal (Karma -5/Woche, Moral-Deckel). */
procedure rl_vc_pacht(variable haus, variable n) begin
   variable h := RL_VAULT_CITY;
   if (n > 0) then
      call rl_zwang_dazu(haus, h, n);
   else begin
      n := rl_min(-n, haus[rl_idx(h, RL_F_ZWANG)]);
      haus[rl_idx(h, RL_F_ZWANG)] := haus[rl_idx(h, RL_F_ZWANG)] - n;
      haus[rl_idx(h, RL_F_PERSONAL)] := rl_max(0, haus[rl_idx(h, RL_F_PERSONAL)] - n);
      n := -n;
   end
   haus[rl_idx(h, RL_F_LOEHNE)] := rl_max(0, haus[rl_idx(h, RL_F_LOEHNE)] + n * RL_PACHT_WOCHE);
end

/* Figuren in der Kloake: Hanne (vor und nach der Uebernahme) und Sorensen */
procedure rl_vc_figuren(variable haus, variable welt) begin
   if (welt[RL_W_VC_TOTE] == 0) then
      call rl_figur(PID_AVERAGE_PEASANT_FEMALE, rl_haus_platz(RL_VAULT_CITY, RL_PLATZ_MADAME), SCRIPT_RLHANNE);
   if ((welt[RL_W_VC_SORENSEN] bwand RL_SORENSEN_TOT) == 0) then
      call rl_figur(PID_MALE_VAULT_CITIZEN, rl_haus_platz(RL_VAULT_CITY, RL_PLATZ_GAST2), SCRIPT_RLSORENSEN);
end

#endif
