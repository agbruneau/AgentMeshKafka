# /status - Show Project Progress

Display the current progress status of the EDA-Lab project.

## Usage

```
/status
```

## Instructions

When this command is invoked:

1. **Read PLAN.MD** progress table
2. **Check infrastructure status** (if applicable)
3. **Summarize current state**
4. **Identify next action**

## Output Format

```
=== EDA-LAB PROJECT STATUS ===

MVP Progress: [Phase X of 8]
Current Phase: [Name]
Status: [Not Started | In Progress | Completed]

Phase Progress:
| Phase | Name           | Code | Tests | Status      |
|-------|----------------|------|-------|-------------|
| 0     | Infrastructure | X    | X     | [status]    |
| 1     | Fondations Go  | X    | X     | [status]    |
| ...   | ...            | ...  | ...   | ...         |

Infrastructure:
- Docker: [Running/Stopped/Unknown]
- Kafka: [Healthy/Unhealthy/Unknown]
- PostgreSQL: [Healthy/Unhealthy/Unknown]
- Schema Registry: [Healthy/Unhealthy/Unknown]

Next Action:
- [Recommendation based on current state]

Commands:
- /phase N     : Implement phase N
- /validate    : Validate current checkpoint
- /recover     : Diagnose and fix issues
```

## Status Determination

Read from PLAN.MD progress table:
- ❌ = Not Started
- ⏳ = In Progress
- ✓ = Completed
- 🔄 = In Recovery (failed validation)

## Example

```
User: /status
Claude: Checking EDA-Lab project status...

=== EDA-LAB PROJECT STATUS ===
MVP Progress: Phase 0 of 8
Current Phase: Infrastructure
Status: Not Started
...
```
