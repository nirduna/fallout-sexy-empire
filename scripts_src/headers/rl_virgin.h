/*
   rl_virgin.h - "Blut auf der Virgin Street" (Phase 3 Abschnitte 3.1 und 4.1,
   Phase 4 Abschnitt 3.6). Umsetzung 12.

   Carlo Venuti, Mordino-Capo der Virgin Street, und Miss Kitty vom Cat's Paw.
   Miss Kitty ist eine Vanilla-Figur und spricht nicht selbst (Fahrplan,
   Grundsatz 1); fuer sie verhandelt Jade, ihre rechte Hand.

     Akt 1  Venuti will 200 $/Woche: zahlen, halbieren (Barter 60), ueber seinen
            Kopf (Speech 80: Gebuehr weg, E +5, Venuti gedemuetigt), verweigern
            (H +10, Akt 3 sofort), Made Man einer anderen Familie (Gebuehr weg, H +5)
     Akt 2  Kittys Angebot (Jade): Buendnis, Fusion, Druck, Sabotage, Verrat
     Akt 3  Jet im Blut: ein Dealer im Strumpfband (Moral -10, Stoff x2). Finden
            (PE 7, Sneak 60 oder Moral >= 70), rauswerfen (Unarmed 60), umdrehen
            (Speech 70: Beweise), verschwinden lassen (H +20); heilen (Doctor 60
            oder Myrons Antidot)
     Akt 4  Die Nacht der langen Messer: Sit-down (Speech 90 oder CH 8 mit Made
            Man), zuvorkommen (Beweise und Speech 60 bei Wright), zahlen
            (1.500 $), Umarmung (nur mit Mordino-Pate), oder Kampf im Haus
     Enden  Der leere Stuhl, Waffenstillstand, Die Umarmung

   Kitty als Rivalin ("Kittys Kralle" in Redding): -10 % in der Schlacke,
   Abwerbung, -10 bei der Anhoerung der Reinen. Beenden ueber Nell:
   Versoehnung (Speech 80 und 2.000 $), Uebernahme (E Redding >= 40), Gewalt.

   Wird am Ende von rotlicht.h eingebunden.
*/
#ifndef RL_VIRGIN_H
#define RL_VIRGIN_H

// Aktstand in RL_W_VIRGIN (Enden 10-12 in rotlicht.h)
#define RL_VIRGIN_OFFEN             (0)
#define RL_VIRGIN_GEBUEHR           (1)
#define RL_VIRGIN_KITTY             (2)
#define RL_VIRGIN_JET               (3)
#define RL_VIRGIN_MESSER            (4)

// Bits in RL_W_VIRGIN_FLAGS
#define RL_VF_GEDEMUETIGT           (1)
#define RL_VF_DEALER_GEFUNDEN       (2)
#define RL_VF_BEWEISE               (4)     // der Dealer ist umgedreht
#define RL_VF_DEALER_WEG            (8)
#define RL_VF_GEHEILT               (16)
#define RL_VF_ENTSCHIEDEN           (32)    // Akt 1 ist entschieden
#define RL_VF_RACHE                 (64)    // die Mordinos waren schon gefallen: Venuti will Rache (ab Akt 3)
#define RL_VF_NEU_VERHANDELT        (128)   // nach dem leeren Stuhl: die Tribute sind neu verhandelt

// Kittys Weg (RL_W_KITTY_WEG)
#define RL_KITTY_OFFEN              (0)
#define RL_KITTY_BUENDNIS           (1)
#define RL_KITTY_FUSION             (2)
#define RL_KITTY_DRUCK              (3)
#define RL_KITTY_SABOTAGE           (4)
#define RL_KITTY_VERRAT             (5)
#define RL_KITTY_VERSOEHNT          (6)
#define RL_KITTY_KRALLE_GEKAUFT     (7)
#define RL_KITTY_GEWALT             (8)

// Das Cat's Paw (RL_W_CATSPAW): 0 offen (-15 %), 1 Buendnis (-5 %), 2 geloest, 3 bei den Mordinos (-15 %)
#define RL_CATSPAW_MORDINO          (3)

#define RL_VIRGIN_TOT_VENUTI        (1)     // Bits in RL_W_VIRGIN_TOTE
#define RL_VIRGIN_TOT_JADE          (2)

#define RL_ANGRIFF_VIRGIN           (4)     // Die Nacht der langen Messer (RL_F_ANGRIFF)

#define RL_VENUTI_GEBUEHR           (200)
#define RL_VENUTI_SITDOWN_PREIS     (1500)
#define RL_KITTY_FUSION_PREIS       (3000)
#define RL_KITTY_DRUCK_PREIS        (1500)
#define RL_KITTY_VERRAT_LOHN        (1000)
#define RL_KITTY_VERSOEHNUNG        (2000)
#define RL_KITTY_FUEHRUNG           (85)
#define RL_VIRGIN_ABSTAND           (2)
#define RL_VIRGIN_FRIST             (4)
#define RL_ABWERBUNG_WOCHEN         (4)     // Kittys Abwerbung: einmal im Monat

procedure rl_virgin_gebuehr(variable haus, variable welt, variable betrag);
procedure rl_virgin_weiter(variable welt, variable akt);
procedure rl_virgin_ende(variable haus, variable welt, variable ende);
procedure rl_virgin_umarmung(variable haus, variable welt);
procedure rl_virgin_venuti_da(variable welt);
procedure rl_virgin_jade_da(variable welt);
procedure rl_virgin_figuren(variable haus, variable welt);
procedure rl_kitty_rivalin(variable welt, variable weg);

// Die Gebuehr steht als Schmiergeld-Abweichung in der Wochenrechnung des Strumpfbands
procedure rl_virgin_gebuehr(variable haus, variable welt, variable betrag) begin
   welt[RL_W_VIRGIN_GEBUEHR] := rl_max(0, betrag);
   haus[rl_idx(RL_NEW_RENO, RL_F_BESTECHUNG_MOD)] := welt[RL_W_VIRGIN_GEBUEHR];
end

procedure rl_virgin_weiter(variable welt, variable akt) begin
   welt[RL_W_VIRGIN] := akt;
   welt[RL_W_VIRGIN_WOCHE] := rl_woche_jetzt;
end

/* Akt 5: ein Ende (Phase 3, 3.1) */
procedure rl_virgin_ende(variable haus, variable welt, variable ende) begin
   if (welt[RL_W_VIRGIN] >= RL_VIRGIN_UMARMUNG) then return;
   welt[RL_W_VIRGIN] := ende;
   welt[RL_W_VIRGIN_WOCHE] := rl_woche_jetzt;
   call rl_virgin_gebuehr(haus, welt, 0);
   if (ende == RL_VIRGIN_LEERER_STUHL) then
      call rl_haus_plus(haus, RL_NEW_RENO, RL_F_EINFLUSS, 20);
   else if (ende == RL_VIRGIN_WAFFENSTILLSTAND) then
      call rl_haus_plus(haus, RL_NEW_RENO, RL_F_HITZE, -20);
   else if (ende == RL_VIRGIN_UMARMUNG) then begin
      rl_karma(-30);
      call rl_nr_misstrauen(welt, RL_SEGEN_WRIGHT);
      welt[RL_W_JET_VERTRAG] := 1;
      if (global_var(GVAR_MADE_MAN_MORDINO) == 0) then set_global_var(GVAR_MADE_MAN_MORDINO, 1);
      call rl_virgin_umarmung(haus, welt);
   end
end

/* Die Umarmung: Jet-Theke in jedem eigenen Haus und Einnahmen +20 % (einmal je Haus) */
procedure rl_virgin_umarmung(variable haus, variable welt) begin
   variable h := 0;
   while (h < RL_ANZAHL_HAEUSER) do begin
      if (haus[rl_idx(h, RL_F_BESITZ)] and ((welt[RL_W_UMARMUNG_HAEUSER] bwand rl_bit(h)) == 0)) then begin
         welt[RL_W_UMARMUNG_HAEUSER] := welt[RL_W_UMARMUNG_HAEUSER] bwor rl_bit(h);
         if ((haus[rl_idx(h, RL_F_MODULE)] bwand RL_MOD_JET_THEKE) == 0) then begin
            haus[rl_idx(h, RL_F_MODULE)] := haus[rl_idx(h, RL_F_MODULE)] bwor RL_MOD_JET_THEKE;
            haus[rl_idx(h, RL_F_NEBEN)]  := haus[rl_idx(h, RL_F_NEBEN)] + 6;
            haus[rl_idx(h, RL_F_STUFEN)] := haus[rl_idx(h, RL_F_STUFEN)] + 1;
         end
         haus[rl_idx(h, RL_F_PREISMOD)] := haus[rl_idx(h, RL_F_PREISMOD)] + 20;
      end
      h := h + 1;
   end
end

// Venuti kommt in Akt 1 (bis zur Entscheidung) und in Akt 4
procedure rl_virgin_venuti_da(variable welt) begin
   variable akt := welt[RL_W_VIRGIN];
   if (welt[RL_W_VIRGIN_TOTE] bwand RL_VIRGIN_TOT_VENUTI) then return 0;
   if ((akt == RL_VIRGIN_GEBUEHR) and ((welt[RL_W_VIRGIN_FLAGS] bwand RL_VF_ENTSCHIEDEN) == 0)) then return 1;
   return (akt == RL_VIRGIN_MESSER);
end

// Jade kommt ab Akt 2, bis Kittys Angebot entschieden ist
procedure rl_virgin_jade_da(variable welt) begin
   if (welt[RL_W_VIRGIN_TOTE] bwand RL_VIRGIN_TOT_JADE) then return 0;
   return ((welt[RL_W_VIRGIN] >= RL_VIRGIN_KITTY) and (welt[RL_W_KITTY_WEG] == RL_KITTY_OFFEN));
end

procedure rl_virgin_figuren(variable haus, variable welt) begin
   if (not rl_nr_besitz(haus)) then return;
   if (rl_virgin_venuti_da(welt) and (haus[rl_idx(RL_NEW_RENO, RL_F_ANGRIFF)] == RL_ANGRIFF_KEINER)) then
      call rl_figur(PID_TOUGH_THUG_MALE, rl_haus_platz(RL_NEW_RENO, RL_PLATZ_GAST1), SCRIPT_RLVENUTI);
   if (rl_virgin_jade_da(welt)) then
      call rl_figur(PID_AVERAGE_PEASANT_FEMALE, rl_haus_platz(RL_NEW_RENO, RL_PLATZ_GAST2), SCRIPT_RLJADE);
end

// Kitty wird Rivalin: "Kittys Kralle" in Redding unter dem Schutz der Wrights
procedure rl_kitty_rivalin(variable welt, variable weg) begin
   welt[RL_W_KITTY_WEG] := weg;
   welt[RL_W_KITTY_RIVALIN] := 1;
   welt[RL_W_KITTY_ABWERBUNG] := rl_woche_jetzt;
end

#endif
