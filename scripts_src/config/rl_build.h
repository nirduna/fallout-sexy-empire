/*
   rl_build.h - Build-Einstellungen (Standard fuer das Restoration Project)

   tools/build_scripts.sh kompiliert eine Kopie von scripts_src und
   ueberschreibt darin diese Datei mit den Werten aus den Umgebungsvariablen.
   Diese Fassung gilt nur, wenn von Hand kompiliert wird.

   Hinweis: sslc wertet nur einen einzigen -m-Schalter und nur einen
   einzigen -I-Pfad aus. Deshalb laufen alle Einstellungen ueber diese Datei.
*/
#define RL_SCRIPT_BASE              (1559)
#define RL_GVAR_BASE                (791)
// #define RL_SELBSTTEST
// #define RL_DEBUG
