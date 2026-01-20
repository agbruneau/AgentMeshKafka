# /recover - Diagnose and Recover from Failures

Diagnose issues and guide recovery when a phase validation fails.

## Usage

```
/recover
```

## Instructions

When this command is invoked:

1. **Identify the failed phase** from PLAN.MD progress table
2. **Run diagnostic commands** to identify the root cause
3. **Analyze error messages**
4. **Propose recovery steps**
5. **Guide through resolution**

## Diagnostic Workflow

```
=== RECOVERY DIAGNOSTIC ===

1. Identifying failed phase...
   Current Phase: [N]
   Last Checkpoint: [PASS/FAIL]

2. Running diagnostics...

   Infrastructure:
   $ docker-compose ps
   [output]

   Kafka:
   $ docker-compose logs kafka | tail -20
   [output]

   PostgreSQL:
   $ docker-compose logs postgres | tail -20
   [output]

   Go Tests:
   $ go test ./... 2>&1 | tail -50
   [output]

3. Analysis:
   [Root cause identification]

4. Recovery Steps:
   [ ] Step 1: [action]
   [ ] Step 2: [action]
   ...

5. After recovery:
   Run /validate to confirm fix
```

## Common Issues and Solutions

| Issue | Diagnostic | Solution |
|-------|------------|----------|
| Container won't start | `docker-compose logs <svc>` | Check port conflicts, resources |
| Kafka not ready | `docker-compose ps kafka` | Wait for healthcheck, restart |
| Schema Registry error | `curl localhost:8081/subjects` | Check Kafka connectivity |
| PostgreSQL connection | `psql` connection test | Check credentials, firewall |
| Go test failure | `go test -v ./...` | Read error, fix code |
| npm build failure | `npm run build 2>&1` | Check dependencies, TypeScript |

## Recovery Commands

```bash
# Full infrastructure reset
make infra-clean && make infra-up

# Clear Go test cache
go clean -testcache

# Reset npm dependencies
rm -rf node_modules && npm install

# Check port availability (Linux/Mac)
lsof -i :9092  # Kafka
lsof -i :5432  # PostgreSQL
lsof -i :8081  # Schema Registry
```

## Example

```
User: /recover
Claude: Starting recovery diagnostic...

=== RECOVERY DIAGNOSTIC ===
1. Identifying failed phase...
   Current Phase: 0 (Infrastructure)
   Last Checkpoint: FAIL

2. Running diagnostics...
...
```
