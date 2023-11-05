# Scenario 1: Small Simple DAGs

## DAG Set
<!--- CASE_TABLE_START -->
| Property                | Value              |
|:------------------------|:-------------------|
| id                      | 1                  |
| name                    | Small Simple DAGs  |
| dag_files               | [1, 10, 100, 1000] |
| dags_per_file           | 1                  |
| tasks_per_dag           | 10                 |
| dag_shape               | linear             |
| max_active_runs_per_dag | 1                  |
| parallelism             | 128                |
| total_dagruns_per_dag   | 1                  |
<!--- CASE_TABLE_END -->

## Environment

| Environment | Executor   | Scheduler AUs | Worker Count | Worker AUs | Extra Capacity AUs | Webserver AUs |
|-------------|------------|---------------|--------------|------------|--------------------|---------------|
| 1           | Local      | 5             | 0            | 0          | 0                  | 5             |
| 2           | Local      | 10            | 0            | 0          | 0                  | 5             |
| 3           | Celery     | 5             | 1            | 10         | 0                  | 5             |
| 4           | Celery     | 10            | 1            | 10         | 0                  | 5             |
| 7           | Kubernetes | 5             | 0            | 0          | 10                 | 5             |
| 8           | Kubernetes | 10            | 0            | 0          | 10                 | 5             |

## Benchmark

Run the Benchmark for each Environment (1-8) and fill the table below:

| Case | DAG Files | Avg DagRun Duration | Scheduler Lag | Queuing time |
|------|-----------|---------------------|---------------|--------------|
| 1    | 1         |                     |               |              |
| 2    | 10        |                     |               |              |
| 3    | 100       |                     |               |              |
| 4    | 1000      |                     |               |              |

where:

- **Avg DagRun Duration** is the average Duration of all DagRuns
- **Scheduler Lag** is the time between recorded end date of one task and start date of next (taking in to
account max(end_date) of all upstream tasks etc.)
- **Queuing time** is the time between scheduler putting state to queued and task starting (need to make
sure this only makes sense when we are not at queue capacity. i.e. no point recording this if we have 200 tasks but only 16 executor slots.)
* Max (infinite) Dag Concurrency
