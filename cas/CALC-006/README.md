# CALC-006 — Exonération sans motif déclaré

| | |
|---|---|
| Catégorie | calcul et ventilation |
| Ce que le cas teste | Déclenche une assertion officielle |
| Règle | EN 16931 — BR-E-10 |
| Source de l'exigence | EN 16931 |
| Assertions déclenchées | BR-E-10 |
| Libellé officiel | A VAT Breakdown (BG-23) with VAT Category code (BT-118) "Exempt from VAT" shall have a VAT exemption reason code (BT-121) or a VAT exemption reason text (BT-120). |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(CALC-006) est un identifiant du corpus, pas un code de norme.

## Le défaut

Catégorie TVA « E » sans code ni texte d'exonération.

## Pourquoi une implémentation le rate

Cas très fréquent chez les auto-entrepreneurs en franchise de TVA. Souvent accepté à tort.

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
