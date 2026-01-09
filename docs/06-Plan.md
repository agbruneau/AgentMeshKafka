# Plan d'Implémentation - Projet AgentMeshKafka

> **Version :** 1.0.0 | **Statut :** En cours | **Dernière révision :** Janvier 2026
>
> **Documents connexes :** [00-Readme.md](./00-Readme.md) | [07-Constitution.md](./07-Constitution.md)

Ce document sert de **Feuille de Route (Roadmap)** pour l'exécution du projet. Il est divisé en phases logiques, allant de l'infrastructure (Système Nerveux) vers l'intelligence (Cerveau) et la validation (Système Immunitaire), suivant une approche itérative **"Bottom-Up"**.
**Objectif :** Livrer un POC fonctionnel démontrant l'interopérabilité d'agents autonomes via un backbone Kafka sécurisé.

---

## 📅 Phase 0 : Initialisation & Environnement

**Objectif :** Mettre en place le socle technique et les outils de développement.

* [ ] **0.1 Setup Repository**
* [ ] Initialiser Git (`git init`).
* [ ] Créer la structure de dossiers (`docs/`, `src/`, `schemas/`, `tests/`).
* [ ] Rédiger le `README.md` initial.


* [ ] **0.2 Infrastructure Locale (Docker)**
* [ ] Configurer `docker-compose.yml` (Zookeeper, Kafka Broker, Schema Registry, Control Center).
* [ ] Vérifier la bonne santé des conteneurs (`docker ps`).


* [ ] **0.3 Environnement Python**
* [ ] Créer un `virtualenv`.
* [ ] Définir `requirements.txt` (confluent-kafka, langchain, pydantic, openai, pytest, chromadb).
* [ ] Configurer les variables d'environnement (`.env`) pour les clés API.



---

## 🧠 Phase 1 : Le Système Nerveux (Data & Kafka)

**Objectif :** Établir les contrats d'interface stricts avant de coder l'intelligence. *Schema-First Design.*

* [ ] **1.1 Définition des Schémas (Avro)**
* [ ] Rédiger `schemas/loan_application.avsc` (Demande).
* [ ] Rédiger `schemas/risk_assessment.avsc` (Risque).
* [ ] Rédiger `schemas/loan_decision.avsc` (Décision).


* [ ] **1.2 Enregistrement & Topologie**
* [ ] Créer un script `scripts/init_kafka.py` pour créer les Topics avec les bonnes rétentions.
* [ ] Enregistrer les schémas dans le Schema Registry local.


* [ ] **1.3 Génération de Code**
* [ ] Générer les classes Python (Pydantic models) à partir des fichiers Avro pour assurer le typage dans le code.



---

## 🤖 Phase 2 : Le Cerveau (Développement des Agents)

**Objectif :** Implémenter la logique cognitive des 3 agents selon le pattern ReAct.

* [ ] **2.1 Agent Intake (Le Gatekeeper)**
* [ ] Implémenter le Consumer (Source externe) et le Producer (Kafka).
* [ ] Ajouter la validation structurelle (Pydantic).
* [ ] *Livrable :* L'agent publie un JSON valide dans `finance.loan.application.v1`.


* [ ] **2.2 Base de Connaissance (RAG)**
* [ ] Créer une base vectorielle (ChromaDB locale).
* [ ] Ingérer le document PDF "Politique de Crédit" (chunking + embedding).
* [ ] Créer l'outil de recherche `search_credit_policy`.


* [ ] **2.3 Agent Risk Analyst (Le Coeur Cognitif)**
* [ ] Configurer LangChain/LangGraph avec le System Prompt "Analyste".
* [ ] Connecter les outils : RAG + Calculatrice.
* [ ] Implémenter la boucle de consommation Kafka  Réflexion  Production.


* [ ] **2.4 Agent Loan Officer (Le Décideur)**
* [ ] Implémenter la logique de décision finale (Seuils d'approbation).
* [ ] Publier la décision finale.



---

## 🛡️ Phase 3 : Le Système Immunitaire (AgentOps & Sec)

**Objectif :** Sécuriser et fiabiliser le maillage (Passage du POC à la "Prod académique").

* [ ] **3.1 Tests Unitaires & Intégration**
* [ ] Écrire les tests pour les outils (calculs mathématiques).
* [ ] Écrire les tests de sérialisation/désérialisation Avro.


* [ ] **3.2 Pipeline d'Évaluation (Le Diamant)**
* [ ] Configurer "LLM-as-a-Judge" (ex: via DeepEval).
* [ ] Créer un dataset de 10 cas de tests (Golden Dataset).
* [ ] Exécuter l'évaluation de factualité sur l'Agent Risque.


* [ ] **3.3 Garde-fous (Security)**
* [ ] Implémenter la validation des inputs (Nettoyage XML/HTML).
* [ ] Tester une injection de prompt simple ("Ignore instructions").



---

## 🚀 Phase 4 : Orchestration & Démonstration

**Objectif :** Prouver que le système fonctionne de bout en bout.

* [ ] **4.1 Script de Simulation**
* [ ] Créer `scripts/simulate_traffic.py` pour injecter 50 demandes variées.


* [ ] **4.2 Observabilité**
* [ ] Mettre en place un logging structuré pour suivre la `trace_id` à travers les 3 agents.
* [ ] (Optionnel) Visualiser les flux dans Confluent Control Center.


* [ ] **4.3 Rapport Final**
* [ ] Compiler les résultats des tests d'évaluation.
* [ ] Rédiger la conclusion du projet académique.



---

## 📦 Livrables Finaux

1. Code source complet (GitHub).
2. Documentation technique (`/docs`).
3. Rapport d'exécution des tests (Preuve de fiabilité).
4. Vidéo/Démo du flux de données en temps réel.

---

## 📚 Navigation

| ⬅️ Précédent | 🏠 Index | ➡️ Suivant |
|:---|:---:|---:|
| [05-ThreatModel.md](./05-ThreatModel.md) | [Documentation](./00-Readme.md#-documentation-complète) | [07-Constitution.md](./07-Constitution.md) |