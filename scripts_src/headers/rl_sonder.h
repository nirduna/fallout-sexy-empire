/*
   rl_sonder.h - Sondermodule ausserhalb des Simulator-Katalogs

   Dunkle und Story-Module aus Phase 2 (Zuflucht, gezinkte Waage, Jet-Theke,
   Die Akte, Schmuggelkammer, Registratur). Sie stehen im Ausbau-Menue unter
   "Etwas, das es nur hier gibt", werden gebaut wie Katalog-Module und setzen
   bei Fertigstellung ein Flag in RL_F_MODULE.

   IDs: Katalog-Module 0..RL_MODULE_ANZAHL-1, Sondermodule ab RL_SONDER_BASIS
   (so steht es auch in RL_F_BAU_ID - 1). Texte: Namen ab 430, Wirkung ab 530.
*/
#ifndef RL_SONDER_H
#define RL_SONDER_H

#define RL_SONDER_BASIS             (50)
#define RL_SM_ZUFLUCHT              (0)     // Den: versteckte Kammer (Ketten, Akt 2/3)
#define RL_SM_JET_THEKE             (1)     // New Reno: nur mit Mordino-Pate oder Jet-Vertrag (Umsetzung 7)
#define RL_SM_WAAGE                 (2)     // Redding: die gezinkte Goldwaage (Umsetzung 8)
#define RL_SM_AKTE                  (3)     // Vault City: Die Akte (Umsetzung 9)
#define RL_SM_REGISTRATUR           (4)     // NCR: Registratur (Umsetzung 10)
#define RL_SM_ANZAHL                (5)
#define RL_MSG_SONDER_NAME          (430)
#define RL_MSG_SONDER_EFFEKT        (530)

procedure rl_sonder_kosten(variable sm);
procedure rl_sonder_wochen(variable sm);
procedure rl_sonder_flag(variable sm);
procedure rl_sonder_fertig(variable haus, variable h, variable sm);

procedure rl_sonder_kosten(variable sm) begin
   return get_array([600, 800, 150, 1000, 500], sm);
end

procedure rl_sonder_wochen(variable sm) begin
   return get_array([1, 2, 1, 1, 1], sm);
end

procedure rl_sonder_flag(variable sm) begin
   return get_array([RL_MOD_ZUFLUCHT, RL_MOD_JET_THEKE, RL_MOD_WAAGE_GEZINKT, RL_MOD_AKTE, RL_MOD_REGISTRATUR], sm);
end

/* Fertigstellung: Flag setzen, eine Ausbaustufe mehr Unterhalt.
   Jet-Theke: +6 $ Nebenumsatz je Kunde (Phase 2). Doppelte Stoff-Ereignisse
   und das Misstrauen der Wrights folgen aus dem Flag (gl_rotlicht.ssl). */
procedure rl_sonder_fertig(variable haus, variable h, variable sm) begin
   haus[rl_idx(h, RL_F_MODULE)] := haus[rl_idx(h, RL_F_MODULE)] bwor rl_sonder_flag(sm);
   haus[rl_idx(h, RL_F_STUFEN)] := haus[rl_idx(h, RL_F_STUFEN)] + 1;
   if (sm == RL_SM_JET_THEKE) then
      haus[rl_idx(h, RL_F_NEBEN)] := haus[rl_idx(h, RL_F_NEBEN)] + 6;
   // Gezinkte Waage: Umsatz +15 %, H +10. Karma und Entdeckung im Wochentakt
   // Die Akte: H +10. Einfluss und Entdeckung im Wochentakt
   if (sm == RL_SM_AKTE) then
      haus[rl_idx(h, RL_F_HITZE)] := rl_min(100, haus[rl_idx(h, RL_F_HITZE)] + 10);
   if (sm == RL_SM_WAAGE) then begin
      haus[rl_idx(h, RL_F_PREISMOD)] := haus[rl_idx(h, RL_F_PREISMOD)] + 15;
      haus[rl_idx(h, RL_F_HITZE)] := rl_min(100, haus[rl_idx(h, RL_F_HITZE)] + 10);
   end
end

#endif
