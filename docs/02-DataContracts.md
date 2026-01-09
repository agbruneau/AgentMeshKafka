# Data Contracts & Kafka Topology

> **Version :** 1.0.0 | **Statut :** Approuvé | **Dernière révision :** Janvier 2026
>
> **Documents connexes :** [01-ArchitectureDecisions.md](./01-ArchitectureDecisions.md) (ADR-002) | [03-AgentSpecs.md](./03-AgentSpecs.md)

Ce document définit les **spécifications formelles des échanges de données** au sein du Maillage Agentique (**Agent Mesh**). Il constitue le pilier de la **Gouvernance des Données** (le "Système Immunitaire") et définit rigoureusement comment les agents communiquent.
Pour garantir la robustesse du système face à l'imprévisibilité des LLM, tous les échanges sont régis par des **Contrats de Données stricts** appliqués via le *Confluent Schema Registry*.

## 1. Principes de Gouvernance

### 1.1 Standard de Sérialisation

Tous les événements publiés sur le backbone Kafka doivent être sérialisés au format **Apache Avro**.

* **Pourquoi Avro ?** Il est compact, typé, et permet l'évolution de schéma (Schema Evolution).
* **Validation :** Tout message ne respectant pas le schéma enregistré sera rejeté par le *Producer* (avant même d'atteindre le Broker), empêchant la pollution des données.

### 1.2 Politique de Compatibilité

La politique de compatibilité est fixée à **`FORWARD`**.

* **Signification :** Les données produites avec un *nouveau* schéma peuvent être lues par des consommateurs utilisant une *ancienne* version du schéma.
* **Règle d'Or :** On peut ajouter des champs (avec valeur par défaut), mais on ne peut jamais supprimer ou renommer un champ existant.

### 1.3 Gestion des Erreurs (Dead Letter Queue)

Si un agent (IA) échoue à produire une structure conforme au schéma (ex: un JSON malformé généré par le LLM), le message brut est redirigé vers un topic de rejet : `sys.deadletter.queue.v1` pour analyse humaine, sans bloquer le pipeline.

---

## 2. Topologie des Topics (Le Système Nerveux)

Voici la cartographie des canaux de communication pour le scénario de "Demande de Prêt".

| Topic Name | Partition Key | Retention | Description | Producteur | Consommateurs |
| --- | --- | --- | --- | --- | --- |
| `finance.loan.application.v1` | `application_id` | 7 jours | Demandes de prêt brutes initiées par les clients. | **Intake Agent** | Risk Agent |
| `risk.scoring.result.v1` | `application_id` | Permanent (Log) | Évaluation des risques et justification cognitive. | **Risk Agent** | Decision Agent |
| `finance.loan.decision.v1` | `application_id` | Permanent (Log) | Décision finale (Approbation/Refus) notifiée. | **Decision Agent** | Notification Service |

---

## 3. Définition des Schémas (AVRO)

### 3.1 Événement : Demande de Prêt Soumise

**Topic :** `finance.loan.application.v1`
**Fichier :** `schemas/loan_application.avsc`

Cet événement représente le "Fait" initial. Il contient les données brutes à analyser.

```json
{
  "type": "record",
  "name": "LoanApplication",
  "namespace": "com.agentmesh.finance",
  "fields": [
    { "name": "application_id", "type": "string", "doc": "UUID unique de la demande" },
    { "name": "timestamp", "type": "long", "logicalType": "timestamp-millis" },
    { "name": "applicant_id", "type": "string" },
    { "name": "amount_requested", "type": "double" },
    { "name": "currency", "type": "string", "default": "USD" },
    { "name": "declared_monthly_income", "type": "double" },
    { 
      "name": "employment_status", 
      "type": { "type": "enum", "name": "EmploymentStatus", "symbols": ["FULL_TIME", "PART_TIME", "SELF_EMPLOYED", "UNEMPLOYED"] }
    }
  ]
}

```

### 3.2 Événement : Analyse de Risque Complétée

**Topic :** `risk.scoring.result.v1`
**Fichier :** `schemas/risk_assessment.avsc`

Cet événement est le résultat du travail cognitif de l'Agent Risque (Pattern ReAct). Il contient des données structurées (score) et non structurées (raisonnement).

```json
{
  "type": "record",
  "name": "RiskAssessment",
  "namespace": "com.agentmesh.risk",
  "fields": [
    { "name": "application_id", "type": "string" },
    { "name": "risk_score", "type": "int", "doc": "Score de 0 (Sûr) à 100 (Risqué)" },
    { 
      "name": "risk_category", 
      "type": { "type": "enum", "name": "RiskLevel", "symbols": ["LOW", "MEDIUM", "HIGH", "CRITICAL"] }
    },
    { 
      "name": "rationale", 
      "type": "string", 
      "doc": "Explication en langage naturel générée par le LLM justifiant le score." 
    },
    {
      "name": "checked_policies",
      "type": { "type": "array", "items": "string" },
      "doc": "Liste des documents de politique de crédit consultés (RAG)."
    }
  ]
}

```

### 3.3 Événement : Décision Finale

**Topic :** `finance.loan.decision.v1`
**Fichier :** `schemas/loan_decision.avsc`

L'acte d'autorité final émis par l'Agent Décisionnel.

```json
{
  "type": "record",
  "name": "LoanDecision",
  "namespace": "com.agentmesh.finance",
  "fields": [
    { "name": "application_id", "type": "string" },
    { 
      "name": "status", 
      "type": { "type": "enum", "name": "DecisionStatus", "symbols": ["APPROVED", "REJECTED", "MANUAL_REVIEW_REQUIRED"] }
    },
    { "name": "approved_amount", "type": ["null", "double"], "default": null },
    { "name": "decision_timestamp", "type": "long", "logicalType": "timestamp-millis" }
  ]
}

```

---

## 4. Cycle de Vie des Contrats (CI/CD)

Pour modifier un contrat de données, le processus suivant est obligatoire (GitOps) :

1. **Pull Request :** Modifier le fichier `.avsc` dans le dossier `/schemas`.
2. **Validation CI :** Un script `confluent schema-registry check` vérifie la compatibilité avec la version précédente.
3. **Merge & Deploy :** Lors du merge sur `main`, le nouveau schéma est enregistré automatiquement dans le registre.
4. **Génération de Code :** Les classes Python (Pydantic models) sont régénérées à partir des schémas Avro pour être utilisées par les agents.

---

## 📚 Navigation

| ⬅️ Précédent | 🏠 Index | ➡️ Suivant |
|:---|:---:|---:|
| [01-ArchitectureDecisions.md](./01-ArchitectureDecisions.md) | [Documentation](./00-Readme.md#-documentation-complète) | [03-AgentSpecs.md](./03-AgentSpecs.md) |