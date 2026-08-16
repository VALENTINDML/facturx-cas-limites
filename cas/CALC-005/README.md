# CALC-005 — Même taux, deux écritures (20 et 20.00)

| | |
|---|---|
| Catégorie | calcul et ventilation |
| Ce que le cas teste | Déclenche une assertion officielle |
| Règle | EN 16931 — BR-S-08 |
| Source de l'exigence | EN 16931 |
| Assertions déclenchées | BR-S-08 (deux fois) |
| Libellé officiel | For each different value of VAT category rate (BT-119) where the VAT category code (BT-118) is "Standard rated", the VAT category taxable amount (BT-116) in a VAT breakdown (BG-23) shall equal the sum of Invoice line net amounts (BT-131) plus the sum of document level charge amounts (BT-99) minus the sum of document level allowance amounts (BT-92) where the VAT category code (BT-151, BT-102, BT-95) is "Standard rated" and the VAT rate (BT-152, BT-103, BT-96) equals the VAT category rate (BT-119). |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(CALC-005) est un identifiant du corpus, pas un code de norme.

## Le défaut

Deux lignes au même taux réel, écrit `20.00` puis `20`, produisant deux ventilations TVA distinctes pour un même couple catégorie/taux. BR-CO-17 tient — chaque ventilation est arithmétiquement juste — et BR-CO-14 aussi. C'est BR-S-08 qui se déclenche, deux fois : la comparaison des taux y est numérique, `20` et `20.00` sont donc le même taux, et la base déclarée par chaque ventilation (2 400,00 puis 135,00) ne vaut pas la somme des lignes à ce taux (2 535,00).

## Pourquoi une implémentation le rate

Un regroupement par chaîne de caractères crée deux ventilations distinctes au lieu d'une. Le validateur ne nomme pas le vrai problème : il signale des bases de TVA fausses, alors que la cause est un regroupement raté. Chercher l'erreur dans les montants fait perdre des heures.

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
