# /phase - Implement EDA-Lab Phase

Implement a specific phase of the EDA-Lab MVP according to PLAN.MD.

## Usage

```
/phase <N>
```

Where N is the phase number (0-8).

## Instructions

When this command is invoked with a phase number:

1. **Read PLAN.MD** to understand the phase requirements
2. **Check prerequisites**: Verify previous phase checkpoint is validated
3. **Execute each sub-step** in order following TDD protocol:
   - RED: Write test first, verify it fails
   - GREEN: Write minimal implementation to pass
   - REFACTOR: Improve code while keeping tests green
4. **Validate checkpoint** at the end of the phase
5. **Update progress** in PLAN.MD tableau de progression

## Phase Summary

| Phase | Name | Key Deliverables |
|-------|------|------------------|
| 0 | Infrastructure | Docker Compose, Kafka, PostgreSQL, Schema Registry |
| 1 | Fondations Go | pkg/config, pkg/kafka, pkg/database, pkg/observability |
| 2 | Schemas Avro | .avsc files, Schema Registry registration, Go types |
| 3 | Simulator | Event generator service with REST API |
| 4 | Bancaire | Event consumer service with PostgreSQL persistence |
| 5 | Gateway | REST proxy + WebSocket hub |
| 6 | Observability | Prometheus + Grafana dashboards |
| 7 | Web UI | React + React Flow visualization |
| 8 | Integration | E2E tests, documentation, validation |

## Emergency Stop

If any validation fails during implementation:
1. STOP immediately
2. Run `/recover` to diagnose
3. Fix the issue before continuing

## Example

```
User: /phase 0
Claude: I'll implement Phase 0 (Infrastructure) following the PLAN.MD...
```
