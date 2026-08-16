# CALC-002 — Somme des lignes ≠ total des lignes

| | |
|---|---|
| Catégorie | calcul et ventilation |
| Ce que le cas teste | Déclenche une assertion officielle |
| Règle | EN 16931 — BR-CO-10 |
| Source de l'exigence | EN 16931 |
| Assertions déclenchées | BR-CO-10, puis BR-CO-13 |
| Libellé officiel | Sum of Invoice line net amount (BT-106) = Σ Invoice line net amount (BT-131). |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(CALC-002) est un identifiant du corpus, pas un code de norme.

## Le défaut

Le champ LineTotalAmount ne correspond pas à la somme des montants de ligne. Le total HT restant calé sur les lignes réelles, BR-CO-13 (total HT = somme des lignes − remises + charges) se déclenche aussi.

## Pourquoi une implémentation le rate

Souvent causé par un arrondi appliqué au total plutôt que ligne par ligne.

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
