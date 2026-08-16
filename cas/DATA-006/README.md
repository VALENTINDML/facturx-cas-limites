# DATA-006 — Prix net négatif sur une ligne

| | |
|---|---|
| Catégorie | formats de valeurs |
| Ce que le cas teste | Déclenche une assertion officielle |
| Règle | EN 16931 — BR-27 |
| Source de l'exigence | EN 16931 |
| Assertions déclenchées | BR-27, BR-FR-DEC-03_BT-146 |
| Libellé officiel | The Item net price (BT-146) shall NOT be negative. |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(DATA-006) est un identifiant du corpus, pas un code de norme.

## Le défaut

Prix unitaire net et montant de ligne négatifs. C'est le PRIX négatif qui est interdit (BR-27) : un montant de ligne négatif (BT-131) est licite en EN 16931, même sur une facture de type 380 — c'est ainsi qu'on porte une remise en ligne. Le profil français ajoute BR-FR-DEC-03_BT-146, qui exige lui aussi un prix strictement positif hors contrats bi-directionnels.

## Pourquoi une implémentation le rate

L'intuition « négatif = avoir (381) » est fausse au niveau de la ligne : rejeter tout montant négatif sur une 380 refuse des factures valides ; accepter un prix négatif viole la norme. La règle est sur le prix, pas sur le montant.

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
