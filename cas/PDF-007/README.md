# PDF-007 — Pas de PDF/A (OutputIntent absent)

| | |
|---|---|
| Catégorie | structure PDF |
| Ce que le cas teste | Conteneur PDF/A-3 ou spécification Factur-X |
| Règle | ISO 19005-3 — conformité PDF/A-3 |
| Source de l'exigence | ISO 19005-3 |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(PDF-007) est un identifiant du corpus, pas un code de norme.

## Le défaut

PDF ordinaire portant un XML Factur-X : l'OutputIntent est retiré volontairement à la construction. La non-conformité PDF/A-3 est ici le défaut injecté, pas un artefact du générateur — les 31 autres cas embarquent profil ICC et polices. Hors schematron : le XML embarqué reste, lui, parfaitement valide.

## Pourquoi une implémentation le rate

Techniquement exploitable, réglementairement non conforme — c'est le défaut le plus fréquent des générateurs maison.

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
