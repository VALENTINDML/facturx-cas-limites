# Corpus de cas limites Factur-X

32 factures Factur-X portant chacune un défaut précis, avec l'assertion réellement violée et le comportement attendu.

## À quoi ça sert

Tester une implémentation Factur-X sur ce qu'elle laisse passer et sur ce qu'elle rejette à tort. La question n'est pas seulement « accepte-t-elle une facture valide », mais « quand elle refuse, dit-elle pourquoi ». Un rejet qui ne nomme pas la règle violée oblige l'émetteur à deviner, et c'est ce qui remplit les files de support.

## Usage

Ces fichiers sont destinés à tester votre propre implémentation, ou une implémentation publique et librement accessible. Ne les soumettez pas au système de production d'un tiers sans y avoir été invité.

## Références normatives

Les 32 documents ont été passés aux validateurs officiels, et le classement ci-dessous est celui des assertions réellement obtenues — pas d'une lecture des règles. Quand une assertion se déclenche, son libellé officiel est repris tel quel. Vérifié le 16/08/2026 contre :

- EN 16931 : ConnectingEurope validation-1.3.16 (CII, preprocessed), sha256 54e0dc6d06cd7f17d268bb9696ff56f58d386ee28961c9bbef0a56718c400c89
- BR-FR : FNFE-MPE France_RFE v1.4.0.03 du 04/08/2026, BR-FR-Flux2-Schematron-CII V1.4.0 du 30/06/2026, sha256 d1172c6e89cc17fcdafcaaaf2ad57c2d1d1a576ad7694b5a6e5514a7cec0c4db

Exécution via les XSLT compilés publiés dans ces mêmes releases, sous Saxon-HE 13 (XSLT 2.0). Le témoin `OK-001` sort à **0 échec sur 91 règles EN 16931 et 69 règles BR-FR**.

Les références de cas (`OK-001`, `CALC-001`…) sont des identifiants du corpus, **pas** des codes de norme.

## Les cas, groupés par ce qu'ils testent

Le groupement suit ce que chaque cas déclenche réellement, pas la famille dont il vient. Le groupe non normé vient en premier : c'est celui qui justifie l'existence de ce corpus.

### Témoin (1 cas)

La facture saine. Un validateur qui la rejette a un problème avant même de traiter les cas défectueux.

| Réf | Cas | Attendu | Référence |
|---|---|---|---|
| `OK-001` | Facture conforme (témoin) | acceptation | EN 16931 — profil BASIC |

### Non normé — aucune assertion ne se déclenche (5 cas)

Le cœur du corpus. Ces documents passent la validation normative : aucune assertion EN 16931 ni BR-FR ne les rejette, et deux implémentations également conformes peuvent malgré tout les traiter différemment — l'une accepte, l'autre refuse, et le flux bloque sans qu'aucune des deux n'ait tort. C'est là que se logent les litiges d'interopérabilité que la norme ne tranche pas, et c'est ce qu'un corpus apporte qu'un validateur ne donne pas : la liste explicite de ce sur quoi il faut se mettre d'accord contractuellement.

| Réf | Cas | Attendu | Référence |
|---|---|---|---|
| `IDENT-001` | SIRET à 13 chiffres dans le visuel PDF | acceptation | comportement non normé — incohérence entre le visuel PDF et le XML (le XML reste conforme) |
| `IDENT-002` | Clé de TVA intracommunautaire fausse | avertissement | aucune assertion — contrôle métier (clé française), hors schematron |
| `PDF-004` | AFRelationship incorrect (/Source) | avertissement | Factur-X 1.0.07 — AFRelationship attendu /Data ; tolérance d'implémentation |
| `PRF-001` | Profil MINIMUM avec contenu BASIC | avertissement | Factur-X 1.0.07 — cohérence profil / contenu (hors schematron ; divergence d'implémentation) |
| `RBT-001` | Désignation de 1 000 caractères | acceptation | comportement non normé — aucune limite de longueur dans les schematrons |

### Déclenche une assertion officielle (13 cas)

Un validateur conforme doit les rejeter, et nommer la règle. L'assertion exacte est indiquée, avec son libellé officiel repris tel quel dans la fiche du cas.

| Réf | Cas | Attendu | Assertion |
|---|---|---|---|
| `CALC-001` | Total TTC ≠ HT + TVA | rejet | BR-CO-15, puis BR-CO-16 |
| `CALC-002` | Somme des lignes ≠ total des lignes | rejet | BR-CO-10, puis BR-CO-13 |
| `CALC-003` | Ventilation TVA ≠ total TVA | rejet | BR-CO-14, puis BR-CO-16 |
| `CALC-004` | Arrondi au demi-centime | rejet | BR-DEC-23, BR-FR-DEC-01_BT-131, BR-S-08 |
| `CALC-005` | Même taux, deux écritures (20 et 20.00) | rejet | BR-S-08 (deux fois) |
| `CALC-006` | Exonération sans motif déclaré | rejet | BR-E-10 |
| `DATA-001` | Date en ISO au lieu du format 102 | rejet | BR-FR-03_BT-2, CII-DT-097 |
| `DATA-002` | Date inexistante (30 février) | rejet | BR-FR-03_BT-2 |
| `DATA-003` | Échéance antérieure à l'émission | rejet | BR-FR-CO-07_BT-9 |
| `DATA-004` | Devise absente | rejet | BR-05 |
| `DATA-006` | Prix net négatif sur une ligne | rejet | BR-27, BR-FR-DEC-03_BT-146 |
| `IDENT-003` | Vendeur sans identifiant TVA (lignes taxées) | rejet | BR-S-02 |
| `XML-004` | GuidelineID absent | rejet | BR-01 |

### Échoue en amont du schematron (5 cas)

Document mal formé ou hors schéma XSD : aucun schematron ne s'exécute. Le rejet doit être explicite sur la cause — un message de parseur brut n'est pas exploitable par l'émetteur.

| Réf | Cas | Attendu | Référence |
|---|---|---|---|
| `DATA-005` | Séparateur décimal virgule | rejet | XSD UN/CEFACT CII — xs:decimal, point décimal (en amont du schematron) |
| `RBT-002` | Caractères spéciaux et entités XML | rejet | W3C XML 1.0 §2.4 — échappement (en amont de tout schematron) |
| `XML-001` | XML tronqué | rejet | W3C XML 1.0 — document bien formé (en amont de tout schematron) |
| `XML-002` | Espace de noms rsm erroné | rejet | UN/CEFACT CII — espace de noms :100 (validation XSD, en amont du schematron) |
| `XML-003` | Déclaration d'encodage mensongère | rejet | W3C XML 1.0 §4.3.3 — déclaration d'encodage |

### Conteneur PDF/A-3 ou spécification Factur-X (8 cas)

Le XML embarqué est valide ; c'est le conteneur ou la cohérence PDF/XML qui est en défaut. Aucune assertion de schematron ne porte sur ces points.

| Réf | Cas | Attendu | Référence |
|---|---|---|---|
| `PDF-001` | Aucun XML embarqué | rejet | Factur-X 1.0.07 — XML embarqué obligatoire (hors schematron) |
| `PDF-002` | Nom de pièce jointe non normalisé | rejet | Factur-X 1.0.07 — nom de fichier factur-x.xml (hors schematron) |
| `PDF-003` | AFRelationship absent | rejet | ISO 19005-3 (PDF/A-3) — clé AFRelationship obligatoire |
| `PDF-005` | Métadonnées XMP Factur-X absentes | rejet | Factur-X 1.0.07 — extension XMP obligatoire (hors schematron) |
| `PDF-006` | XMP déclare un profil différent du XML | rejet | Factur-X 1.0.07 — cohérence XMP / GuidelineID (hors schematron) |
| `PDF-007` | Pas de PDF/A (OutputIntent absent) | rejet | ISO 19005-3 — conformité PDF/A-3 |
| `PDF-008` | Entrée /AF absente à la racine | rejet | Factur-X 1.0.07 — tableau /AF du catalogue (ISO 32000-2) |
| `PRF-002` | Profil inexistant | rejet | Factur-X 1.0.07 / XP Z12-012 — liste fermée des profils (hors schematron EN / BR-FR) |

## Ce que ce corpus a corrigé

Ce corpus a d'abord été écrit de mémoire, en attribuant à chaque cas la règle qui semblait évidente. La vérification a établi que **8 cas ne testaient pas ce qu'ils annonçaient** : règle qui tient malgré le défaut, défaut qui n'atteint jamais le XML, norme source erronée, ou assertion déclarée absente qui se déclenche pourtant. Ils sont listés ici plutôt que corrigés en silence — un corpus dont on peut vérifier les affirmations vaut mieux qu'un corpus qui n'admet rien.

Elle s'est faite en deux passes, et la seconde a compté. Lire les schematrons en a corrigé six. **Exécuter** ensuite les validateurs sur les 32 documents a rectifié trois attributions de plus — `DATA-003` et `XML-002`, qui s'ajoutent à la liste, et `CALC-005`, que la lecture avait déjà repris une fois et classé à tort « aucune assertion ». Lire une règle et l'exécuter ne donnent pas le même résultat : c'est la leçon la plus utile de ce corpus, et elle vaut aussi pour qui l'utilisera.

**`IDENT-001`** — annoncé : ID-001 — « SIRET à 13 chiffres », violation de BR-CO-26, rejet attendu.

Établi : Le SIRET tronqué n'atteint jamais le XML : il n'existe que dans le visuel PDF. Le XML embarqué est celui du témoin à l'octet près (empreintes identiques). Aucune assertion ne se déclenche, un validateur conforme accepte. Le cas est conservé — il teste désormais ce qu'il testait en fait depuis le début : la cohérence entre le lisible et le structuré. Attendu corrigé en acceptation.

**`IDENT-002`** — annoncé : ID-002 — clé de TVA fausse, violation de BR-CO-09, rejet attendu.

Établi : BR-CO-09 ne vérifie que le préfixe pays ISO 3166-1, correct ici. Aucun schematron ne recalcule la clé française modulo 97. Un validateur normatif accepte ce document. Attendu corrigé en avertissement.

**`IDENT-003`** — annoncé : ID-003 — « vendeur sans aucun identifiant », violation de BR-CO-26.

Établi : L'identifiant légal (SIREN, schemeID 0002) reste présent dans le XML : BR-CO-26, qui exige au moins un identifiant parmi trois, tient. C'est BR-S-02 qui se déclenche — TVA facturée sans identifiant TVA du vendeur. Titre et règle corrigés.

**`CALC-005`** — annoncé : BR-005 — deux écritures du même taux, violation de BR-CO-17.

Établi : BR-CO-17 tient : chaque ventilation est arithmétiquement juste, et leur somme aussi (BR-CO-14 tient). C'est BR-S-08 qui se déclenche, deux fois — la comparaison des taux y est numérique, donc `20` et `20.00` sont le même taux, et chaque base déclarée ne vaut pas la somme des lignes à ce taux. Corrigé en deux temps : d'abord classé à tort « aucune assertion » sur lecture du schematron, puis rectifié en exécutant les validateurs.

**`DATA-006`** — annoncé : FMT-006 — « ligne à montant négatif », violation de la distinction TypeCode 380 / 381.

Établi : Un montant de ligne négatif (BT-131) est licite en EN 16931, y compris sur une facture 380 : c'est ainsi qu'on porte une remise en ligne. C'est le PRIX net négatif que BR-27 interdit. Rejeter tout montant négatif sur une 380 refuserait des factures valides.

**`PDF-008`** — annoncé : PDF-008 — entrée /AF absente, violation de PDF/A-3 §3.1.

Établi : PDF/A-3 n'exige pas le tableau /AF du catalogue. L'exigence vient de la spécification Factur-X, qui s'appuie sur les fichiers associés d'ISO 32000-2. Norme source corrigée ; le défaut et le comportement attendu sont inchangés.

**`DATA-003`** — annoncé : FMT-003 — échéance antérieure à l'émission, « aucune règle ne l'interdit », avertissement attendu.

Établi : Le schematron français l'interdit explicitement : BR-FR-CO-07_BT-9 exige une échéance postérieure ou égale à la date de facture, sauf acompte (386, 500, 503) ou cadre B2/S2/M2. L'affirmation « aucune assertion » ne valait que pour le schematron européen. Attendu corrigé en rejet.

**`XML-002`** — annoncé : XML-002 — namespace erroné, « aucun contexte de schematron ne correspond plus ».

Établi : Faux : les éléments `ram:` continuent de correspondre, seule la racine `rsm:` ne correspond plus. Exécuter le schematron sur ce document produit trois erreurs qui désignent autre chose (BR-CO-18, BR-S-08, CII-DT-033) — ce qui rend le cas plus instructif, pas moins : il montre ce que coûte de sauter la validation XSD.

Trois autres cas portaient un code faux sans se tromper sur la nature du défaut : `DATA-001` et `DATA-002` citaient `BR-02` (qui concerne le numéro de facture, pas la date) alors que le contrôle du format et du calendrier vient du schematron français `BR-FR-03_BT-2` ; `CALC-004` citait la famille `BR-DEC-*` au lieu de l'assertion précise `BR-DEC-23`.

## Renumérotation des références

Les références de cas ont changé **une fois, avant la première publication** du corpus. Les anciens préfixes pouvaient se lire comme des codes normatifs : `BR-001` n'a jamais désigné la règle EN 16931 `BR-1`, et `FMT-` est par ailleurs utilisé par le moteur de diagnostic pour ses propres contrôles. Les références ci-dessous sont désormais stables.

| Ancienne réf | Nouvelle réf |
|---|---|
| `BR-001` | `CALC-001` |
| `BR-002` | `CALC-002` |
| `BR-003` | `CALC-003` |
| `BR-004` | `CALC-004` |
| `BR-005` | `CALC-005` |
| `BR-006` | `CALC-006` |
| `FMT-001` | `DATA-001` |
| `FMT-002` | `DATA-002` |
| `FMT-003` | `DATA-003` |
| `FMT-004` | `DATA-004` |
| `FMT-005` | `DATA-005` |
| `FMT-006` | `DATA-006` |
| `ID-001` | `IDENT-001` |
| `ID-002` | `IDENT-002` |
| `ID-003` | `IDENT-003` |

`OK-001`, `PDF-00x`, `XML-00x`, `PRF-00x` et `RBT-00x` sont inchangés : aucune ambiguïté possible avec un code normatif.

## Conformité PDF/A-3 de cette génération

Générée avec polices souscrites (Arial.ttf) et profil ICC embarqué (sRGB Profile.icc), schéma d'extension XMP Factur-X déclaré. La seule exception est `PDF-007`, dont la non-conformité PDF/A-3 est le défaut injecté. La génération échoue explicitement quand ces ressources manquent — un corpus produit sans elles porte la mention `--sans-pdfa` dans son manifeste.

## Structure

```
CAS-XXX/
  facture.pdf     document complet
  factur-x.xml    XML seul
  README.md       description du défaut
```

---

Documents fictifs, sans valeur légale. Toute ressemblance avec des entreprises existantes serait fortuite.