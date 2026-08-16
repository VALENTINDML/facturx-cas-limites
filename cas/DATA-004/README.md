# DATA-004 — Devise absente

| | |
|---|---|
| Catégorie | formats de valeurs |
| Ce que le cas teste | Déclenche une assertion officielle |
| Règle | EN 16931 — BR-05 |
| Source de l'exigence | EN 16931 |
| Assertions déclenchées | BR-05 |
| Libellé officiel | An Invoice shall have an Invoice currency code (BT-5). |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(DATA-004) est un identifiant du corpus, pas un code de norme.

## Le défaut

Aucun code devise déclaré au niveau document.

## Pourquoi une implémentation le rate

Une implémentation qui suppose EUR par défaut accepte le document et fausse tout traitement multidevise ultérieur.

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
