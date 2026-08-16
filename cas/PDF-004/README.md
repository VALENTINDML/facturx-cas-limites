# PDF-004 — AFRelationship incorrect (/Source)

| | |
|---|---|
| Catégorie | structure PDF |
| Ce que le cas teste | Non normé — aucune assertion ne se déclenche |
| Règle | Factur-X 1.0.07 — AFRelationship attendu /Data ; tolérance d'implémentation |
| Source de l'exigence | Factur-X 1.0.07 (FNFE-MPE / FeRD) |
| Comportement attendu | **avertissement** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(PDF-004) est un identifiant du corpus, pas un code de norme.

## Le défaut

Relation déclarée `/Source` au lieu de `/Data`. Comportement non normé au sens des schematrons ; la valeur attendue a varié selon les versions de la spécification (ZUGFeRD 2.0 utilisait /Alternative), d'où des divergences d'implémentation.

## Pourquoi une implémentation le rate

Cas fréquent en production. Toléré par la plupart des lecteurs, signalé par les validateurs stricts. À traiter en avertissement, pas en rejet.

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
