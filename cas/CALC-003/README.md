# CALC-003 — Ventilation TVA ≠ total TVA

| | |
|---|---|
| Catégorie | calcul et ventilation |
| Ce que le cas teste | Déclenche une assertion officielle |
| Règle | EN 16931 — BR-CO-14 |
| Source de l'exigence | EN 16931 |
| Assertions déclenchées | BR-CO-14, puis BR-CO-16 |
| Libellé officiel | Invoice total VAT amount (BT-110) = Σ VAT category tax amount (BT-117). |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(CALC-003) est un identifiant du corpus, pas un code de norme.

## Le défaut

Le total de TVA ne correspond pas à la somme des montants ventilés par taux. Le net à payer n'ayant pas été recalé sur le TTC forcé, BR-CO-16 se déclenche aussi.

## Pourquoi une implémentation le rate

Passe inaperçu quand un seul taux est présent et que le contrôle porte sur le total global.

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
