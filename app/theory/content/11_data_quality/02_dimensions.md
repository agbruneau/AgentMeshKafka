# Dimensions de Qualité des Données

## 1. Complétude (Completeness)

Mesure la présence des données attendues.

```
┌─────────────────────────────────────────────────┐
│              COMPLÉTUDE                          │
├─────────────────────────────────────────────────┤
│                                                  │
│  Formule : (Non-nulls / Total) × 100            │
│                                                  │
│  Exemple customers.email :                       │
│  ┌────────────────────────────────────┐         │
│  │ ID   │ Name       │ Email         │         │
│  ├────────────────────────────────────┤         │
│  │ 1    │ Dupont     │ jean@mail.com │  ✓      │
│  │ 2    │ Martin     │ NULL          │  ✗      │
│  │ 3    │ Durant     │ pierre@...    │  ✓      │
│  │ 4    │ Moreau     │ NULL          │  ✗      │
│  │ 5    │ Petit      │ marie@...     │  ✓      │
│  └────────────────────────────────────┘         │
│                                                  │
│  Complétude email = 3/5 = 60%                   │
│                                                  │
│  Seuils typiques :                               │
│  • Critique (facturation) : > 99%               │
│  • Important (contact) : > 95%                   │
│  • Optionnel (marketing) : > 80%                │
│                                                  │
└─────────────────────────────────────────────────┘
```

## 2. Exactitude (Accuracy)

Vérifie que les données respectent le format et les règles attendues.

```
┌─────────────────────────────────────────────────┐
│              EXACTITUDE                          │
├─────────────────────────────────────────────────┤
│                                                  │
│  Règles de validation :                          │
│                                                  │
│  EMAIL                                           │
│  • Pattern: ^[\w.-]+@[\w.-]+\.\w+$              │
│  • "jean@mail.com" → ✓                          │
│  • "jean@" → ✗                                  │
│  • "jean.mail.com" → ✗                          │
│                                                  │
│  TÉLÉPHONE (France)                              │
│  • Pattern: ^0[1-9][0-9]{8}$                    │
│  • "0612345678" → ✓                             │
│  • "612345678" → ✗ (manque 0)                   │
│  • "+33612345678" → À normaliser                │
│                                                  │
│  CODE POSTAL                                     │
│  • Pattern: ^[0-9]{5}$                          │
│  • "75001" → ✓                                  │
│  • "7500" → ✗                                   │
│                                                  │
│  DATE                                            │
│  • Format: YYYY-MM-DD                           │
│  • Cohérence: date_naissance < date_jour        │
│  • "2024-13-45" → ✗ (invalide)                  │
│                                                  │
└─────────────────────────────────────────────────┘
```

## 3. Cohérence (Consistency)

Assure que les données sont cohérentes entre elles et entre systèmes.

```
┌─────────────────────────────────────────────────┐
│              COHÉRENCE                           │
├─────────────────────────────────────────────────┤
│                                                  │
│  COHÉRENCE INTRA-RECORD                          │
│  ───────────────────────                         │
│  • date_debut < date_fin                        │
│  • montant_ht + tva = montant_ttc               │
│  • age >= 18 si statut = "MAJEUR"               │
│                                                  │
│  COHÉRENCE INTER-SYSTÈMES                        │
│  ────────────────────────                        │
│                                                  │
│  CRM               Policy Admin                  │
│  ─────────         ────────────                  │
│  "Jean Dupont"  vs "JEAN DUPONT"    → ⚠️        │
│  "0612345678"   vs "06 12 34 56 78" → ⚠️        │
│                                                  │
│  INTÉGRITÉ RÉFÉRENTIELLE                         │
│  ───────────────────────                         │
│  • policy.customer_id existe dans customers     │
│  • claim.policy_id existe dans policies         │
│                                                  │
│  Test:                                           │
│  SELECT COUNT(*) FROM claims c                  │
│  LEFT JOIN policies p ON c.policy_id = p.id    │
│  WHERE p.id IS NULL; -- Doit retourner 0       │
│                                                  │
└─────────────────────────────────────────────────┘
```

## 4. Validité (Validity)

Vérifie que les valeurs sont dans les plages autorisées.

```
┌─────────────────────────────────────────────────┐
│              VALIDITÉ                            │
├─────────────────────────────────────────────────┤
│                                                  │
│  LISTES DE VALEURS AUTORISÉES                    │
│  ─────────────────────────────                   │
│  policy.status IN ('DRAFT', 'ACTIVE',           │
│                    'CANCELLED', 'EXPIRED')      │
│                                                  │
│  customer.segment IN ('BASIC', 'STANDARD',      │
│                       'PREMIUM')                 │
│                                                  │
│  product.type IN ('AUTO', 'HOME', 'HEALTH')     │
│                                                  │
│  PLAGES NUMÉRIQUES                               │
│  ─────────────────                               │
│  • premium BETWEEN 0 AND 100000                 │
│  • age BETWEEN 0 AND 150                        │
│  • percentage BETWEEN 0 AND 100                 │
│                                                  │
│  RÈGLES MÉTIER                                   │
│  ─────────────                                   │
│  • IF product = 'AUTO' THEN premium >= 200      │
│  • IF age < 25 THEN premium *= 1.5 (jeune)      │
│  • IF status = 'ACTIVE' THEN premium > 0        │
│                                                  │
└─────────────────────────────────────────────────┘
```

## 5. Unicité (Uniqueness)

Détecte et gère les doublons.

```
┌─────────────────────────────────────────────────┐
│              UNICITÉ                             │
├─────────────────────────────────────────────────┤
│                                                  │
│  DOUBLONS EXACTS                                 │
│  ───────────────                                 │
│  SELECT email, COUNT(*) as cnt                  │
│  FROM customers                                  │
│  GROUP BY email                                  │
│  HAVING COUNT(*) > 1;                           │
│                                                  │
│  DOUBLONS APPROXIMATIFS (Fuzzy)                  │
│  ─────────────────────────────                   │
│  ┌────────────────────────────────────┐         │
│  │ "Jean Dupont"    │ "Jean DUPONT"   │ 95%    │
│  │ "Marie Martin"   │ "M. Martin"     │ 80%    │
│  │ "Pierre Durant"  │ "P. Durand"     │ 75%    │
│  └────────────────────────────────────┘         │
│                                                  │
│  Algorithmes de matching :                       │
│  • Levenshtein distance                         │
│  • Soundex / Metaphone                          │
│  • Jaro-Winkler similarity                      │
│  • N-gram matching                              │
│                                                  │
│  Actions sur doublons :                          │
│  • Merge (fusion avec règles survivorship)      │
│  • Link (liaison sans fusion)                   │
│  • Purge (suppression)                          │
│                                                  │
└─────────────────────────────────────────────────┘
```

## 6. Fraîcheur (Timeliness)

Mesure si les données sont suffisamment récentes.

```
┌─────────────────────────────────────────────────┐
│              FRAÎCHEUR                           │
├─────────────────────────────────────────────────┤
│                                                  │
│  SLA par type de données :                       │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │ Donnée          │ SLA         │ Actuel   │   │
│  ├──────────────────────────────────────────┤   │
│  │ Prix temps réel │ < 1 seconde │ 500ms ✓  │   │
│  │ Stock           │ < 1 minute  │ 45s ✓    │   │
│  │ Client CRM      │ < 1 heure   │ 2h ✗     │   │
│  │ Reporting       │ < 24 heures │ 18h ✓    │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  Mesure :                                        │
│  Freshness = NOW() - MAX(updated_at)            │
│                                                  │
│  Causes de retard :                              │
│  • Pipeline ETL en échec                        │
│  • CDC décalé (lag)                             │
│  • Source non mise à jour                       │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Scorecard qualité

```
┌─────────────────────────────────────────────────┐
│        DATA QUALITY SCORECARD                    │
├─────────────────────────────────────────────────┤
│                                                  │
│  Dataset: CUSTOMERS                              │
│  Date: 2024-01-15                                │
│                                                  │
│  Dimension        Score    Seuil    Status      │
│  ──────────────────────────────────────────     │
│  Complétude       94%      95%      ⚠️ WARNING  │
│  Exactitude       98%      95%      ✅ OK       │
│  Cohérence        97%      95%      ✅ OK       │
│  Validité         99%      98%      ✅ OK       │
│  Unicité          92%      95%      ❌ CRITICAL │
│  Fraîcheur        100%     99%      ✅ OK       │
│  ──────────────────────────────────────────     │
│  SCORE GLOBAL     96.7%    95%      ✅ OK       │
│                                                  │
│  Actions requises:                               │
│  • Résoudre 847 doublons clients                │
│  • Compléter 312 emails manquants               │
│                                                  │
└─────────────────────────────────────────────────┘
```
