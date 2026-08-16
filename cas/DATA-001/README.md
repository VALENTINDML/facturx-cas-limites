# DATA-001 — Date en ISO au lieu du format 102

| | |
|---|---|
| Catégorie | formats de valeurs |
| Ce que le cas teste | Déclenche une assertion officielle |
| Règle | BR-FR / FNFE-MPE — BR-FR-03_BT-2 |
| Source de l'exigence | BR-FR / FNFE-MPE |
| Assertions déclenchées | BR-FR-03_BT-2, CII-DT-097 |
| Libellé officiel | La date d'émission (udt:DateTimeString) doit contenir une année comprise entre 2000 et 2099, au format AAAAMMJJ. |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(DATA-001) est un identifiant du corpus, pas un code de norme.

## Le défaut

Date écrite `2026-08-15` alors que l'attribut annonce le format 102. BR-03 ne se déclenche pas : il vérifie seulement que l'élément est présent et non vide. Se déclenchent, mesuré : BR-FR-03_BT-2 (format AAAAMMJJ, schematron français) et CII-DT-097, la règle de syntaxe CII qui impose AAAAMMJJ quand l'attribut `format` vaut 102.

## Pourquoi une implémentation le rate

Un parseur tolérant lit la date correctement et masque une non-conformité qui cassera chez le destinataire suivant.

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
