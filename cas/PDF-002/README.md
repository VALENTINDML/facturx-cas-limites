# PDF-002 — Nom de pièce jointe non normalisé

| | |
|---|---|
| Catégorie | structure PDF |
| Ce que le cas teste | Conteneur PDF/A-3 ou spécification Factur-X |
| Règle | Factur-X 1.0.07 — nom de fichier factur-x.xml (hors schematron) |
| Source de l'exigence | Factur-X 1.0.07 (FNFE-MPE / FeRD) |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(PDF-002) est un identifiant du corpus, pas un code de norme.

## Le défaut

Le XML est embarqué sous le nom `facture.xml` au lieu de `factur-x.xml`. Contrôle au niveau du conteneur : aucune assertion de schematron ne se déclenche.

## Pourquoi une implémentation le rate

Une implémentation qui scanne toutes les pièces jointes l'accepte, une autre qui cherche le nom exact ne le trouve pas. Les deux comportements existent en production.

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
