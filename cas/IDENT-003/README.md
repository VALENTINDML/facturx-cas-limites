# IDENT-003 — Vendeur sans identifiant TVA (lignes taxées)

| | |
|---|---|
| Catégorie | identifiants |
| Ce que le cas teste | Déclenche une assertion officielle |
| Règle | EN 16931 — BR-S-02 |
| Source de l'exigence | EN 16931 |
| Assertions déclenchées | BR-S-02 |
| Libellé officiel | An Invoice that contains an Invoice line (BG-25) where the Invoiced item VAT category code (BT-151) is "Standard rated" shall contain the Seller VAT Identifier (BT-31), the Seller tax registration identifier (BT-32) and/or the Seller tax representative VAT identifier (BT-63). |
| Comportement attendu | **rejet** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(IDENT-003) est un identifiant du corpus, pas un code de norme.

## Le défaut

L'identifiant TVA du vendeur est retiré alors que les lignes sont en catégorie « Standard rated ». L'identifiant légal (SIREN, schemeID 0002) reste présent dans le XML : BR-CO-26, qui exige au moins un identifiant parmi trois, tient. C'est BR-S-02 qui se déclenche — TVA facturée sans identifiant TVA du vendeur.

## Pourquoi une implémentation le rate

Une implémentation qui ne teste que « au moins un identifiant » (BR-CO-26) accepte ce document à tort : la règle applicable dépend de la catégorie de TVA des lignes.

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
