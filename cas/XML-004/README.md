# XML-004 — GuidelineID absent

| | |
|---|---|
| Catégorie | structure XML |
| Ce que le cas teste | Déclenche une assertion officielle |
| Règle | EN 16931 — BR-01 |
| Source de l'exigence | EN 16931 |
| Assertions déclenchées | BR-01 |
| Libellé officiel | An Invoice shall have a Specification identifier (BT-24). |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(XML-004) est un identifiant du corpus, pas un code de norme.

## Le défaut

Identifiant de profil vide : impossible de savoir quelles règles appliquer. L'assertion vérifie que l'élément, une fois normalisé, n'est pas vide — un élément présent mais vide déclenche bien la règle.

## Pourquoi une implémentation le rate

Certaines implémentations supposent BASIC par défaut au lieu de rejeter.

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
