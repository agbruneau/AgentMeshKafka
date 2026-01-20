# PRD - Application d'Apprentissage de l'Interopérabilité en Écosystème d'Entreprise

## 1. Vision et Objectifs

### 1.1 Vision
Créer une plateforme d'apprentissage interactive permettant aux architectes d'entreprise de maîtriser les **trois piliers de l'intégration d'entreprise** :
- **Intégration des Applications** (Application Integration)
- **Intégration des Événements** (Event Integration)
- **Intégration des Données** (Data Integration)

Le tout à travers un environnement sandbox simulant un écosystème d'assurance dommage complet.

### 1.2 Les Trois Piliers de l'Intégration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INTEROPÉRABILITÉ EN ENTREPRISE                           │
├─────────────────────┬─────────────────────┬─────────────────────────────────┤
│                     │                     │                                 │
│   🔗 INTÉGRATION    │   ⚡ INTÉGRATION    │   📊 INTÉGRATION               │
│   APPLICATIONS      │   ÉVÉNEMENTS        │   DONNÉES                       │
│                     │                     │                                 │
│   • API REST/SOAP   │   • Event-Driven    │   • ETL/ELT                    │
│   • API Gateway     │   • Pub/Sub         │   • CDC                        │
│   • Service Mesh    │   • Event Sourcing  │   • Data Pipeline              │
│   • Orchestration   │   • Streaming       │   • Master Data                │
│   • BPM/Workflow    │   • Message Queue   │   • Data Lake                  │
│   • ESB patterns    │   • CQRS            │   • Data Virtualization        │
│                     │                     │                                 │
│   Synchrone +       │   Asynchrone        │   Batch + Near                 │
│   Requête/Réponse   │   Découplé          │   Real-time                    │
│                     │                     │                                 │
└─────────────────────┴─────────────────────┴─────────────────────────────────┘
```

### 1.3 Objectifs Principaux
- **Éducatif** : Transmettre les concepts théoriques des trois domaines d'intégration
- **Pratique** : Offrir un environnement sandbox pour expérimenter chaque type d'intégration
- **Métier** : Contextualiser l'apprentissage dans le domaine de l'assurance dommage
- **Progressif** : Guider l'apprenant dans un parcours structuré couvrant les trois piliers
- **Holistique** : Démontrer comment les trois approches se complètent dans un écosystème réel

### 1.4 Principes Directeurs

| Principe | Description |
|----------|-------------|
| **Simplicité** | Focus sur les concepts, simulations simplifiées, code monolithique |
| **Autonomie** | 100% offline, auto-suffisant, pas de dépendances externes |
| **Liberté** | Navigation libre, pas d'évaluation formelle, pas de gamification |
| **Expérience** | Interface moderne sombre, animations expressives, feedback visuel |

---

## 2. Public Cible

### 2.1 Persona Principal
**Architecte d'Entreprise / Architecte Solutions**
- Expérience : 3-10 ans en IT
- Besoin : Comprendre et concevoir des architectures d'intégration
- Contexte : Projets de transformation digitale, modernisation de SI

### 2.2 Prérequis Attendus
- Connaissances de base en développement logiciel
- Compréhension des concepts REST/HTTP
- Familiarité avec les bases de données relationnelles

---

## 3. Domaine Métier - Assurance Dommage

### 3.0 Spécifications Domaine Métier

| Aspect | Spécification |
|--------|---------------|
| **Fidélité** | Simplifiée - entités basiques sans complexité réelle |
| **Terminologie** | Générique - Client, Contrat, Réclamation (compréhensible par tous) |
| **Règles métier** | Basiques - quelques règles simples (ex: prime selon âge) |
| **Produits** | Auto + Habitation - deux lignes de produits IARD classiques |
| **Données test** | Fixes et prédéfinies - non modifiables |

### 3.1 Processus Métier Couverts

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  QUOTATION  │───▶│ SOUSCRIPTION │───▶│   POLICE    │
│  (Devis)    │    │ (Underwriting)│   │  (Policy)   │
└─────────────┘    └──────────────┘    └──────┬──────┘
                                              │
                   ┌──────────────────────────┼──────────────────────────┐
                   │                          │                          │
                   ▼                          ▼                          ▼
            ┌─────────────┐           ┌─────────────┐           ┌─────────────┐
            │ RÉCLAMATION │           │ FACTURATION │           │RENOUVELLEMENT│
            │   (Claim)   │           │  (Billing)  │           │  (Renewal)   │
            └─────────────┘           └─────────────┘           └─────────────┘
```

### 3.2 Entités Métier Principales

| Entité | Description | Attributs Clés |
|--------|-------------|----------------|
| **Quote** | Devis d'assurance | ID, client, risque, prime estimée, validité |
| **Policy** | Police d'assurance | Numéro, assuré, garanties, période, statut |
| **Claim** | Déclaration de sinistre | Numéro, police, date sinistre, description, montant |
| **Invoice** | Facture de prime | Numéro, police, montant, échéance, statut |
| **Customer** | Client assuré | ID, nom, coordonnées, historique |

### 3.3 Systèmes Simulés (Mock Services)

| Système | Rôle | APIs Exposées |
|---------|------|---------------|
| **Quote Engine** | Calcul des devis | POST /quotes, GET /quotes/{id} |
| **Policy Admin System (PAS)** | Gestion des polices | CRUD /policies |
| **Claims Management** | Gestion des sinistres | POST /claims, PUT /claims/{id}/status |
| **Billing System** | Facturation | POST /invoices, GET /invoices/policy/{id} |
| **Customer Hub** | Référentiel clients | CRUD /customers |
| **Document Management** | GED | POST /documents, GET /documents/{id} |
| **Notification Service** | Envoi notifications | POST /notifications |
| **External Rating API** | Tarification externe | GET /rates |

---

## 4. Les Trois Domaines d'Intégration

### 4.1 PILIER 1 : Intégration des Applications (Application Integration)

L'intégration des applications permet aux systèmes de communiquer entre eux de manière **synchrone** ou **asynchrone** via des interfaces bien définies.

#### 4.1.1 Concepts Fondamentaux

| Concept | Description | Contexte Assurance |
|---------|-------------|-------------------|
| **Couplage** | Degré de dépendance entre systèmes | PAS ↔ Quote Engine |
| **Contrat d'interface** | Spécification API formelle | OpenAPI pour partenaires |
| **Versioning** | Gestion des évolutions d'API | v1/v2 des APIs courtiers |
| **Service Discovery** | Localisation dynamique des services | Registre des microservices |
| **Load Balancing** | Distribution de charge | Répartition quotations |

#### 4.1.2 Patterns d'Intégration Applicative

| Pattern | Description | Cas d'Usage Assurance | Type |
|---------|-------------|----------------------|------|
| **API Gateway** | Point d'entrée unique | Façade unifiée partenaires | Synchrone |
| **Backend for Frontend (BFF)** | API par canal | API mobile vs API courtier | Synchrone |
| **Service Mesh** | Infrastructure de communication | Observabilité inter-services | Synchrone |
| **API Composition** | Agrégation de données | Vue 360° client | Synchrone |
| **Adapter/Wrapper** | Adaptation d'interface | Legacy mainframe → REST | Synchrone |
| **Anti-Corruption Layer** | Protection du domaine | Isolation système tiers | Synchrone |
| **Ambassador** | Proxy sidecar | Authentification externalisée | Synchrone |
| **Strangler Fig** | Migration progressive | Modernisation PAS legacy | Synchrone |

#### 4.1.3 Styles d'API

| Style | Caractéristiques | Usage Assurance |
|-------|-----------------|-----------------|
| **REST** | Ressources, HTTP verbs, stateless | CRUD polices, clients |
| **GraphQL** | Requêtes flexibles, schéma typé | Portail client personnalisé |
| **gRPC** | Binaire, performant, streaming | Communication inter-microservices |
| **SOAP** | XML, WS-*, contrats stricts | Intégration legacy, partenaires B2B |
| **OData** | REST enrichi, requêtage avancé | Exposition données reporting |

#### 4.1.4 Scénarios Sandbox - Applications

| ID | Scénario | Objectif d'Apprentissage |
|----|----------|-------------------------|
| **APP-01** | Création API REST Quote Engine | Design API, documentation OpenAPI |
| **APP-02** | API Gateway avec routing | Routage, rate limiting, auth |
| **APP-03** | BFF Mobile vs Courtier | Adaptation par canal |
| **APP-04** | API Composition vue client | Agrégation multi-sources |
| **APP-05** | Migration Strangler Fig | Cohabitation legacy/moderne |
| **APP-06** | Service Mesh basique | Observabilité, retry |

---

### 4.2 PILIER 2 : Intégration des Événements (Event Integration)

L'intégration par événements permet un découplage fort entre producteurs et consommateurs via des **messages asynchrones**.

#### 4.2.1 Concepts Fondamentaux

| Concept | Description | Contexte Assurance |
|---------|-------------|-------------------|
| **Événement métier** | Fait significatif survenu | PolicyCreated, ClaimSubmitted |
| **Producteur/Consommateur** | Émetteur/Récepteur découplés | PAS → Billing, Notifications |
| **Topic/Queue** | Canal de distribution | topic.policies, queue.claims |
| **Garantie de livraison** | At-least-once, exactly-once | Criticité facturation |
| **Ordering** | Ordre des messages | Séquence modifications police |
| **Idempotence** | Traitement répété sans effet | Relance safe |

#### 4.2.2 Patterns d'Intégration Événementielle

| Pattern | Description | Cas d'Usage Assurance | Type |
|---------|-------------|----------------------|------|
| **Message Queue** | File point-à-point | Traitement souscriptions | Async |
| **Publish/Subscribe** | Diffusion multi-consommateurs | Notification création police | Async |
| **Event-Driven Architecture** | Architecture réactive | Cycle de vie police | Async |
| **Event Sourcing** | État = séquence d'événements | Audit trail complet | Async |
| **CQRS** | Séparation commande/requête | Transactions vs reporting | Async |
| **Saga Pattern** | Transactions distribuées | Souscription multi-étapes | Async |
| **Outbox Pattern** | Fiabilité publication | Garantie événement publié | Async |
| **Event Notification** | Signal léger | Trigger consultation API | Async |
| **Event-Carried State Transfer** | Données complètes dans événement | Autonomie consommateur | Async |
| **Dead Letter Queue** | Gestion erreurs | Messages non traitables | Async |
| **Competing Consumers** | Parallélisation | Scale-out traitement claims | Async |

#### 4.2.3 Taxonomie des Événements

```
ÉVÉNEMENTS MÉTIER (Domain Events)
├── Événements de Cycle de Vie
│   ├── QuoteCreated, QuoteExpired
│   ├── PolicyIssued, PolicyCancelled, PolicyRenewed
│   ├── ClaimOpened, ClaimAssessed, ClaimSettled
│   └── InvoiceGenerated, PaymentReceived
│
├── Événements de Changement d'État
│   ├── PolicyStatusChanged
│   ├── ClaimStatusChanged
│   └── CustomerAddressUpdated
│
└── Événements d'Intégration
    ├── ExternalRatingReceived
    ├── DocumentUploaded
    └── NotificationSent

ÉVÉNEMENTS TECHNIQUES (Infrastructure Events)
├── ServiceStarted, ServiceStopped
├── CircuitBreakerTripped
└── RetryExhausted
```

#### 4.2.4 Scénarios Sandbox - Événements

| ID | Scénario | Objectif d'Apprentissage |
|----|----------|-------------------------|
| **EVT-01** | Pub/Sub PolicyCreated | Publication/souscription basique |
| **EVT-02** | Queue traitement claims | Point-à-point, competing consumers |
| **EVT-03** | Event Sourcing police | Reconstruction état, replay |
| **EVT-04** | Saga souscription | Transactions distribuées, compensation |
| **EVT-05** | CQRS reporting | Séparation modèles lecture/écriture |
| **EVT-06** | Outbox pattern | Fiabilité atomique DB + événement |
| **EVT-07** | Dead Letter handling | Gestion erreurs, retry strategies |

---

### 4.3 PILIER 3 : Intégration des Données (Data Integration)

L'intégration des données assure la **cohérence**, la **disponibilité** et la **qualité** des données à travers l'écosystème.

#### 4.3.1 Concepts Fondamentaux

| Concept | Description | Contexte Assurance |
|---------|-------------|-------------------|
| **Master Data** | Données de référence | Client, Produit, Garantie |
| **Data Quality** | Qualité des données | Validation adresse, complétude |
| **Data Lineage** | Traçabilité des données | Origine prime calculée |
| **Data Governance** | Gouvernance | Ownership, accès, rétention |
| **Latence** | Fraîcheur des données | Temps réel vs batch |
| **Consistance** | Cohérence inter-systèmes | Même client partout |

#### 4.3.2 Patterns d'Intégration de Données

| Pattern | Description | Cas d'Usage Assurance | Type |
|---------|-------------|----------------------|------|
| **ETL** | Extract-Transform-Load | Alimentation datawarehouse | Batch |
| **ELT** | Extract-Load-Transform | Data lake analytics | Batch |
| **CDC (Change Data Capture)** | Capture incrémentale | Sync temps réel PAS → DWH | Near RT |
| **Data Pipeline** | Flux de données orchestré | Traitement renouvellements | Batch |
| **Data Virtualization** | Vue unifiée sans copie | Fédération sources clients | Real-time |
| **Data Replication** | Copie synchronisée | DR, lecture locale | Async |
| **Materialized View** | Vue pré-calculée | Dashboard sinistralité | Near RT |
| **Data Lake** | Stockage brut massif | Historique complet | Batch |
| **Data Mesh** | Domaines autonomes | Données par département | Federated |
| **Master Data Management** | Référentiel unique | Golden record client | Real-time |

#### 4.3.3 Modèles de Flux de Données

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    FLUX DE DONNÉES ASSURANCE                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  SYSTÈMES SOURCES              INTÉGRATION              CIBLES          │
│  ─────────────────            ───────────            ────────          │
│                                                                         │
│  ┌─────────┐                  ┌─────────┐           ┌─────────┐        │
│  │   PAS   │───CDC───────────▶│         │──────────▶│   DWH   │        │
│  └─────────┘                  │         │           └─────────┘        │
│                               │  Data   │                              │
│  ┌─────────┐                  │  Hub    │           ┌─────────┐        │
│  │ Claims  │───ETL (nuit)────▶│         │──────────▶│ DataMart│        │
│  └─────────┘                  │         │           │Sinistres│        │
│                               │         │           └─────────┘        │
│  ┌─────────┐                  │         │                              │
│  │ Billing │───Streaming─────▶│         │           ┌─────────┐        │
│  └─────────┘                  │         │──────────▶│ Reporting│       │
│                               └─────────┘           │   BI    │        │
│  ┌─────────┐                       │                └─────────┘        │
│  │External │                       │                                   │
│  │ Rating  │───API Batch───────────┘                ┌─────────┐        │
│  └─────────┘                                        │ ML/AI   │        │
│                                                     │ Models  │        │
│                                                     └─────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 4.3.4 Scénarios Sandbox - Données

| ID | Scénario | Objectif d'Apprentissage |
|----|----------|-------------------------|
| **DATA-01** | ETL batch sinistres | Pipeline ETL classique |
| **DATA-02** | CDC temps réel polices | Capture incrémentale, Debezium |
| **DATA-03** | Data pipeline renouvellements | Orchestration, dépendances |
| **DATA-04** | MDM client | Golden record, matching, merge |
| **DATA-05** | Data quality checks | Validation, profiling, alerting |
| **DATA-06** | Data virtualization | Vue fédérée multi-sources |
| **DATA-07** | Data lineage | Traçabilité bout-en-bout |

---

### 4.4 Matrice de Décision : Quel Type d'Intégration ?

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                     ARBRE DE DÉCISION INTÉGRATION                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Quel est le besoin principal ?                                              │
│  │                                                                           │
│  ├─▶ Appeler une fonction/service d'un autre système                         │
│  │   └─▶ 🔗 INTÉGRATION APPLICATIONS                                         │
│  │       ├─ Réponse immédiate requise ? → REST/gRPC synchrone               │
│  │       └─ Peut attendre ? → Message Queue (request-reply)                  │
│  │                                                                           │
│  ├─▶ Réagir à quelque chose qui s'est passé                                  │
│  │   └─▶ ⚡ INTÉGRATION ÉVÉNEMENTS                                           │
│  │       ├─ Plusieurs consommateurs ? → Pub/Sub                              │
│  │       ├─ Un seul consommateur ? → Queue                                   │
│  │       └─ Workflow long ? → Saga                                           │
│  │                                                                           │
│  └─▶ Synchroniser/Analyser des données entre systèmes                        │
│      └─▶ 📊 INTÉGRATION DONNÉES                                              │
│          ├─ Temps réel requis ? → CDC/Streaming                              │
│          ├─ Nuit/batch OK ? → ETL                                            │
│          └─ Sans copie ? → Data Virtualization                               │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 4.5 Comparatif des Trois Approches

| Critère | Applications | Événements | Données |
|---------|--------------|------------|---------|
| **Couplage** | Moyen-Fort | Faible | Variable |
| **Latence** | Temps réel | Near real-time | Batch à temps réel |
| **Volume** | Transactionnel | Transactionnel | Massif |
| **Complexité** | Moyenne | Haute | Haute |
| **Cas d'usage** | Requête/Réponse | Réaction, Workflow | Analytics, Sync |
| **Outils typiques** | API Gateway, ESB | Kafka, RabbitMQ | Talend, Spark |
| **Granularité** | Opération | Événement | Dataset |

---

## 5. Patterns Transversaux (Cross-Cutting)

### 5.1 Patterns de Résilience

| Pattern | Description | Cas d'Usage Assurance | Pilier |
|---------|-------------|----------------------|--------|
| **Circuit Breaker** | Coupe-circuit | Protection appels tarificateur externe | App/Event |
| **Retry with Backoff** | Réessai progressif | Appels services tiers | App/Event |
| **Bulkhead** | Isolation des ressources | Séparation quotation/claims | App |
| **Timeout** | Délai maximum | SLA sur réponse devis | App |
| **Fallback** | Solution de repli | Cache tarifs si API indisponible | App |
| **Idempotent Receiver** | Traitement répété safe | Retraitement messages | Event |
| **Transactional Outbox** | Atomicité DB + message | Cohérence publication | Event/Data |

### 5.2 Patterns d'Orchestration

| Pattern | Description | Cas d'Usage Assurance | Pilier |
|---------|-------------|----------------------|--------|
| **Orchestration** | Coordination centralisée | Workflow de souscription | App/Event |
| **Choreography** | Coordination décentralisée | Événements entre domaines | Event |
| **Process Manager** | Gestionnaire de processus | Suivi dossier sinistre | Event |
| **State Machine** | Machine à états | Cycle de vie réclamation | Event |
| **Scheduler** | Planification jobs | Batch nocturne | Data |

### 5.3 Patterns de Sécurité

| Pattern | Description | Cas d'Usage Assurance | Pilier |
|---------|-------------|----------------------|--------|
| **API Key** | Authentification simple | Partenaires externes | App |
| **OAuth 2.0 / OIDC** | Délégation auth | SSO courtiers | App |
| **JWT** | Token auto-contenu | Inter-services | App |
| **mTLS** | Auth mutuelle | Service-to-service | App |
| **Encryption at Rest** | Chiffrement stockage | Données sensibles | Data |
| **Data Masking** | Masquage données | Environnements non-prod | Data |

---

## 6. Architecture Technique

### 6.1 Stack Technologique

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERFACE UTILISATEUR                     │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Tailwind CSS│  │    HTMX     │  │    D3.js    │         │
│  │  (styling)  │  │(interactif) │  │ (diagrammes)│         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│  Lucide Icons │ Thème sombre │ Panneaux redimensionnables   │
└─────────────────────────────────────────────────────────────┘
                              │
                         SSE (temps réel)
                              │
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION BACKEND                       │
│                    Python 3.11+ / FastAPI                    │
│                    (Structure monolithique simple)           │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Modules   │  │   Sandbox   │  │    Mock     │         │
│  │  (Markdown) │  │ (In-memory) │  │  Services   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│  Message Broker: Simulation pure Python (in-memory)         │
│  État sandbox: En mémoire (reset au redémarrage)            │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    STOCKAGE LOCAL                            │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   SQLite    │  │ LocalStorage│  │  Markdown   │         │
│  │ (SQL brut)  │  │(préférences)│  │  (contenu)  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Justification des Choix Techniques

| Technologie | Raison | Alternative Écartée |
|-------------|--------|---------------------|
| **Python 3.11+** | Simple, lisible, facile sur Windows | Node.js (plus complexe) |
| **FastAPI** | Moderne, async natif, SSE intégré | Flask (moins moderne) |
| **SQLite brut** | Zéro config, requêtes SQL transparentes | ORM (abstraction inutile) |
| **In-memory Python** | Zéro dépendance, simulation suffisante | Redis (installation requise) |
| **HTMX** | Interactivité sans JS complexe | React/Vue (overkill) |
| **Tailwind CSS** | Rapide, moderne, thème sombre facile | Bootstrap (moins flexible) |
| **D3.js** | Diagrammes interactifs puissants | Mermaid (moins interactif) |
| **Lucide Icons** | Moderne, léger, grande variété | Font Awesome (plus lourd) |
| **SSE** | Simple, unidirectionnel, natif HTTP | WebSocket (bidirectionnel inutile) |
| **Markdown** | Facile à éditer, rendu automatique | HTML (plus verbeux) |
| **LocalStorage** | Simple pour préférences utilisateur | SQLite (overkill) |

### 6.3 Principes d'Architecture

| Principe | Application |
|----------|-------------|
| **Monolithique simple** | Tout dans quelques fichiers, pas de microservices |
| **État en mémoire** | Sandbox reset à chaque démarrage, pas de persistance complexe |
| **Typage minimal** | Pas de type hints partout, code plus court |
| **Configuration constantes** | Fichier config.py simple, pas de .env |
| **100% Offline** | Aucune dépendance réseau après installation |

### 6.4 Structure du Projet

```
interop-learning/
├── app/
│   ├── main.py                     # Point d'entrée FastAPI
│   ├── config.py                   # Configuration
│   │
│   ├── theory/                     # Modules théoriques
│   │   ├── content/                # Contenu markdown par module
│   │   │   ├── 01_introduction/
│   │   │   ├── 02_domaine_assurance/
│   │   │   ├── 03_rest_api/
│   │   │   ├── ...
│   │   │   └── 16_projet_final/
│   │   └── renderer.py             # Rendu markdown → HTML
│   │
│   ├── sandbox/                    # Moteur de simulation
│   │   ├── engine.py               # Orchestrateur sandbox
│   │   ├── visualizer.py           # Visualisation flux
│   │   └── scenarios/              # Scénarios par pilier
│   │       ├── applications/       # APP-01 à APP-05
│   │       ├── events/             # EVT-01 à EVT-06
│   │       ├── data/               # DATA-01 à DATA-05
│   │       └── cross_cutting/      # CROSS-01 à CROSS-04
│   │
│   ├── mocks/                      # Services simulés (assurance)
│   │   ├── quote_engine.py         # Moteur de devis
│   │   ├── policy_admin.py         # Administration polices
│   │   ├── claims.py               # Gestion sinistres
│   │   ├── billing.py              # Facturation
│   │   ├── customer_hub.py         # Référentiel clients
│   │   ├── document_mgmt.py        # GED
│   │   ├── notifications.py        # Service notifications
│   │   └── external_rating.py      # API tarification externe
│   │
│   ├── integration/                # Implémentations des 3 piliers
│   │   │
│   │   ├── applications/           # 🔗 PILIER APPLICATIONS
│   │   │   ├── gateway.py          # API Gateway simulation
│   │   │   ├── composition.py      # API Composition
│   │   │   ├── bff.py              # Backend for Frontend
│   │   │   └── acl.py              # Anti-Corruption Layer
│   │   │
│   │   ├── events/                 # ⚡ PILIER ÉVÉNEMENTS
│   │   │   ├── message_queue.py    # Queue point-à-point
│   │   │   ├── pubsub.py           # Publish/Subscribe
│   │   │   ├── event_store.py      # Event Sourcing
│   │   │   ├── saga.py             # Saga orchestration
│   │   │   ├── cqrs.py             # CQRS simulation
│   │   │   └── outbox.py           # Outbox pattern
│   │   │
│   │   ├── data/                   # 📊 PILIER DONNÉES
│   │   │   ├── etl_pipeline.py     # Pipeline ETL
│   │   │   ├── cdc_simulator.py    # Change Data Capture
│   │   │   ├── data_quality.py     # Contrôles qualité
│   │   │   ├── mdm.py              # Master Data Management
│   │   │   └── lineage.py          # Data Lineage
│   │   │
│   │   └── cross_cutting/          # Patterns transversaux
│   │       ├── circuit_breaker.py
│   │       ├── retry.py
│   │       ├── observability.py
│   │       └── security.py
│   │
│   ├── api/                        # Routes API internes
│   │   ├── theory.py               # API modules théoriques
│   │   ├── sandbox.py              # API sandbox
│   │   └── progress.py             # API progression
│   │
│   └── templates/                  # Templates HTML (Jinja2)
│       ├── base.html
│       ├── theory/
│       ├── sandbox/
│       │   ├── applications.html
│       │   ├── events.html
│       │   ├── data.html
│       │   └── visualizer.html
│       └── components/
│
├── static/                         # Assets statiques
│   ├── css/
│   ├── js/
│   │   ├── sandbox-engine.js
│   │   └── flow-visualizer.js
│   └── diagrams/
│
├── data/                           # Données
│   ├── learning.db                 # SQLite - progression
│   ├── mock_data/                  # Données mock assurance
│   │   ├── customers.json
│   │   ├── policies.json
│   │   ├── claims.json
│   │   └── invoices.json
│   └── scenarios/                  # État des scénarios
│
├── tests/                          # Tests
│   ├── test_applications/
│   ├── test_events/
│   ├── test_data/
│   └── test_sandbox/
│
├── docs/                           # Documentation
│   ├── architecture.md
│   └── patterns/
│
├── requirements.txt                # Dépendances Python
├── README.md                       # Documentation
└── run.py                          # Script de lancement
```

---

## 7. Parcours Pédagogique

### 7.1 Vue d'Ensemble du Parcours

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PARCOURS D'APPRENTISSAGE                            │
│                    (16 Modules - 3 Piliers + Fondations)                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  NIVEAU 1 - FONDATIONS                                                      │
│  ══════════════════════                                                     │
│  [M1] Introduction  [M2] Écosystème Assurance                              │
│                                                                             │
│  NIVEAU 2 - INTÉGRATION APPLICATIONS  🔗                                    │
│  ═══════════════════════════════════════                                    │
│  [M3] REST API Design  [M4] API Gateway  [M5] Patterns Avancés             │
│                                                                             │
│  NIVEAU 3 - INTÉGRATION ÉVÉNEMENTS  ⚡                                      │
│  ═════════════════════════════════════                                      │
│  [M6] Messaging Basics  [M7] Event-Driven  [M8] Saga & Transactions        │
│                                                                             │
│  NIVEAU 4 - INTÉGRATION DONNÉES  📊                                         │
│  ════════════════════════════════                                           │
│  [M9] ETL & Batch  [M10] CDC & Streaming  [M11] Data Quality               │
│                                                                             │
│  NIVEAU 5 - PATTERNS TRANSVERSAUX                                          │
│  ═════════════════════════════════                                          │
│  [M12] Résilience  [M13] Observabilité  [M14] Sécurité                     │
│                                                                             │
│  NIVEAU 6 - SYNTHÈSE & ARCHITECTURE                                        │
│  ═══════════════════════════════════                                        │
│  [M15] Décisions d'Architecture  [M16] Projet Final                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Structure Détaillée du Parcours

```
══════════════════════════════════════════════════════════════════════════════
NIVEAU 1 - FONDATIONS (Modules 1-2)
══════════════════════════════════════════════════════════════════════════════

├── Module 1: Introduction à l'Interopérabilité
│   ├── 1.1 Qu'est-ce que l'interopérabilité ?
│   ├── 1.2 Les trois piliers : Applications, Événements, Données
│   ├── 1.3 Enjeux métier et techniques
│   └── 1.4 Vue d'ensemble des patterns
│       └── 🎮 Sandbox: Explorer l'écosystème simulé
│
└── Module 2: Domaine Métier - Assurance Dommage
    ├── 2.1 Processus métier (Quote → Policy → Claim → Billing)
    ├── 2.2 Entités et relations
    ├── 2.3 Systèmes typiques d'un assureur
    └── 2.4 Points d'intégration identifiés
        └── 🎮 Sandbox: Cartographie des flux métier

══════════════════════════════════════════════════════════════════════════════
NIVEAU 2 - INTÉGRATION APPLICATIONS 🔗 (Modules 3-5)
══════════════════════════════════════════════════════════════════════════════

├── Module 3: Design d'API REST
│   ├── 3.1 Principes REST et Richardson Maturity Model
│   ├── 3.2 Design de ressources (Nouns vs Verbs)
│   ├── 3.3 Versioning et évolution d'API
│   ├── 3.4 Documentation OpenAPI/Swagger
│   └── 3.5 Gestion des erreurs et codes HTTP
│       └── 🎮 Sandbox: Créer l'API du Quote Engine
│
├── Module 4: API Gateway et Patterns de Façade
│   ├── 4.1 Rôle et responsabilités de l'API Gateway
│   ├── 4.2 Routing et transformation
│   ├── 4.3 Rate limiting et throttling
│   ├── 4.4 Authentification et autorisation
│   └── 4.5 Backend for Frontend (BFF)
│       └── 🎮 Sandbox: Gateway unifié pour partenaires
│
└── Module 5: Patterns Avancés d'Intégration Applicative
    ├── 5.1 API Composition et agrégation
    ├── 5.2 Anti-Corruption Layer
    ├── 5.3 Strangler Fig Pattern
    ├── 5.4 Service Mesh introduction
    └── 5.5 GraphQL vs REST vs gRPC
        └── 🎮 Sandbox: Vue 360° client par composition

══════════════════════════════════════════════════════════════════════════════
NIVEAU 3 - INTÉGRATION ÉVÉNEMENTS ⚡ (Modules 6-8)
══════════════════════════════════════════════════════════════════════════════

├── Module 6: Fondamentaux du Messaging
│   ├── 6.1 Synchrone vs Asynchrone : quand choisir ?
│   ├── 6.2 Message Queue (Point-to-Point)
│   ├── 6.3 Publish/Subscribe (Topics)
│   ├── 6.4 Garanties de livraison (at-least-once, exactly-once)
│   └── 6.5 Idempotence et déduplication
│       └── 🎮 Sandbox: Queue pour traitement des souscriptions
│
├── Module 7: Architecture Event-Driven
│   ├── 7.1 Événements métier vs techniques
│   ├── 7.2 Event Notification vs Event-Carried State Transfer
│   ├── 7.3 Event Sourcing : l'état comme séquence d'événements
│   ├── 7.4 CQRS : séparer lectures et écritures
│   └── 7.5 Projection et reconstruction d'état
│       └── 🎮 Sandbox: Event Sourcing du cycle de vie police
│
└── Module 8: Transactions Distribuées et Saga
    ├── 8.1 Problème des transactions distribuées
    ├── 8.2 Saga Pattern : orchestration vs choreography
    ├── 8.3 Compensation et rollback
    ├── 8.4 Outbox Pattern pour fiabilité
    └── 8.5 Dead Letter Queue et error handling
        └── 🎮 Sandbox: Saga complète de souscription

══════════════════════════════════════════════════════════════════════════════
NIVEAU 4 - INTÉGRATION DONNÉES 📊 (Modules 9-11)
══════════════════════════════════════════════════════════════════════════════

├── Module 9: ETL et Traitement Batch
│   ├── 9.1 ETL vs ELT : concepts et différences
│   ├── 9.2 Design de pipelines ETL
│   ├── 9.3 Orchestration de jobs (scheduling, dépendances)
│   ├── 9.4 Gestion des erreurs et reprise
│   └── 9.5 Optimisation et parallélisation
│       └── 🎮 Sandbox: Pipeline batch renouvellements annuels
│
├── Module 10: CDC et Streaming de Données
│   ├── 10.1 Change Data Capture : principes
│   ├── 10.2 Log-based CDC vs Trigger-based
│   ├── 10.3 Streaming avec Kafka/alternatives
│   ├── 10.4 Data Pipeline temps réel
│   └── 10.5 Database per Service et synchronisation
│       └── 🎮 Sandbox: CDC temps réel PAS → Reporting
│
└── Module 11: Qualité et Gouvernance des Données
    ├── 11.1 Data Quality : dimensions et métriques
    ├── 11.2 Data Profiling et validation
    ├── 11.3 Master Data Management (MDM)
    ├── 11.4 Data Lineage et traçabilité
    └── 11.5 Data Governance : ownership et accès
        └── 🎮 Sandbox: Pipeline avec contrôles qualité

══════════════════════════════════════════════════════════════════════════════
NIVEAU 5 - PATTERNS TRANSVERSAUX (Modules 12-14)
══════════════════════════════════════════════════════════════════════════════

├── Module 12: Résilience et Tolérance aux Pannes
│   ├── 12.1 Circuit Breaker pattern
│   ├── 12.2 Retry avec backoff exponentiel
│   ├── 12.3 Timeout et Fallback
│   ├── 12.4 Bulkhead : isolation des ressources
│   └── 12.5 Chaos Engineering basics
│       └── 🎮 Sandbox: Résilience appels tarificateur externe
│
├── Module 13: Observabilité
│   ├── 13.1 Les trois piliers : Logs, Metrics, Traces
│   ├── 13.2 Logging structuré et corrélation
│   ├── 13.3 Distributed Tracing
│   ├── 13.4 Métriques et alerting
│   └── 13.5 Health checks et readiness probes
│       └── 🎮 Sandbox: Instrumenter l'écosystème complet
│
└── Module 14: Sécurité des Intégrations
    ├── 14.1 Authentification API (API Key, OAuth, JWT)
    ├── 14.2 Autorisation et RBAC
    ├── 14.3 Chiffrement en transit et au repos
    ├── 14.4 Sécurité des événements et messages
    └── 14.5 Audit et conformité
        └── 🎮 Sandbox: Sécuriser le gateway

══════════════════════════════════════════════════════════════════════════════
NIVEAU 6 - SYNTHÈSE ET ARCHITECTURE (Modules 15-16)
══════════════════════════════════════════════════════════════════════════════

├── Module 15: Décisions d'Architecture
│   ├── 15.1 Orchestration vs Choreography : critères de choix
│   ├── 15.2 Quand utiliser chaque type d'intégration
│   ├── 15.3 Trade-offs et compromis
│   ├── 15.4 Anti-patterns à éviter
│   └── 15.5 Architecture Decision Records (ADR)
│       └── 🎮 Sandbox: Documenter les choix d'architecture
│
└── Module 16: Projet Final - Écosystème Complet
    ├── 16.1 Cahier des charges
    ├── 16.2 Conception de l'architecture
    ├── 16.3 Implémentation guidée
    ├── 16.4 Tests et validation
    └── 16.5 Évaluation finale
        └── 🎮 Sandbox: Intégrer les trois piliers
```

### 7.3 Spécifications Contenu Théorique

| Aspect | Spécification |
|--------|---------------|
| **Format** | Modulaire - résumé + sections "En savoir plus" dépliables |
| **Diagrammes** | Interactifs (survol pour détails, zoom, clic pour naviguer) |
| **Code** | Pseudo-code uniquement (pas de langage spécifique) |
| **Ressources** | Auto-suffisant - tout le contenu dans l'app |
| **Évaluation** | Aucune - pas de quiz ni validation |
| **Gamification** | Aucune - pas de badges, points ou niveaux |
| **Navigation** | Totalement libre - accès à tous les modules dès le départ |
| **Temps estimé** | Non affiché |

### 7.4 Structure d'un Module Type

```
┌────────────────────────────────────────────────────────────┐
│                     MODULE N: [TITRE]                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  📚 THÉORIE                                                │
│  ├── Résumé (points clés, bullet points)                  │
│  ├── [+] En savoir plus (sections dépliables)             │
│  ├── Diagrammes interactifs                               │
│  ├── Pseudo-code illustratif                              │
│  └── Cas d'usage assurance                                │
│                                                            │
│  🎮 SANDBOX                                                │
│  ├── Objectif du scénario (6-10 étapes)                   │
│  ├── Contexte métier (assurance simplifiée)               │
│  ├── Guidance progressive (strict → libre)                │
│  ├── Visualisation hybride (diagrammes + logs)            │
│  ├── Replay animé avec timeline                           │
│  └── Auto-save de la progression                          │
│                                                            │
│  📖 DOCUMENTATION LIÉE                                     │
│  ├── Fiches patterns concernés                            │
│  ├── Glossaire termes utilisés                            │
│  └── Liens vers patterns connexes                         │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## 8. Fonctionnalités du Sandbox

### 8.1 Spécifications Sandbox Détaillées

#### Philosophie

| Aspect | Spécification |
|--------|---------------|
| **Réalisme** | Simplifié - flux linéaires, focus sur les concepts |
| **Persistance** | Session unique - reset complet à chaque démarrage |
| **Interaction** | GUI uniquement - pas de ligne de commande |
| **Guidance** | Progressive - strict au début, puis de plus en plus libre |
| **Erreurs** | Laisser échouer puis expliquer (pédagogie par l'échec) |
| **Mode libre** | Non - uniquement scénarios prédéfinis |

#### Simulation

| Aspect | Spécification |
|--------|---------------|
| **Latence** | Délais fixes par service (ex: 50ms, 100ms, 200ms) |
| **Pannes** | Aléatoires avec probabilité configurable |
| **Logs** | Détaillés - chaque étape intermédiaire visible |
| **Données visibles** | Abstrait - représentation simplifiée (icônes, noms) |
| **Message broker** | Simulation pure Python in-memory |
| **Format messages** | JSON simple (dictionnaires) |

#### Scénarios

| Aspect | Spécification |
|--------|---------------|
| **Nombre d'étapes** | 6-10 par scénario |
| **Sauvegarde** | Auto-save de l'état courant |
| **Données de test** | Fixes, non modifiables par l'apprenant |
| **Replay** | Animé avec timeline - rejouer visuellement les étapes |

### 8.2 Moteur de Simulation

#### Capacités Principales
- **Démarrage/Arrêt** des services mock individuellement
- **Données de test fixes** (clients, polices, sinistres)
- **Latence fixe** par service (non configurable par l'utilisateur)
- **Pannes aléatoires** avec probabilité prédéfinie
- **Visualisation temps réel** des flux (diagrammes + logs)

#### Interface de Contrôle

```
┌─────────────────────────────────────────────────────────────┐
│  SANDBOX CONTROL PANEL                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Services         Status      Latency    Actions            │
│  ─────────────────────────────────────────────────          │
│  Quote Engine     🟢 Running   50ms      [Stop] [Config]    │
│  Policy Admin     🟢 Running   30ms      [Stop] [Config]    │
│  Claims           🟡 Degraded  500ms     [Stop] [Config]    │
│  Billing          🔴 Stopped   -         [Start][Config]    │
│  Notifications    🟢 Running   20ms      [Stop] [Config]    │
│                                                             │
│  [Inject Failure: Quote Engine]  [Reset All]  [Load Scenario]│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8.3 Spécifications Visualisation D3.js

| Aspect | Spécification |
|--------|---------------|
| **Layout** | Force-directed (nœuds qui se repoussent/attirent) |
| **Services** | Boîtes rectangulaires avec icône + nom |
| **Connexions** | Lignes animées avec particules qui se déplacent |
| **Zoom/Pan** | Molette pour zoom, drag pour déplacer |
| **Queues** | Animation entrée/sortie des messages |
| **Couleurs** | Par pilier : 🔗 Bleu | ⚡ Orange | 📊 Vert |

### 8.4 Visualisation des Flux

```
┌─────────────────────────────────────────────────────────────┐
│  MESSAGE FLOW VISUALIZER                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│    [Client]                                                 │
│       │                                                     │
│       │ POST /quotes                                        │
│       ▼                                                     │
│  ┌─────────┐  ──PolicyCreated──▶  ┌─────────┐              │
│  │ Gateway │                      │ PubSub  │              │
│  └────┬────┘                      └────┬────┘              │
│       │                               │                     │
│       │ route                    ┌────┴────┬────┐          │
│       ▼                          ▼         ▼    ▼          │
│  ┌─────────┐               ┌───────┐ ┌───────┐ ┌───────┐   │
│  │  Quote  │               │Billing│ │ Notif │ │ Audit │   │
│  │ Engine  │               └───────┘ └───────┘ └───────┘   │
│  └─────────┘                                               │
│                                                             │
│  Timeline: ══════════════════════════════════════════▶     │
│            0ms   50ms   100ms   150ms   200ms              │
│                                                             │
│  Messages: [PolicyCreated] [InvoiceGenerated] [EmailSent]  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8.3 Scénarios Prédéfinis par Pilier

#### Scénarios Intégration Applications 🔗

| ID | Scénario | Patterns | Complexité |
|----|----------|----------|------------|
| **APP-01** | Création devis auto | REST, API Design | ⭐ |
| **APP-02** | Gateway multi-partenaires | API Gateway, Routing | ⭐⭐ |
| **APP-03** | BFF Mobile vs Portail | Backend for Frontend | ⭐⭐ |
| **APP-04** | Vue 360° client | API Composition | ⭐⭐⭐ |
| **APP-05** | Migration PAS legacy | Strangler Fig, ACL | ⭐⭐⭐ |

#### Scénarios Intégration Événements ⚡

| ID | Scénario | Patterns | Complexité |
|----|----------|----------|------------|
| **EVT-01** | Notification création police | Pub/Sub | ⭐ |
| **EVT-02** | Traitement claims async | Message Queue | ⭐⭐ |
| **EVT-03** | Historique police complet | Event Sourcing | ⭐⭐⭐ |
| **EVT-04** | Souscription multi-étapes | Saga Orchestration | ⭐⭐⭐ |
| **EVT-05** | Séparation transac/reporting | CQRS | ⭐⭐⭐ |
| **EVT-06** | Gestion erreurs messaging | DLQ, Retry | ⭐⭐ |

#### Scénarios Intégration Données 📊

| ID | Scénario | Patterns | Complexité |
|----|----------|----------|------------|
| **DATA-01** | Export sinistres nuit | ETL Batch | ⭐ |
| **DATA-02** | Sync polices temps réel | CDC | ⭐⭐ |
| **DATA-03** | Renouvellements massifs | Data Pipeline | ⭐⭐⭐ |
| **DATA-04** | Référentiel client unique | MDM | ⭐⭐⭐ |
| **DATA-05** | Contrôle qualité données | Data Quality | ⭐⭐ |

#### Scénarios Transversaux

| ID | Scénario | Patterns | Complexité |
|----|----------|----------|------------|
| **CROSS-01** | Panne tarificateur externe | Circuit Breaker, Fallback | ⭐⭐ |
| **CROSS-02** | Tracing distribué | Observability | ⭐⭐ |
| **CROSS-03** | Sécurisation gateway | OAuth, JWT | ⭐⭐ |
| **CROSS-04** | Écosystème complet | Tous patterns | ⭐⭐⭐⭐ |

---

## 9. Documentation En Ligne Intégrée

### 9.1 Vue d'Ensemble

L'application intègre une **documentation complète accessible directement depuis l'interface**, permettant aux apprenants de consulter les références sans quitter l'environnement d'apprentissage.

### 9.2 Structure de la Documentation

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DOCUMENTATION EN LIGNE                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📖 RÉFÉRENCE RAPIDE                                                        │
│  ├── Glossaire interactif (termes cliquables)                              │
│  ├── Cheat sheets par pilier                                               │
│  ├── Aide-mémoire patterns                                                 │
│  └── FAQ                                                                   │
│                                                                             │
│  📚 CATALOGUE DES PATTERNS                                                  │
│  ├── 🔗 Patterns Applications (fiches détaillées)                          │
│  ├── ⚡ Patterns Événements (fiches détaillées)                            │
│  ├── 📊 Patterns Données (fiches détaillées)                               │
│  └── 🛡️ Patterns Transversaux (fiches détaillées)                          │
│                                                                             │
│  🏢 DOMAINE MÉTIER ASSURANCE                                                │
│  ├── Glossaire métier assurance                                            │
│  ├── Schémas des processus                                                 │
│  ├── Modèle de données de référence                                        │
│  └── Règles métier courantes                                               │
│                                                                             │
│  🔧 RÉFÉRENCE TECHNIQUE                                                     │
│  ├── API Reference (OpenAPI intégré)                                       │
│  ├── Commandes sandbox                                                     │
│  ├── Configuration et paramètres                                           │
│  └── Troubleshooting                                                       │
│                                                                             │
│  📐 ARCHITECTURE                                                            │
│  ├── Diagrammes d'architecture                                             │
│  ├── Décisions d'architecture (ADR)                                        │
│  └── Anti-patterns à éviter                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.3 Fonctionnalités de la Documentation

| Fonctionnalité | Spécification |
|----------------|---------------|
| **Accès** | Section dédiée + accès contextuel depuis chaque module |
| **Recherche** | Avec filtres par pilier et type de contenu |
| **Patterns liés** | Graphe de relations interactif entre patterns |
| **Historique** | Liste des 10 dernières pages visitées |
| **Tooltips** | Définitions au survol des termes techniques |
| **Mode offline** | 100% accessible sans connexion |

### 9.4 Fiche Pattern Type

Chaque pattern dispose d'une fiche standardisée :

```
┌─────────────────────────────────────────────────────────────────┐
│  📋 FICHE PATTERN: [NOM DU PATTERN]                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  IDENTITÉ                                                       │
│  ├── Nom : Circuit Breaker                                     │
│  ├── Pilier : 🔗 Applications / ⚡ Événements                   │
│  ├── Catégorie : Résilience                                    │
│  └── Alias : Coupe-circuit, Disjoncteur                        │
│                                                                 │
│  PROBLÈME RÉSOLU                                                │
│  └── [Description du problème que ce pattern adresse]          │
│                                                                 │
│  SOLUTION                                                       │
│  └── [Explication de la solution apportée]                     │
│                                                                 │
│  DIAGRAMME                                                      │
│  └── [Schéma visuel du pattern]                                │
│                                                                 │
│  QUAND UTILISER                                                 │
│  └── [Critères et contextes appropriés]                        │
│                                                                 │
│  QUAND NE PAS UTILISER                                          │
│  └── [Anti-patterns et contextes inappropriés]                 │
│                                                                 │
│  IMPLÉMENTATION                                                 │
│  └── [Exemple de code commenté]                                │
│                                                                 │
│  CAS D'USAGE ASSURANCE                                          │
│  └── [Application concrète dans le domaine]                    │
│                                                                 │
│  PATTERNS LIÉS                                                  │
│  └── [Liens vers patterns complémentaires]                     │
│                                                                 │
│  RÉFÉRENCES                                                     │
│  └── [Sources et lectures complémentaires]                     │
│                                                                 │
│  SCÉNARIOS SANDBOX                                              │
│  └── [Liens vers scénarios pratiques]                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 9.5 Intégration avec l'Apprentissage

```
┌─────────────────────────────────────────────────────────────────┐
│  MODULE EN COURS                        [?] Aide  [📖] Doc     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Le pattern Circuit Breaker permet de...                       │
│                     ▲                                          │
│                     │ clic                                     │
│              ┌──────┴──────┐                                   │
│              │  TOOLTIP    │                                   │
│              │             │                                   │
│              │ Circuit     │                                   │
│              │ Breaker:    │                                   │
│              │ Pattern de  │                                   │
│              │ résilience  │                                   │
│              │             │                                   │
│              │ [Voir fiche]│                                   │
│              └─────────────┘                                   │
│                                                                 │
│  ─────────────────────────────────────────────────────────────│
│  💡 Documentation liée à ce module:                            │
│  • Fiche: Circuit Breaker                                      │
│  • Fiche: Retry Pattern                                        │
│  • Glossaire: Résilience                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 9.6 Structure des Fichiers Documentation

```
app/
├── docs/                              # Documentation intégrée
│   ├── reference/                     # Référence rapide
│   │   ├── glossary.md               # Glossaire complet
│   │   ├── cheatsheets/              # Aide-mémoire par pilier
│   │   │   ├── applications.md
│   │   │   ├── events.md
│   │   │   └── data.md
│   │   └── faq.md
│   │
│   ├── patterns/                      # Catalogue des patterns
│   │   ├── applications/             # Fiches patterns applicatifs
│   │   │   ├── api_gateway.md
│   │   │   ├── bff.md
│   │   │   ├── api_composition.md
│   │   │   └── ...
│   │   ├── events/                   # Fiches patterns événementiels
│   │   │   ├── pubsub.md
│   │   │   ├── event_sourcing.md
│   │   │   ├── saga.md
│   │   │   └── ...
│   │   ├── data/                     # Fiches patterns données
│   │   │   ├── etl.md
│   │   │   ├── cdc.md
│   │   │   ├── mdm.md
│   │   │   └── ...
│   │   └── cross_cutting/            # Fiches patterns transversaux
│   │       ├── circuit_breaker.md
│   │       ├── retry.md
│   │       └── ...
│   │
│   ├── domain/                        # Domaine métier assurance
│   │   ├── glossary_insurance.md     # Glossaire assurance
│   │   ├── processes.md              # Processus métier
│   │   ├── data_model.md             # Modèle de données
│   │   └── business_rules.md         # Règles métier
│   │
│   ├── technical/                     # Référence technique
│   │   ├── api_reference.md          # Documentation API
│   │   ├── sandbox_commands.md       # Commandes sandbox
│   │   ├── configuration.md          # Configuration
│   │   └── troubleshooting.md        # Dépannage
│   │
│   └── architecture/                  # Architecture
│       ├── diagrams/                 # Diagrammes
│       ├── adr/                      # Architecture Decision Records
│       └── anti_patterns.md          # Anti-patterns
│
└── api/
    └── docs.py                        # Routes API documentation
```

### 9.7 API Documentation

```yaml
GET /api/docs/search?q={query}
  # Recherche full-text dans la documentation

GET /api/docs/patterns
  # Liste tous les patterns avec métadonnées

GET /api/docs/patterns/{pattern_id}
  # Fiche détaillée d'un pattern

GET /api/docs/glossary
  # Glossaire complet

GET /api/docs/glossary/{term}
  # Définition d'un terme spécifique

GET /api/docs/domain/{section}
  # Section documentation métier

GET /api/docs/related/{module_id}
  # Documentation liée à un module
```

---

## 10. Interface Utilisateur

### 10.1 Spécifications UI/UX Détaillées

#### Design Visuel

| Aspect | Spécification |
|--------|---------------|
| **Style** | Moderne coloré avec thème sombre uniquement |
| **Densité** | Modérée - équilibre information/lisibilité |
| **Police** | Taille ajustable par l'utilisateur |
| **Couleurs messages** | REST=bleu, Events=orange, Data=vert + icônes distinctes |
| **Animations** | Expressives (500ms+), effet pédagogique |
| **Icônes** | Lucide Icons |
| **Framework CSS** | Tailwind CSS |

#### Layout et Navigation

| Aspect | Spécification |
|--------|---------------|
| **Navigation** | Menu latéral fixe (sidebar toujours visible) |
| **Breadcrumb** | Oui - chemin complet affiché |
| **Layout sandbox** | Panneaux redimensionnables |
| **Raccourcis clavier** | Aucun - navigation souris uniquement |
| **Page d'accueil** | Dashboard avec état actuel et accès rapides |
| **Organisation piliers** | 3 onglets principaux : Applications \| Événements \| Données |

#### Feedback Utilisateur

| Aspect | Spécification |
|--------|---------------|
| **Erreurs** | Toast notifications (temporaires, coin d'écran) |
| **Chargement** | Spinner global pleine page |
| **Confirmation** | Aucune - actions immédiates avec undo si erreur |
| **États services** | Multi-états (Actif / Dégradé / En erreur / Arrêté) |

#### Langue et Accessibilité

| Aspect | Spécification |
|--------|---------------|
| **Langue** | Français uniquement (termes techniques traduits) |
| **Terminologie** | Générique (Client, Contrat, Réclamation) |
| **Accessibilité** | Taille de police ajustable |

### 10.2 Navigation Principale

```
┌─────────────────────────────────────────────────────────────┐
│  🎓 INTEROP LEARNING                    [Progression: 45%]  │
├──────────┬──────────────────────────────────────────────────┤
│          │                                                  │
│  📚 Parcours │                                              │
│          │    NIVEAU 2 - MESSAGING                          │
│  ├─ Niveau 1 │                                              │
│  │  ✅ Complet │    Module 4: Communication Asynchrone      │
│  │          │                                               │
│  ├─ Niveau 2 │    ┌─────────────────────────────────────┐  │
│  │  ▶ En cours │  │ 4.1 Queues vs Topics                │  │
│  │  │ Module 4│   │                                     │  │
│  │  │ Module 5│   │ [Contenu théorique...]              │  │
│  │  │ Module 6│   │                                     │  │
│  │          │    │ 📊 Diagramme interactif              │  │
│  ├─ Niveau 3 │   │                                     │  │
│  │  🔒 Verrouillé│ └─────────────────────────────────────┘  │
│  │          │                                               │
│  └─ ...     │    [◀ Précédent]  [Suivant ▶]  [🎮 Sandbox]   │
│          │                                                  │
│  ⚙️ Paramètres│                                             │
│          │                                                  │
└──────────┴──────────────────────────────────────────────────┘
```

### 10.2 Vue Sandbox

```
┌─────────────────────────────────────────────────────────────┐
│  🎮 SANDBOX - Scénario: Souscription Complète               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────┐  ┌─────────────────────────────┐  │
│  │ INSTRUCTIONS        │  │ SERVICES ACTIFS             │  │
│  │                     │  │                             │  │
│  │ Étape 3/7           │  │  Quote ──▶ Policy ──▶ Billing│
│  │                     │  │    │                   │    │
│  │ Publiez un événement│  │    └───────┬───────────┘    │
│  │ PolicyCreated sur   │  │            ▼                │  │
│  │ le topic policies   │  │       [Notifications]       │  │
│  │                     │  │                             │  │
│  │ [Indice]            │  │  Messages: 23  Erreurs: 0   │  │
│  └─────────────────────┘  └─────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ CONSOLE D'EXÉCUTION                                   │  │
│  │                                                        │  │
│  │ > publish policies PolicyCreated {"policy_id": "P001"}│  │
│  │ ✓ Event published successfully                        │  │
│  │ ← Billing received: PolicyCreated                     │  │
│  │ ← Notifications received: PolicyCreated               │  │
│  │ > _                                                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  [Reset Scénario]  [Valider Étape]  [Voir Solution]        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 11. Modèle de Données

### 11.1 Schéma Base de Données (SQLite)

```sql
-- Progression de l'apprenant
CREATE TABLE learner_progress (
    id INTEGER PRIMARY KEY,
    module_id TEXT NOT NULL,
    status TEXT CHECK(status IN ('locked','available','in_progress','completed')),
    started_at DATETIME,
    completed_at DATETIME,
    score INTEGER
);

-- Résultats des quiz
CREATE TABLE quiz_results (
    id INTEGER PRIMARY KEY,
    module_id TEXT NOT NULL,
    attempt INTEGER DEFAULT 1,
    score INTEGER,
    answers JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- État des scénarios sandbox
CREATE TABLE sandbox_sessions (
    id INTEGER PRIMARY KEY,
    scenario_id TEXT NOT NULL,
    state JSON,
    current_step INTEGER DEFAULT 1,
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);

-- Événements du sandbox (pour replay)
CREATE TABLE sandbox_events (
    id INTEGER PRIMARY KEY,
    session_id INTEGER REFERENCES sandbox_sessions(id),
    event_type TEXT,
    payload JSON,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Badges obtenus
CREATE TABLE badges (
    id INTEGER PRIMARY KEY,
    badge_type TEXT NOT NULL,
    earned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    module_id TEXT
);
```

### 11.2 Données Mock Assurance

```python
# Exemple de données pré-chargées

MOCK_CUSTOMERS = [
    {"id": "C001", "name": "Jean Dupont", "email": "jean.dupont@email.com"},
    {"id": "C002", "name": "Marie Martin", "email": "marie.martin@email.com"},
    # ...
]

MOCK_POLICIES = [
    {
        "number": "POL-2024-001",
        "customer_id": "C001",
        "type": "AUTO",
        "status": "ACTIVE",
        "premium": 850.00,
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "coverages": ["RC", "VOL", "BRIS_GLACE"]
    },
    # ...
]

MOCK_CLAIMS = [
    {
        "number": "CLM-2024-001",
        "policy_number": "POL-2024-001",
        "type": "ACCIDENT",
        "status": "OPEN",
        "reported_date": "2024-03-15",
        "estimated_amount": 2500.00
    },
    # ...
]
```

---

## 12. APIs Internes

### 12.1 API Théorie

```yaml
GET /api/theory/modules
  # Liste tous les modules avec statut de progression

GET /api/theory/modules/{module_id}
  # Contenu complet d'un module

POST /api/theory/modules/{module_id}/complete
  # Marque un module comme complété

GET /api/theory/modules/{module_id}/quiz
  # Questions du quiz

POST /api/theory/modules/{module_id}/quiz
  # Soumet les réponses du quiz
```

### 12.2 API Sandbox

```yaml
POST /api/sandbox/sessions
  # Démarre une nouvelle session sandbox
  Body: { "scenario_id": "SC-02" }

GET /api/sandbox/sessions/{session_id}
  # État actuel de la session

POST /api/sandbox/sessions/{session_id}/execute
  # Exécute une commande
  Body: { "command": "publish", "args": {...} }

POST /api/sandbox/sessions/{session_id}/validate
  # Valide l'étape courante

GET /api/sandbox/sessions/{session_id}/events
  # Stream SSE des événements temps réel

POST /api/sandbox/services/{service_id}/config
  # Configure un service mock (latence, erreurs)
```

### 12.3 API Progression

```yaml
GET /api/progress
  # Progression globale

GET /api/progress/badges
  # Badges obtenus

GET /api/progress/stats
  # Statistiques détaillées
```

---

## 13. Installation et Déploiement

### 13.1 Prérequis Windows 11

- Python 3.11+ (via Microsoft Store ou python.org)
- Navigateur moderne (Chrome, Edge, Firefox)
- *Pas de Redis requis* - simulation pure Python

### 13.2 Installation via Script Batch

**install.bat** :
```batch
@echo off
echo === Installation Interop Learning ===

echo Création de l'environnement virtuel...
python -m venv venv
call venv\Scripts\activate.bat

echo Installation des dépendances...
pip install -r requirements.txt

echo Initialisation de la base de données...
python -c "from app.database import init_db; init_db()"

echo.
echo === Installation terminée ===
echo Lancez l'application avec: run.bat
pause
```

**run.bat** :
```batch
@echo off
call venv\Scripts\activate.bat
python run.py
```

### 13.3 Script de Lancement (run.py)

```python
"""
Point d'entrée de l'application Interop Learning.
Lance le serveur FastAPI et ouvre le navigateur automatiquement.
"""
import uvicorn
import webbrowser
from threading import Timer

def open_browser():
    """Ouvre le navigateur sur l'application après un délai."""
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    Timer(1.5, open_browser).start()
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
```

---

## 14. Dépendances

### 14.1 requirements.txt

```
# Framework web
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6

# Templates
jinja2>=3.1.3

# Markdown processing
markdown>=3.5.2
pygments>=2.17.2

# Base de données (SQL brut, pas d'ORM)
aiosqlite>=0.19.0

# SSE pour temps réel
sse-starlette>=1.6.0

# Utilitaires
pydantic>=2.6.0

# Tests (couverture complète)
pytest>=8.0.0
pytest-asyncio>=0.23.4
pytest-cov>=4.1.0
```

### 14.2 Assets Frontend (pas de build, fichiers directs)

```
static/
├── css/
│   └── tailwind.min.css      # Tailwind CSS (CDN ou local)
├── js/
│   ├── htmx.min.js           # HTMX
│   ├── d3.min.js             # D3.js pour diagrammes
│   └── app.js                # Code applicatif
└── icons/
    └── lucide-icons/         # Icônes Lucide
```

---

## 15. Critères de Succès

### 15.1 Critères Utilisateur

| Critère | Description |
|---------|-------------|
| **Compréhension** | L'apprenant peut expliquer les 3 piliers d'intégration |
| **Application** | L'apprenant identifie quel pattern utiliser selon le contexte |
| **Navigation** | Accès à tout contenu en moins de 3 clics |
| **Autonomie** | Utilisation sans aide externe ni documentation |

*Note : Pas de métriques quantitatives (quiz, scores) - évaluation qualitative uniquement*

### 15.2 Métriques Techniques

| Métrique | Objectif |
|----------|----------|
| Temps de chargement page | < 2s |
| Latence sandbox | < 100ms |
| Disponibilité | 99% (local) |

### 15.3 Définition de "Done"

Un module est considéré complet quand :
- ✅ Contenu théorique rédigé (résumé + sections dépliables)
- ✅ Diagrammes interactifs fonctionnels
- ✅ Pseudo-code illustratif inclus
- ✅ Scénario sandbox fonctionnel (6-10 étapes)
- ✅ Replay animé opérationnel
- ✅ Fiches patterns liées créées
- ✅ Tests automatisés passants
- ✅ Docstrings complets dans le code

---

## 16. Roadmap de Développement

### Phase 1 - Fondations
- [ ] Setup projet et architecture de base
- [ ] Infrastructure (FastAPI, SQLite, Redis simulation, templates)
- [ ] Système de navigation et progression
- [ ] Modules 1-2 : Fondations et domaine métier

### Phase 2 - Pilier Applications 🔗
- [ ] Mock services assurance (Quote, Policy, Claims, Billing)
- [ ] Modules 3-5 : REST, API Gateway, Patterns avancés
- [ ] Scénarios sandbox APP-01 à APP-05

### Phase 3 - Pilier Événements ⚡
- [ ] Simulation messaging (queues, topics, pub/sub)
- [ ] Visualiseur de flux événements temps réel
- [ ] Modules 6-8 : Messaging, Event-Driven, Saga
- [ ] Scénarios sandbox EVT-01 à EVT-06

### Phase 4 - Pilier Données 📊
- [ ] Simulation ETL et pipelines
- [ ] CDC et streaming simulation
- [ ] Modules 9-11 : ETL, CDC, Data Quality
- [ ] Scénarios sandbox DATA-01 à DATA-05

### Phase 5 - Patterns Transversaux
- [ ] Patterns de résilience implémentés
- [ ] Simulation pannes et chaos
- [ ] Observabilité et tracing
- [ ] Modules 12-14 : Résilience, Observabilité, Sécurité

### Phase 6 - Synthèse et Finalisation
- [ ] Modules 15-16 : Architecture et Projet Final
- [ ] Scénario CROSS-04 : Écosystème complet
- [ ] Polish UI/UX
- [ ] Documentation complète

---

## 17. Risques et Mitigations

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| Complexité simulation messaging | Haut | Moyen | Utiliser fakeredis, simplifier si nécessaire |
| Courbe d'apprentissage trop raide | Moyen | Moyen | Ajouter indices progressifs, tutoriels vidéo |
| Performance sandbox | Moyen | Faible | Profiling régulier, optimisation lazy loading |
| Installation Redis Windows | Faible | Moyen | Alternative Memurai ou simulation pure Python |

---

## 18. Annexes

### A. Glossaire

#### Termes Généraux

| Terme | Définition |
|-------|------------|
| **Interopérabilité** | Capacité de systèmes hétérogènes à échanger des informations |
| **Couplage** | Degré de dépendance entre deux systèmes |
| **Latence** | Délai entre l'envoi d'une requête et la réception de la réponse |
| **Idempotence** | Propriété d'une opération pouvant être exécutée plusieurs fois sans effet supplémentaire |

#### Termes Assurance

| Terme | Définition |
|-------|------------|
| **PAS** | Policy Administration System - Système de gestion des polices |
| **Quote/Devis** | Proposition tarifaire pour une couverture d'assurance |
| **Policy/Police** | Contrat d'assurance en vigueur |
| **Claim/Sinistre** | Déclaration d'un événement couvert par la police |
| **Premium/Prime** | Montant payé par l'assuré pour la couverture |
| **Underwriting** | Processus d'évaluation et d'acceptation des risques |

#### Termes Pilier Applications 🔗

| Terme | Définition |
|-------|------------|
| **API Gateway** | Point d'entrée unique gérant routing, auth, rate limiting |
| **BFF** | Backend for Frontend - API adaptée par canal (mobile, web, partenaire) |
| **ACL** | Anti-Corruption Layer - Couche d'isolation entre domaines |
| **Service Mesh** | Infrastructure dédiée à la communication inter-services |
| **REST** | Representational State Transfer - Style architectural pour APIs |
| **GraphQL** | Langage de requête pour APIs avec schéma typé |
| **gRPC** | Framework RPC haute performance de Google |

#### Termes Pilier Événements ⚡

| Terme | Définition |
|-------|------------|
| **Event** | Fait significatif survenu dans le système |
| **Message Queue** | File d'attente point-à-point pour messages |
| **Topic** | Canal de diffusion multi-consommateurs (pub/sub) |
| **Event Sourcing** | Stockage de l'état comme séquence d'événements |
| **CQRS** | Command Query Responsibility Segregation - Séparation lectures/écritures |
| **Saga** | Pattern de gestion des transactions distribuées avec compensation |
| **DLQ** | Dead Letter Queue - File pour messages non traitables |
| **Outbox Pattern** | Garantie atomique publication événement + commit DB |

#### Termes Pilier Données 📊

| Terme | Définition |
|-------|------------|
| **ETL** | Extract-Transform-Load - Pipeline batch de données |
| **ELT** | Extract-Load-Transform - Transformation après chargement |
| **CDC** | Change Data Capture - Capture incrémentale des modifications |
| **MDM** | Master Data Management - Gestion des données de référence |
| **Data Lineage** | Traçabilité de l'origine et transformations des données |
| **Data Quality** | Ensemble des dimensions mesurant la qualité des données |
| **Golden Record** | Enregistrement de référence consolidé et fiable |

#### Termes Résilience

| Terme | Définition |
|-------|------------|
| **Circuit Breaker** | Pattern de protection contre les pannes en cascade |
| **Retry** | Mécanisme de réessai avec backoff |
| **Fallback** | Solution de repli en cas d'échec |
| **Bulkhead** | Isolation des ressources pour limiter l'impact des pannes |
| **Timeout** | Délai maximum d'attente avant abandon |

### B. Références

#### Livres de Référence
- **Enterprise Integration Patterns** (Hohpe, Woolf) - Bible des patterns d'intégration
- **Building Microservices** (Sam Newman) - Architecture microservices
- **Designing Data-Intensive Applications** (Kleppmann) - Systèmes de données distribués
- **Domain-Driven Design** (Eric Evans) - Conception pilotée par le domaine
- **Implementing Domain-Driven Design** (Vaughn Vernon) - DDD appliqué
- **Fundamentals of Data Engineering** (Reis, Housley) - Ingénierie des données

#### Documentation Technique
- FastAPI Documentation
- Redis Documentation
- Apache Kafka Documentation
- OpenAPI Specification

### C. Diagramme Récapitulatif des Trois Piliers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ÉCOSYSTÈME ASSURANCE - VUE INTÉGRATION                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   CANAUX                    INTÉGRATION                    SYSTÈMES         │
│   ───────                   ───────────                    ─────────        │
│                                                                             │
│   ┌─────────┐              ┌───────────────┐              ┌─────────┐      │
│   │ Portail │──────────────│               │──────────────│  Quote  │      │
│   │  Web    │    🔗 API    │               │    🔗 API    │ Engine  │      │
│   └─────────┘              │               │              └─────────┘      │
│                            │               │                               │
│   ┌─────────┐              │   GATEWAY /   │              ┌─────────┐      │
│   │  App    │──────────────│    ESB /      │──────────────│   PAS   │      │
│   │ Mobile  │    🔗 BFF    │   SERVICE     │    🔗 REST   │         │      │
│   └─────────┘              │    MESH       │              └─────────┘      │
│                            │               │                               │
│   ┌─────────┐              │               │              ┌─────────┐      │
│   │Courtiers│──────────────│               │──────────────│ Claims  │      │
│   │   B2B   │    🔗 API    │               │    🔗 gRPC   │  Mgmt   │      │
│   └─────────┘              └───────┬───────┘              └─────────┘      │
│                                    │                                       │
│                            ┌───────┴───────┐                               │
│                            │  EVENT BUS /  │                               │
│                            │  MESSAGE      │                               │
│                            │  BROKER       │                               │
│                            └───────┬───────┘                               │
│                                    │                                       │
│         ┌──────────────────────────┼──────────────────────────┐           │
│         │                          │                          │           │
│         ▼                          ▼                          ▼           │
│   ┌───────────┐             ┌───────────┐             ┌───────────┐       │
│   │  Billing  │◀── ⚡ ─────▶│  Notif    │◀── ⚡ ─────▶│  Audit    │       │
│   │  System   │   Events    │  Service  │   Events    │   Log     │       │
│   └─────┬─────┘             └───────────┘             └───────────┘       │
│         │                                                                  │
│         │ 📊 CDC                                                           │
│         ▼                                                                  │
│   ┌───────────────────────────────────────────────────────────────┐       │
│   │                      DATA PLATFORM                             │       │
│   │                                                                │       │
│   │  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐   │       │
│   │  │   DWH   │◀───│   ETL   │◀───│   CDC   │◀───│ Sources │   │       │
│   │  │         │    │ Pipeline│    │ Stream  │    │   DB    │   │       │
│   │  └────┬────┘    └─────────┘    └─────────┘    └─────────┘   │       │
│   │       │                                                       │       │
│   │       ▼                                                       │       │
│   │  ┌─────────┐    ┌─────────┐                                  │       │
│   │  │   BI    │    │  ML/AI  │                                  │       │
│   │  │Reporting│    │ Models  │                                  │       │
│   │  └─────────┘    └─────────┘                                  │       │
│   └───────────────────────────────────────────────────────────────┘       │
│                                                                             │
│   LÉGENDE:  🔗 Intégration Applications   ⚡ Intégration Événements        │
│             📊 Intégration Données                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 19. Récapitulatif des Décisions d'Architecture

### Décisions Clés (Issues de l'Interview)

| Catégorie | Décision | Justification |
|-----------|----------|---------------|
| **Réalisme** | Simplifié | Focus sur les concepts, pas la complexité réelle |
| **Persistance** | Session unique | Simplicité, pas de gestion d'état complexe |
| **Évaluation** | Aucune | Liberté d'exploration, pas de pression |
| **Navigation** | Totalement libre | Autonomie de l'apprenant |
| **Thème** | Sombre uniquement | Réduction fatigue oculaire |
| **Interaction** | GUI uniquement | Accessibilité maximale |
| **Backend** | Monolithique | Simplicité, maintenabilité |
| **Broker** | In-memory Python | Zéro dépendance externe |
| **ORM** | SQL brut | Transparence, simplicité |
| **Temps réel** | SSE | Plus simple que WebSocket |

### Compromis Acceptés

| Compromis | Ce qu'on gagne | Ce qu'on perd |
|-----------|----------------|---------------|
| Pas de persistance | Simplicité code | Reprise de session |
| Pas d'évaluation | Liberté apprenant | Mesure de progression |
| GUI uniquement | Accessibilité | Expérience CLI réaliste |
| Données fixes | Reproductibilité | Personnalisation |
| Monolithique | Maintenabilité | Scalabilité |

---

*Document Version: 1.2*
*Dernière mise à jour: Janvier 2025*
*Spécifications détaillées issues de l'interview utilisateur*
