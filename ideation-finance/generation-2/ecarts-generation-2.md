# Génération 2 — écarts

1. **Lancement sans le verdict de H03.** La règle scellée prévoyait de lancer les proposeurs après les verdicts de H13 et de H03.
   H13 est jugée (« survit »). La course de H03 est annulée pour une erreur de préinscription (`../tests-de-mort/H03/annulation.md`)
   et sera rejouée sous une préinscription corrigée. Les proposeurs sont lancés avec les deux parents connus (F04 et H13) ; le
   registre qu'ils reçoivent dit que le test de H03 est annulé et ne donne aucun de ses chiffres. Si H03-v2 survit, elle sera
   parent de la génération 3.

2. **Quatrième famille ajoutée : Astra (OpenAI, `gpt-6-astra`).** Oubli de l'orchestrateur, relevé par le commanditaire : la clé
   OpenAI était disponible et la génération 2 avait été lancée avec trois familles seulement. Astra est ajouté comme quatrième
   proposeur (même consigne, identifiants `3A`) et comme quatrième juge. `appeler.py`, la grille et le code d'agrégation ont été
   modifiés et rescellés (`SCEAUX-apres-ecart-2.sha256`) **avant la lecture de toute fiche** : seuls les titres des fiches de Gemini
   avaient été vus. Changements : 4 juges, 20 fiches, au plus 5 « à retenir » et au moins 8 « à écarter » par juge ; les 5 premières
   restent retenues. La course 2 (génération 1) a été jouée sans Astra ; elle n'est pas rejouée.
