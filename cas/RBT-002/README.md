# RBT-002 — Caractères spéciaux et entités XML

| | |
|---|---|
| Catégorie | robustesse |
| Ce que le cas teste | Échoue en amont du schematron |
| Règle | W3C XML 1.0 §2.4 — échappement (en amont de tout schematron) |
| Source de l'exigence | W3C XML 1.0 |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(RBT-002) est un identifiant du corpus, pas un code de norme.

## Le défaut

Chevrons et esperluette non échappés dans les libellés : le document est mal formé, aucun schematron ne s'exécute.

## Pourquoi une implémentation le rate

Un générateur qui concatène des chaînes sans échapper produit un XML mal formé. Le test vérifie que le validateur le dit clairement au lieu de planter.

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
