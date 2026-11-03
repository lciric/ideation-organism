# Lecture gelée — run 20261004-080257-t03

Lecture mécanique des critères gelés (`controle_ia.simulation_t03.lecture`).

| prédiction | verdict | cellules | conformes | contraires | à répliquer | à auditer |
|---|---|---|---|---|---|---|
| P1.1 | confirmée | 510 | 510 | 0 | 0 | 0 |
| P1.2 | confirmée | 9 | 9 | 0 | 0 | 0 |
| P1.3 | confirmée | 36 | 36 | 0 | 0 | 0 |
| P1.4 | confirmée | 9 | 9 | 0 | 0 | 0 |
| P2.1 | confirmée | 24 | 24 | 0 | 0 | 0 |
| P2.2 | confirmée | 21 | 21 | 0 | 0 | 0 |
| P2.3 | confirmée | 3 | 3 | 0 | 0 | 0 |
| P3.1 | confirmée | 18 | 18 | 0 | 0 | 0 |
| P3.2 | confirmée | 36 | 36 | 0 | 0 | 0 |
| P3.3 | confirmée | 6 | 6 | 0 | 0 | 0 |
| P3.4 | confirmée | 12 | 12 | 0 | 0 | 0 |
| P4.1 | confirmée | 7 | 7 | 0 | 0 | 0 |
| P4.2 | confirmée | 68 | 68 | 0 | 0 | 0 |
| P4.3 | confirmée | 3 | 3 | 0 | 0 | 0 |
| P5.1 | confirmée | 5 | 5 | 0 | 0 | 0 |
| P5.2 | confirmée | 4 | 4 | 0 | 0 | 0 |
| P5.3 | confirmée | 6 | 6 | 0 | 0 | 0 |
| P5.4 | confirmée | 1 | 1 | 0 | 0 | 0 |
| P5.5 | confirmée | 1 | 1 | 0 | 0 | 0 |
| P6.1 | confirmée | 12 | 12 | 0 | 0 | 0 |
| P6.2 | confirmée | 8 | 8 | 0 | 0 | 0 |
| P6.3 | confirmée | 4 | 4 | 0 | 0 | 0 |
| P6.4 | confirmée | 12 | 12 | 0 | 0 | 0 |
| P6.5 | confirmée | 9 | 9 | 0 | 0 | 0 |
| P7.1 | confirmée | 3 | 3 | 0 | 0 | 0 |
| P7.2 | confirmée | 1 | 1 | 0 | 0 | 0 |
| P7.3 | confirmée | 6 | 6 | 0 | 0 | 0 |
| P8.1 | confirmée | 3 | 3 | 0 | 0 | 0 |
| P8.2 | confirmée | 11 | 11 | 0 | 0 | 0 |
| P8.3 | confirmée | 4 | 4 | 0 | 0 | 0 |
| P8.4 | confirmée | 34 | 34 | 0 | 0 | 0 |

Audit de symétrie (R4), bornes [0.3, 3.0] : formes closes, variance des écarts réduits 0.955 sur 63 ; égalités, 0.853 sur 104 ; déclenché : False.

## Énoncés du programme (table E)

| énoncé | lecture | exigées | complémentaires |
|---|---|---|---|
| Lemme : « la puissance ne dépend que de B et de la variance — pas de la répartition du sabotage sur les agents ni sur les pas de temps » | Établi par preuve, vérifié en simulation : exact pour la statistique terminale à n₀ fixé, la « variance » étant celle de la statistique (n₀σ²), pour toute répartition (agents, pas, valeurs, choix adaptatif des positions). Faux à variance par action fixée quand n₀ = NT varie : la puissance décroît en n₀. Faux pour la lecture séquentielle toujours valide quant au calendrier (répartition sur les pas) : avancer le sabotage aide le défenseur, le reporter le ramène vers la borne terminale, seule invariante. L'invariance entre agents au même pas (L4) n'est pas testée en T0.3. | P1.1, P1.2, P1.3, P1.4, P3.1, P3.2, P3.3 | — |
| Brief T0.3 : « celle du max par action s'effondre quand la fragmentation croît » | Établi par preuve, vérifié en simulation : exact, avec un plancher strictement au-dessus de α à n₀ fixé. | P2.1, P2.2, P2.3 | — |
| Théorème : « toute statistique fondée sur les marginales (max, moyenne, somme cumulée) a une puissance égale au taux de faux positifs » (dommage dans la corrélation, marginale préservée) | Vrai en classe C (multi-ensemble préservé) pour les statistiques symétriques, trajectoire par trajectoire, et pour toute statistique sous rebrassage uniforme (T1, T2) ; le groupe de permutations compte. Faux en classe K (copule) : la somme et le processus e passent au-dessus de leur taux sous P₀ pour une dépendance positive et en dessous pour une négative ; sous dépendance positive, le max reste à son taux ou en dessous (Slepian) ; c'est le cas de la construction de 2606.10456 (somme 0,07 à 0,25 à α = 0,05). | P4.1, P4.2, P4.3, P6.1, P6.2, P6.3, P6.4, P6.5 | — |
| Théorème : « il faut un agrégateur d'autocorrélation (dans le temps) ou de co-élévation (entre agents) » | En classe K, sous dépendance positive, l'autocorrélation et la co-élévation détectent (P6.1, P6.4) ; sous dépendance négative, la somme et le processus e passent sous leur taux sous P₀ et l'autocorrélation en valeur absolue détecte (P6.2) ; sous dépendance positive, la somme n'est pas aveugle (P6.3, P6.4). Face à un attaquant adaptatif de classe C, l'autocorrélation et les suites sont neutralisables (P5.3) ; seules les statistiques locales — balayage, Page, co-élévation — gardent une garantie trajectorielle (P5.1, P5.4). | P5.1, P5.3, P5.4, P6.1, P6.2, P6.3, P6.4 | P5.2, P5.5 |
| Brief T0.3 : « la somme cumulée échoue » (attaque à marginale préservée) | Exact pour la somme terminale en classe C (T1) ; exact au sens adverse pour la somme séquentielle unilatérale sous arrangements à sommes partielles dominées (T4), dont la règle bilatérale s'échappe ; inexact en classe K : la somme n'est pas aveugle (Φ̄(z_α·√(v₀/v₁)), 0,07 à 0,25 dans la construction de 2606.10456 à α = 0,05), mais reste faible. | P4.1, P6.1, P6.5, P7.1, P7.2 | P7.3 |
| Garde de G1 : « le taux de faux positifs des agrégateurs toujours valides est vérifié empiriquement sur épisodes honnêtes » | Décisive : la règle de Ville dépasse son taux bien spécifié sous effet épisode, corrélation entre agents, dépendance temporelle ou σ sous-estimé, et dépasse α aux niveaux les plus forts d'effet épisode, de corrélation entre agents et de sous-estimation de σ. Le calibrage conforme sur épisodes honnêtes entiers tient son taux quand les épisodes de calibrage et de déploiement sont échangeables (vérification de l'instrument) ; sa robustesse à un décalage entre eux n'est pas testée en T0.3. | P8.1, P8.2, P8.3, P8.4 | — |
