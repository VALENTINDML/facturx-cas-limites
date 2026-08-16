# XML-003 — Déclaration d'encodage mensongère

| | |
|---|---|
| Catégorie | structure XML |
| Ce que le cas teste | Échoue en amont du schematron |
| Règle | W3C XML 1.0 §4.3.3 — déclaration d'encodage |
| Source de l'exigence | W3C XML 1.0 |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(XML-003) est un identifiant du corpus, pas un code de norme.

## Le défaut

En-tête `encoding="UTF-8"` sur un contenu encodé en ISO-8859-1. En amont de tout schematron.

## Pourquoi une implémentation le rate

Les accents deviennent illisibles sans erreur. Le nom de l'acheteur est corrompu en silence — cas typique de défaut qui passe la validation et casse la comptabilité.

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
