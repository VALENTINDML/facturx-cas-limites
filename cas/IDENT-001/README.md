# IDENT-001 — SIRET à 13 chiffres dans le visuel PDF

| | |
|---|---|
| Catégorie | identifiants |
| Ce que le cas teste | Non normé — aucune assertion ne se déclenche |
| Règle | comportement non normé — incohérence entre le visuel PDF et le XML (le XML reste conforme) |
| Source de l'exigence | comportement non normé |
| Comportement attendu | **acceptation** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(IDENT-001) est un identifiant du corpus, pas un code de norme.

## Le défaut

Zéro de tête perdu, typiquement par un passage en tableur — mais uniquement dans le SIRET affiché sur le visuel PDF. Le XML embarqué (SIREN schemeID 0002, adresse de routage, TVA) est identique au témoin, à l'octet près : aucune assertion ne se déclenche, un validateur conforme accepte ce document. Le cas teste le croisement entre le lisible et le structuré, que presque aucune implémentation ne fait.

## Pourquoi une implémentation le rate

Le défaut est invisible pour tout contrôle du XML. Seul un rapprochement du visuel et des données structurées le voit — et c'est pourtant le visuel que le comptable lit.

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
