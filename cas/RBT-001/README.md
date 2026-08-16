# RBT-001 — Désignation de 1 000 caractères

| | |
|---|---|
| Catégorie | robustesse |
| Ce que le cas teste | Non normé — aucune assertion ne se déclenche |
| Règle | comportement non normé — aucune limite de longueur dans les schematrons |
| Source de l'exigence | comportement non normé |
| Comportement attendu | **acceptation** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(RBT-001) est un identifiant du corpus, pas un code de norme.

## Le défaut

Libellé de ligne anormalement long. Aucune assertion ne borne la longueur d'un libellé.

## Pourquoi une implémentation le rate

Doit être accepté. Une troncature silencieuse en base est un défaut grave et invisible.

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
