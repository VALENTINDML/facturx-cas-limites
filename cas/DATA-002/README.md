# DATA-002 — Date inexistante (30 février)

| | |
|---|---|
| Catégorie | formats de valeurs |
| Ce que le cas teste | Déclenche une assertion officielle |
| Règle | BR-FR / FNFE-MPE — BR-FR-03_BT-2 |
| Source de l'exigence | BR-FR / FNFE-MPE |
| Assertions déclenchées | BR-FR-03_BT-2 |
| Libellé officiel | La date d'émission (udt:DateTimeString) doit contenir une année comprise entre 2000 et 2099, au format AAAAMMJJ. |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(DATA-002) est un identifiant du corpus, pas un code de norme.

## Le défaut

Date au bon format AAAAMMJJ mais qui n'existe pas au calendrier. Côté EN 16931, rien ne se déclenche — BR-03 ne vérifie que la présence. La fonction de contrôle du schematron français valide le calendrier réel, années bissextiles comprises : c'est elle qui attrape le 30 février.

## Pourquoi une implémentation le rate

Le contrôle de format passe. Seule une conversion réelle en date détecte le problème — le schematron français la fait, pas l'européen.

## Fichiers

- `facture.pdf` — le document complet
- `factur-x.xml` — le XML seul, pour tester le validateur sans passer par
  l'extraction

## Ce qu'on attend d'un rejet

Un rejet doit nommer la règle violée et le champ concerné. Un message du type
« ce fichier n'a pas pu être traité » n'est pas exploitable par l'émetteur :
c'est précisément le défaut que ce corpus cherche à mesurer.

---
Corpus de test Factur-X. Documents fictifs, sans valeur légale.
