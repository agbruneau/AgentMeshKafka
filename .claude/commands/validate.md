# /validate - Validate Phase Checkpoint

Validate the checkpoint for the current or specified phase according to PLAN.MD.

## Usage

```
/validate [N]
```

Where N is optional phase number. If not specified, validates the current phase based on progress tracking.

## Instructions

When this command is invoked:

1. **Identify current phase** from PLAN.MD progress table
2. **Read the CHECKPOINT section** for that phase in PLAN.MD
3. **Execute validation commands** listed in the checkpoint
4. **Check each item** in the checklist
5. **Report results** with clear pass/fail status
6. **Update progress table** if validation passes

## Validation Output Format

```
=== CHECKPOINT PHASE N VALIDATION ===

Validation Commands:
[ ] Command 1: <result>
[ ] Command 2: <result>

Checklist:
[ ] Item 1: PASS/FAIL
[ ] Item 2: PASS/FAIL
...

Overall: PASS/FAIL

Next Steps:
- If PASS: Proceed to Phase N+1
- If FAIL: Run /recover to diagnose
```

## Checkpoint Criteria per Phase

| Phase | Key Validation |
|-------|----------------|
| 0 | `make test-infra` passes |
| 1 | `go test ./pkg/...` passes |
| 2 | Schemas registered in Schema Registry |
| 3 | Simulator API responds |
| 4 | Bancaire consumes and persists events |
| 5 | WebSocket broadcasts events |
| 6 | Grafana dashboards show metrics |
| 7 | React app builds and tests pass |
| 8 | `./scripts/validate-mvp.sh` passes |

## Example

```
User: /validate 0
Claude: Validating Phase 0 checkpoint...
```
