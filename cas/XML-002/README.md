# XML-002 — Espace de noms rsm erroné

| | |
|---|---|
| Catégorie | structure XML |
| Ce que le cas teste | Échoue en amont du schematron |
| Règle | UN/CEFACT CII — espace de noms :100 (validation XSD, en amont du schematron) |
| Source de l'exigence | UN/CEFACT CII (XSD) |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(XML-002) est un identifiant du corpus, pas un code de norme.

## Le défaut

Le namespace CrossIndustryInvoice pointe vers une version 90 au lieu de 100 : le document est hors schéma et la validation XSD échoue. Le document reste bien formé, et exécuter le schematron malgré tout — mesuré — produit des erreurs qui désignent autre chose : BR-CO-18 « aucune ventilation de TVA », BR-S-08, CII-DT-033. Les éléments `ram:` continuent en effet de correspondre, seule la racine `rsm:` ne correspond plus.

## Pourquoi une implémentation le rate

Un parseur permissif ignore le namespace et traite le document comme valide. Pire : sauter la validation XSD pour n'exécuter que le schematron produit trois erreurs qui pointent toutes à côté, et l'émetteur corrige des montants qui n'ont rien à se reprocher.

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
