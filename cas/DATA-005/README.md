# DATA-005 — Séparateur décimal virgule

| | |
|---|---|
| Catégorie | formats de valeurs |
| Ce que le cas teste | Échoue en amont du schematron |
| Règle | XSD UN/CEFACT CII — xs:decimal, point décimal (en amont du schematron) |
| Source de l'exigence | UN/CEFACT CII (XSD) |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(DATA-005) est un identifiant du corpus, pas un code de norme.

## Le défaut

Montant écrit `2400,00`. La validation XSD échoue avant le schematron — la double validation XSD + schematron est celle prévue par XP Z12-012.

## Pourquoi une implémentation le rate

Le défaut le plus courant des générateurs développés en France. Un parseur qui remplace la virgule en silence masque un bug de génération.

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
