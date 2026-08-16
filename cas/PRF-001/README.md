# PRF-001 — Profil MINIMUM avec contenu BASIC

| | |
|---|---|
| Catégorie | profils |
| Ce que le cas teste | Non normé — aucune assertion ne se déclenche |
| Règle | Factur-X 1.0.07 — cohérence profil / contenu (hors schematron ; divergence d'implémentation) |
| Source de l'exigence | Factur-X 1.0.07 (FNFE-MPE / FeRD) |
| Comportement attendu | **avertissement** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(PRF-001) est un identifiant du corpus, pas un code de norme.

## Le défaut

Le document déclare MINIMUM mais contient des lignes de détail, absentes de ce profil. Aucune assertion EN 16931 / BR-FR ne compare le contenu au profil déclaré : le contrôle relève du schéma du profil Factur-X.

## Pourquoi une implémentation le rate

Techniquement plus riche que déclaré. Faut-il rejeter ou accepter ? Les implémentations divergent, et c'est exactement le genre d'écart qui bloque un flux en production.

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
