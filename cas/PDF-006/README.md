# PDF-006 — XMP déclare un profil différent du XML

| | |
|---|---|
| Catégorie | structure PDF |
| Ce que le cas teste | Conteneur PDF/A-3 ou spécification Factur-X |
| Règle | Factur-X 1.0.07 — cohérence XMP / GuidelineID (hors schematron) |
| Source de l'exigence | Factur-X 1.0.07 (FNFE-MPE / FeRD) |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(PDF-006) est un identifiant du corpus, pas un code de norme.

## Le défaut

Le XMP annonce MINIMUM, le XML déclare BASIC. Seul un contrôle croisé des deux sources le voit ; aucune assertion de schematron ne porte sur le XMP.

## Pourquoi une implémentation le rate

Défaut invisible sans contrôle croisé des deux sources. Très rarement implémenté.

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
