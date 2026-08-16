# PRF-002 — Profil inexistant

| | |
|---|---|
| Catégorie | profils |
| Ce que le cas teste | Conteneur PDF/A-3 ou spécification Factur-X |
| Règle | Factur-X 1.0.07 / XP Z12-012 — liste fermée des profils (hors schematron EN / BR-FR) |
| Source de l'exigence | Factur-X 1.0.07 (FNFE-MPE / FeRD) · XP Z12-012 |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(PRF-002) est un identifiant du corpus, pas un code de norme.

## Le défaut

Identifiant de profil qui ne correspond à aucune spécification. Ni le schematron EN 16931 ni le BR-FR ne vérifient la valeur de l'URN (BR-01 exige seulement qu'il soit non vide) : c'est le validateur qui, ne pouvant pas sélectionner de jeu de règles, doit rejeter en nommant le profil reçu.

## Pourquoi une implémentation le rate

Le rejet doit nommer le profil reçu. Une erreur générique oblige l'émetteur à deviner.

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
