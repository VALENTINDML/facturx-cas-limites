# XML-001 — XML tronqué

| | |
|---|---|
| Catégorie | structure XML |
| Ce que le cas teste | Échoue en amont du schematron |
| Règle | W3C XML 1.0 — document bien formé (en amont de tout schematron) |
| Source de l'exigence | W3C XML 1.0 |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(XML-001) est un identifiant du corpus, pas un code de norme.

## Le défaut

Le fichier embarqué s'arrête au milieu d'une balise. Aucun schematron ne s'exécute sur un document mal formé : l'erreur est au niveau du parseur.

## Pourquoi une implémentation le rate

Doit produire une erreur de parsing explicite, pas un plantage ni un rejet silencieux.

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
