# PDF-008 — Entrée /AF absente à la racine

| | |
|---|---|
| Catégorie | structure PDF |
| Ce que le cas teste | Conteneur PDF/A-3 ou spécification Factur-X |
| Règle | Factur-X 1.0.07 — tableau /AF du catalogue (ISO 32000-2) |
| Source de l'exigence | Factur-X 1.0.07 (FNFE-MPE / FeRD) · ISO 32000-2 |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(PDF-008) est un identifiant du corpus, pas un code de norme.

## Le défaut

La pièce jointe est dans /Names mais pas référencée dans /AF. L'exigence du tableau /AF vient de la spécification Factur-X, qui s'appuie sur les fichiers associés d'ISO 32000-2 — pas de PDF/A-3, qui ne le requiert pas.

## Pourquoi une implémentation le rate

Extraction possible, conformité Factur-X fausse. Classique des bibliothèques qui attachent sans mettre à jour le catalogue.

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
