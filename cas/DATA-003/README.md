# DATA-003 — Échéance antérieure à l'émission

| | |
|---|---|
| Catégorie | formats de valeurs |
| Ce que le cas teste | Déclenche une assertion officielle |
| Règle | BR-FR / FNFE-MPE — BR-FR-CO-07_BT-9 |
| Source de l'exigence | BR-FR / FNFE-MPE |
| Assertions déclenchées | BR-FR-CO-07_BT-9 |
| Libellé officiel | La date d’échéance (BT-9), si présente, doit être postérieure ou égale à la date de facture (BT-2), sauf si la facture est de type acompte (386, 500, 503) ou si le cadre de facturation (BT-23) est B2, S2 ou M2. |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(DATA-003) est un identifiant du corpus, pas un code de norme.

## Le défaut

Date d'échéance avant la date de facture. Côté EN 16931, rien ne se déclenche : aucune assertion européenne ne compare ces deux dates. Le profil français, lui, l'interdit — sauf facture d'acompte (386, 500, 503) ou cadre de facturation B2, S2, M2, où l'échéance antérieure est légitime.

## Pourquoi une implémentation le rate

Une implémentation qui ne charge que le schematron européen accepte ce document. C'est le cas d'école de l'écart entre conformité EN 16931 et conformité au profil français : les deux jeux de règles doivent tourner.

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
