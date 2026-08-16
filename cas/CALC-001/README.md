# CALC-001 — Total TTC ≠ HT + TVA

| | |
|---|---|
| Catégorie | calcul et ventilation |
| Ce que le cas teste | Déclenche une assertion officielle |
| Règle | EN 16931 — BR-CO-15 |
| Source de l'exigence | EN 16931 |
| Assertions déclenchées | BR-CO-15, puis BR-CO-16 |
| Libellé officiel | Invoice total amount with VAT (BT-112) = Invoice total amount without VAT (BT-109) + Invoice total VAT amount (BT-110). |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(CALC-001) est un identifiant du corpus, pas un code de norme.

## Le défaut

Le total TTC déclaré ne correspond pas à la somme du HT et de la TVA. Le net à payer n'ayant pas été recalé, BR-CO-16 (net à payer = TTC − payé + arrondi) se déclenche aussi.

## Pourquoi une implémentation le rate

Le contrôle le plus élémentaire, et pourtant celui que les générateurs maison omettent le plus souvent.

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
