# CALC-004 — Arrondi au demi-centime

| | |
|---|---|
| Catégorie | calcul et ventilation |
| Ce que le cas teste | Déclenche une assertion officielle |
| Règle | EN 16931 — BR-DEC-23 |
| Source de l'exigence | EN 16931 · BR-FR / FNFE-MPE |
| Assertions déclenchées | BR-DEC-23, BR-FR-DEC-01_BT-131, BR-S-08 |
| Libellé officiel | The allowed maximum number of decimals for the Invoice line net amount (BT-131) is 2. |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(CALC-004) est un identifiant du corpus, pas un code de norme.

## Le défaut

Montant de ligne à trois décimales, à la frontière de l'arrondi. Se déclenchent aussi, mesuré : BR-FR-DEC-01_BT-131 (même exigence de deux décimales côté français) et BR-S-08 (la base de TVA déclarée ne retombe pas sur la somme des lignes, précisément à cause du demi-centime). BR-CO-10, en revanche, tient : l'arrondi de la somme des lignes coïncide avec le total déclaré.

## Pourquoi une implémentation le rate

Selon la stratégie d'arrondi (banquier ou demi-supérieur), deux implémentations calculent un TTC différent d'un centime et se rejettent mutuellement. Cause n°1 des litiges de rapprochement.

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
