# PDF-003 — AFRelationship absent

| | |
|---|---|
| Catégorie | structure PDF |
| Ce que le cas teste | Conteneur PDF/A-3 ou spécification Factur-X |
| Règle | ISO 19005-3 (PDF/A-3) — clé AFRelationship obligatoire |
| Source de l'exigence | ISO 19005-3 |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(PDF-003) est un identifiant du corpus, pas un code de norme.

## Le défaut

La pièce jointe existe mais ne déclare pas sa relation au document. Contrôle PDF/A-3, hors schematron.

## Pourquoi une implémentation le rate

L'extraction fonctionne quand même ; seule une validation PDF/A-3 stricte le détecte.

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
