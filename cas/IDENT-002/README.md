# IDENT-002 — Clé de TVA intracommunautaire fausse

| | |
|---|---|
| Catégorie | identifiants |
| Ce que le cas teste | Non normé — aucune assertion ne se déclenche |
| Règle | aucune assertion — contrôle métier (clé française), hors schematron |
| Source de l'exigence | comportement non normé |
| Comportement attendu | **avertissement** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(IDENT-002) est un identifiant du corpus, pas un code de norme.

## Le défaut

Numéro de TVA au bon format mais dont la clé de contrôle est fausse. BR-CO-09, la seule règle officielle sur ce champ, ne vérifie que le préfixe pays ISO 3166-1 — correct ici. Aucun schematron ne recalcule la clé française (modulo 97) : un validateur normatif accepte ce document. Une implémentation soignée recalcule la clé et signale.

## Pourquoi une implémentation le rate

Le contrôle de format passe, le contrôle de clé n'est presque jamais implémenté — et n'est exigé par aucune norme.

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
