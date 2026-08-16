# OK-001 — Facture conforme (témoin)

| | |
|---|---|
| Catégorie | témoin |
| Ce que le cas teste | Témoin |
| Règle | EN 16931 — profil BASIC |
| Source de l'exigence | EN 16931 · BR-FR / FNFE-MPE |
| Comportement attendu | **acceptation** |

Références vérifiées le 16/08/2026 contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
(OK-001) est un identifiant du corpus, pas un code de norme.

## Le défaut

Facture saine. Sert de référence : un validateur qui la rejette a un problème avant même de traiter les cas défectueux.

## Pourquoi une implémentation le rate

Un validateur trop strict sur des champs optionnels rejette ce témoin. C'est le premier test à passer.

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
