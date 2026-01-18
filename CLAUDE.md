# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **"L'Entreprise Agentique"** (The Agentic Enterprise), a French-language academic/professional monograph exploring enterprise transformation toward agentic architectures. The project consists of **81 chapters across 5 volumes** covering theoretical foundations, technical implementations, and strategic implications.

**This is a publishing project, not a software codebase.** Content is authored in Word (.docx) format with markdown for navigation and structure.

## Repository Structure

```
Volume_I_Fondations_Entreprise_Agentique/   (28 chapters - Theoretical foundations)
Volume_II_Infrastructure_Agentique/          (15 chapters - Confluent + Google Cloud)
Volume_III_Apache_Kafka_Guide_Architecte/    (12 chapters - Kafka deep-dive)
Volume_IV_Apache_Iceberg_Lakehouse/          (16 + 2 chapters - Data Lakehouse)
Volume_V_Developpeur_Renaissance/            (10 chapters - Human capital & skills)
```

Each volume contains:
- `README.md` - Volume overview and navigation
- `Partie_*/Chapitre_*/` - Individual chapter directories with .docx files

**Root-level files:**
- `INSTRUCTION.MD` - Consolidated editorial guidelines for all volumes (in French)
- `CLAUDE.md` - Claude Code configuration (this file, in English)

## Editorial Standards

### Language & Terminology

- **Quebec professional French** (infonuagique, courriel, etc.)
- **60% theory / 40% practice** balance for Volume I
- Target audience: Enterprise architects, CTOs, transformation consultants

### Mandatory Terminology (Lexique Obligatoire)

| Term | Usage |
|------|-------|
| Entreprise agentique | NOT "entreprise IA" |
| Agents cognitifs | NOT "agents IA" alone |
| Maillage agentique / Agentic Mesh | Multi-agent orchestration |
| Interopérabilité Cognitivo-Adaptative (ICA) | AI-enhanced semantic understanding |
| Architecture réactive | Event-driven architecture |
| Backbone événementiel | Event backbone |
| AgentOps | Agent operations discipline |
| Architecte d'intentions | Intention Architect role |
| Berger d'intention | Intention Shepherd role |

### Chapter Format

- **Target length**: 5,000 words per chapter
- **Structure**: Introduction (10%) → Development (80%) → Conclusion (10%)
- **Output format**: Word (.docx)
- **Each chapter ends with**: Structured "Résumé" section

---

## Normalized Markdown Structure

All chapter markdown files follow this standardized structure for PDF consolidation.

### Chapter Header (Obligatoire)

```markdown
# Chapitre [VOL].[NUM] — [Titre du Chapitre]

> *« Citation inspirante optionnelle »*
> — Auteur

---

## [VOL].[NUM].0 Introduction

[Paragraphe contextuel 150-300 mots...]
```

**Volume prefixes:**
- Volume I: `I.N`
- Volume II: `II.N`
- Volume III: `III.N`
- Volume IV: `IV.N`

### Title Hierarchy

| Level | Syntax | Usage | Example |
|-------|--------|-------|---------|
| H1 `#` | Chapter title only | `# Chapitre I.5 — Écosystème API` |
| H2 `##` | Main sections | `## I.5.1 L'API comme Interface Stratégique` |
| H3 `###` | Subsections | `### I.5.1.1 Patterns RESTful` |
| H4 `####` | Detail points (rare) | Not numbered |

### Callouts (Blockquote Format)

**Universal callouts (all volumes):**

```markdown
> **Définition formelle**
>
> [Term defined and concise explanation]

> **Perspective stratégique**
>
> [Business implications, recommendations]

> **Exemple concret**
>
> [Practical illustration with context]
```

**Technical callouts (Volumes II-IV):**

```markdown
> **Note de terrain**
>
> *Contexte* : [Description]
> *Défi* : [Problem]
> *Solution* : [Approach]
> *Leçon* : [Lesson learned]

> **Décision architecturale**
>
> *Contexte* : [Situation]
> *Analyse* : [Options]
> *Décision* : [Choice]
> *Justification* : [Reasons]

> **Anti-patron**
>
> *[Error description]* : [Explanation and alternative]

> **Étude de cas : [Name]**
>
> *Secteur* : [Industry]
> *Défi* : [Challenge]
> *Solution* : [Architecture]
> *Résultats* : [Metrics]

> **Migration : [Title]**
>
> *De* : [Source state]
> *Vers* : [Target state]
> *Stratégie* : [Approach]
> *Résultats* : [Outcomes]

> **Performance : [Title]**
>
> [Performance metrics and benchmarks]
```

### Table Format (Pipe-table Markdown)

```markdown
| Critère | Option A | Option B | Recommandation |
|---------|----------|----------|----------------|
| Performance | Élevée | Moyenne | A |
| Coût | Élevé | Faible | B |
```

### Chapter End Structure

```markdown
---

## [VOL].[NUM].[N] Conclusion

[Synthesis 150-200 words]

---

## [VOL].[NUM].[N+1] Résumé

Ce chapitre a exploré [theme]. Points essentiels :

**[Concept 1]** : [Summary 2-3 sentences]

**[Concept 2]** : [Summary 2-3 sentences]

### Tableau Récapitulatif

| Concept | Définition | Implication |
|---------|------------|-------------|
| [Term] | [Definition] | [Application] |

---

*Chapitre suivant : Chapitre [VOL].[NUM+1] — [Title]*
```

**For volume final chapters:**
```markdown
*Fin du Volume [N] — [Volume Title]*
```

---

## Special Callouts

Use these blockquote formats:
- `> **Définition formelle**` - For key concept definitions
- `> **Perspective stratégique**` - For business implications
- `> **Exemple concret**` - For practical illustrations

### Citation Convention

- Prioritize 2023-2026 technical sources
- Reference leaders: Confluent, Apache, Google Cloud, Anthropic
- Format: Name (Year) or "selon [Organization, Year]"

## Technology Stack (Subject Matter)

The monograph covers these technologies:
- **Apache Kafka / Confluent Platform** - Event backbone
- **Google Cloud Vertex AI** - Cognitive layer
- **Apache Iceberg** - Data Lakehouse
- **Schema Registry** - Data contracts
- **AsyncAPI** - Asynchronous protocol specification
- **A2A, MCP** - Agent interoperability protocols

## Cross-Volume References

When writing content, reference related volumes:
- Volume I → Conceptual foundations
- Volume II → Technical implementation (Confluent + GCP)
- Volume III → Kafka architecture details
- Volume IV → Data lakehouse patterns
- Volume V → Human skills and development practices

## Claude Code Configuration

This project uses Claude Code with automatic execution enabled:

```bash
claude --dangerously-skip-permissions
```

This mode bypasses all permission prompts for autonomous operation.
