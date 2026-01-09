# 📖 Documentation Technique - AgentMeshKafka

> **Version :** 1.0.0 | **Dernière mise à jour :** Janvier 2026

## 📂 Structure de la Documentation

```
/docs
  ├── 00-Readme.md                  # Vision et Thèse du projet (ce fichier)
  ├── 01-ArchitectureDecisions.md   # ADRs (Kafka, Vector DB, LangChain/LangGraph)
  ├── 02-DataContracts.md           # Définition des schémas (Avro) et Topologie Kafka
  ├── 03-AgentSpecs.md              # Personas, Outils et Constitutions des Agents
  ├── 04-EvaluationStrategie.md     # Le "Diamant de l'évaluation" (Test Plan)
  ├── 05-ThreatModel.md             # AgentSec et analyse des risques
  ├── 06-Plan.md                    # Plan d'implémentation (Roadmap)
  └── 07-Constitution.md            # Code de Conduite et Standards d'Ingénierie
```

---

# AgentMeshKafka

**Implémentation d'un Maillage Agentique (Agentic Mesh) résilient propulsé par Apache Kafka et les pratiques AgentOps.**

## 📖 À propos du projet

**AgentMeshKafka** est un projet académique visant à démontrer la faisabilité et la robustesse de l'**Entreprise Agentique**. Contrairement aux approches monolithiques ou aux chatbots isolés, ce projet implémente une architecture décentralisée où des agents autonomes collaborent de manière asynchrone pour exécuter des processus métiers complexes.

Ce projet matérialise les concepts d'architecture suivants :

* **Découplage Temporel & Spatial :** Utilisation d'un backbone événementiel (Kafka) pour relier les agents.
* **AgentOps & Fiabilité :** Industrialisation des agents via des pipelines d'évaluation (Le Diamant de l'Évaluation).
* **Gouvernance des Données :** Utilisation de *Schema Registry* pour garantir des contrats de données stricts.

---

## 🏗️ Architecture du Système

L'architecture repose sur trois piliers fondamentaux, inspirés par la biologie organisationnelle :

### 1. Le Système Nerveux (Communication)

Le cœur du système n'est pas l'IA, mais le flux de données.

* **Technologie :** Apache Kafka (ou Confluent).
* **Patterns :** Event Sourcing, CQRS, Transactional Outbox.
* **Rôle :** Assure la persistance immuable des faits et la communication asynchrone entre agents.

### 2. Le Cerveau (Cognition)

Les agents sont des entités autonomes utilisant le pattern **ReAct** (Reason + Act), propulsés par la suite **Anthropic Claude**.

* **Agent 1 (Intake) :** Réception et normalisation des demandes (Claude 3.5 Haiku).
* **Agent 2 (Analyste Risque) :** RAG (Retrieval-Augmented Generation) sur base documentaire pour évaluer le risque (**Claude Opus 4.5**).
* **Agent 3 (Décisionnel) :** Synthèse et exécution de l'action finale (Claude 3.5 Sonnet).

Le développement est assisté par **Claude Code** et l'auto-correction par **Auto Claude** (voir [07-Constitution.md](./07-Constitution.md)).

### 3. Le Système Immunitaire (Sécurité & Gouvernance)

* **AgentSec :** Validation des entrées/sorties pour prévenir les injections de prompt.
* **Data Contracts :** Schémas Avro stricts pour valider la structure des événements avant publication.

---

## 📂 Structure du Répertoire

```bash
AgentMeshKafka/
├── docs/                   # Documentation (ADRs, Specs, Threat Model)
├── schemas/                # Contrats de données (fichiers .avsc Avro)
├── src/
│   ├── agents/             # Code source des agents (Python)
│   │   ├── intake_agent/
│   │   ├── risk_agent/
│   │   └── decision_agent/
│   └── shared/             # Utilitaires partagés (Kafka wrapper, Prompts)
├── tests/
│   ├── unit/               # Tests déterministes
│   └── evaluation/         # Tests cognitifs (LLM-as-a-judge)
├── docker-compose.yml      # Infrastructure locale (Zookeeper, Kafka, Schema Registry)
└── README.md

```

---

## 🚀 Scénario de Démonstration

Le projet simule un processus de **Traitement de Demande de Prêt Bancaire** :

1. Une demande JSON est déposée.
2. **L'Agent Intake** valide la structure et publie un événement `LoanApplicationReceived`.
3. **L'Agent Risque** consomme l'événement, consulte sa base de connaissances (politique de crédit), calcule un score et publie `RiskAssessmentCompleted`.
4. **L'Agent Décision** analyse le score, prend une décision finale (Approuvé/Refusé) et publie `LoanDecisionFinalized`.

---

## 🛠️ Installation et Démarrage

### Prérequis

* Docker & Docker Compose
* Python 3.10+
* Clé API Anthropic Claude (recommandé) ou OpenAI (voir [07-Constitution.md](./07-Constitution.md) pour la matrice des modèles)

### 1. Lancer l'infrastructure (Système Nerveux)

```bash
docker-compose up -d
# Ceci démarre Kafka, Zookeeper et le Schema Registry

```

### 2. Initialiser l'environnement

```bash
pip install -r requirements.txt
cp .env.example .env
# Configurez votre ANTHROPIC_API_KEY (ou OPENAI_API_KEY) dans le fichier .env

```

### 3. Enregistrer les schémas

```bash
python scripts/register_schemas.py

```

### 4. Lancer les Agents

Dans des terminaux séparés :

```bash
# Terminal 1
python src/agents/intake_agent/main.py

# Terminal 2
python src/agents/risk_agent/main.py

# Terminal 3
python src/agents/decision_agent/main.py

```

---

## 🧪 Stratégie d'Évaluation (AgentOps)

Nous appliquons le **Diamant de l'Évaluation Agentique** pour garantir la qualité :

1. **Tests Unitaires :** Validation du code Python (connexion Kafka, parsing).
2. **Évaluation Cognitive :** Utilisation d'un LLM-Juge pour vérifier que l'Agent Risque respecte bien la politique de crédit (Factualité).
3. **Simulation :** Injection de 50 demandes variées pour observer le comportement global du maillage.

Pour lancer la suite d'évaluation :

```bash
pytest tests/evaluation/

```

---

## 🛡️ Sécurité (AgentSec)

* Chaque agent possède une identité propre (Service Account simulé).
* Les agents ne communiquent jamais directement entre eux (pas d'appels HTTP directs), uniquement via le Broker (Zero Trust Network).
* Filtrage des inputs pour détecter les tentatives de *Jailbreak*.

---

## 📚 Documentation Complète

Pour approfondir chaque aspect du projet, consultez :

| Document | Description |
| --- | --- |
| [01-ArchitectureDecisions.md](./01-ArchitectureDecisions.md) | Décisions architecturales (ADRs) justifiant Kafka, Avro, ReAct |
| [02-DataContracts.md](./02-DataContracts.md) | Schémas Avro et topologie des Topics Kafka |
| [03-AgentSpecs.md](./03-AgentSpecs.md) | Spécifications cognitives et System Prompts des agents |
| [04-EvaluationStrategie.md](./04-EvaluationStrategie.md) | Stratégie de test AgentOps (Diamant de l'Évaluation) |
| [05-ThreatModel.md](./05-ThreatModel.md) | Modèle de menaces et sécurité AgentSec |
| [06-Plan.md](./06-Plan.md) | **Plan d'implémentation** - Feuille de route détaillée |
| [07-Constitution.md](./07-Constitution.md) | **Constitution** - Standards et règles fondamentales |

---

## 👥 Auteurs et Références

Projet réalisé dans le cadre académique sur l'architecture des systèmes agentiques.

* **Basé sur les travaux de :** André-Guy Bruneau (Architecture – Maillage Agentique et AgentOps).
* **Stack IA :** Anthropic Claude (Opus 4.5, Sonnet, Haiku) + Claude Code + Auto Claude.
* **Licence :** MIT.

---

## 📚 Navigation

| 🏠 Ce document | ➡️ Suivant |
|:---:|---:|
| **Index de la documentation** | [01-ArchitectureDecisions.md](./01-ArchitectureDecisions.md) |