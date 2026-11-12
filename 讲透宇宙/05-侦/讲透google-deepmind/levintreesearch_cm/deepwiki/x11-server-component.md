<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/levintreesearch_cm · extra page Server Component · fetched 2026-10-26 -->

# Server Component

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [jobsched/scribblings/jobsched.scrbl](jobsched/scribblings/jobsched.scrbl)
- [jobsched/server.rkt](jobsched/server.rkt)

</details>



This document provides a detailed explanation of the Server Component in the JobSched job scheduling system. The Server Component is responsible for managing the job queue, dispatching jobs to workers, and collecting results. For information about the Worker Component, see [Worker Component](#4.1.2).

## Overview

The Server Component is the central coordination mechanism in JobSched's parallel processing framework. It maintains a priority queue of jobs, starts and manages multiple worker processes, distributes jobs to available workers, and collects results when jobs are completed.

```mermaid
flowchart TD
    subgraph "Server Component"
        scheduler["scheduler struct"]
        queue["job priority queue"]
        workermgmt["worker management"]
        jobdistribution["job distribution"]
    end
    
    subgraph "External Components"
        workers["Worker Processes"]
        client["Client Application"]
    end
    
    client -->|"adds jobs\nvia scheduler-add-job!"| queue
    client -->|"starts execution\nvia scheduler-start"| scheduler
    scheduler -->|"maintains"| queue
    scheduler -->|"creates/manages"| workermgmt
    workermgmt -->|"spawns"| workers
    jobdistribution -->|"sends jobs to"| workers
    workers -->|"returns results to"| scheduler
    queue -->|"provides jobs to"| jobdistribution
```

Sources: [jobsched/server.rkt:50-98](), [jobsched/scribblings/jobsched.scrbl:21-49]()

## Core Data Structures

### Scheduler Structure

The `scheduler` struct is the main data structure that encapsulates the server component's state:

```mermaid
classDiagram
    class scheduler {
        queue : heap
        K : integer
        make-worker-command : function
        workers : list
        worker-idx : integer
        n-active-jobs : integer
    }
    
    class worker {
        index : any
        cmd : any
        in : port
        out : port
        err : port
        pid : integer
        handler : function
        start-ms : integer
        job : job
        state : symbol
    }
    
    class job {
        index : integer
        cost : number
        data : any
        start-ms : integer
        stop-ms : integer
    }
    
    scheduler "1" --> "*" worker : manages
    worker "0..1" --> "1" job : processes
```

Sources: [jobsched/server.rkt:51-67](), [jobsched/server.rkt:102-117](), [jobsched/scribblings/jobsched.scrbl:160-174]()

The scheduler struct's fields include:

- `queue`: A priority queue of jobs (implemented with a heap)
- `K`: Number of jobs that have been added
- `make-worker-command`: Function to create the command for starting a worker
- `workers`: List of active worker structures
- `worker-idx`: Index for assigning IDs to new workers
- `n-active-jobs`: Count of currently running jobs

### Worker States

Workers are managed through a state machine with the following states:

| State | Description |
|-------|-------------|
| `state:starting` | Worker process is starting up |
| `state:ready?-sent` | Server sent "ready?" message to worker |
| `state:ready` | Worker is ready to receive jobs |
| `state:running` | Worker is processing a job |
| `state:killed` | Worker has been terminated |
| `state:closing` | Worker is in the process of closing |
| `state:closed` | Worker has closed successfully |

Sources: [jobsched/server.rkt:110-117]()

## Server Operations

### Creating a Scheduler

The server component begins with creating a scheduler using `make-scheduler`, which initializes the scheduler with a job queue and a function to create worker commands:

```mermaid
sequenceDiagram
    participant Client
    participant Scheduler as "scheduler"
    participant Queue as "priority queue"
    
    Client->>Scheduler: make-scheduler(make-worker-command)
    Scheduler->>Queue: make-heap(comparator)
    Note over Queue: Creates priority queue ordered by job cost
    Scheduler-->>Client: Returns new scheduler
```

Sources: [jobsched/server.rkt:60-67]()

### Adding Jobs

Jobs are added to the scheduler's queue using `scheduler-add-job!`, which assigns a unique index to each job and adds it to the priority queue:

```mermaid
sequenceDiagram
    participant Client
    participant Scheduler as "scheduler"
    participant Queue as "priority queue"
    
    Client->>Scheduler: scheduler-add-job!(sched, data, cost)
    Scheduler->>Scheduler: scheduler-next-job-index!
    Scheduler->>Scheduler: Create job struct
    Scheduler->>Queue: heap-add!(queue, job)
    Queue-->>Scheduler: Job added to queue
```

Sources: [jobsched/server.rkt:93-98]()

### Starting the Scheduler

The `scheduler-start` function is the main entry point for starting the server operation. It:

1. Verifies there are no active jobs
2. Adjusts the number of workers to match the requested number
3. Initializes communication with workers
4. Enters the main execution loop to process jobs

```mermaid
flowchart TD
    start["scheduler-start"]
    checkJobs["Check no active jobs"]
    adjustWorkers["Adjust worker count"]
    initComm["Initialize worker communication"]
    mainLoop["Enter main execution loop"]
    finish["Optionally close workers"]
    
    start --> checkJobs
    checkJobs --> adjustWorkers
    adjustWorkers --> initComm
    initComm --> mainLoop
    mainLoop --> finish
    
    subgraph "Main Execution Loop"
        waitWorker["Wait for worker event"]
        processResponse["Process worker response"]
        checkReady["Is worker ready?"]
        sendJob["Send next job to worker"]
        moreJobs["More active jobs?"]
        
        waitWorker --> processResponse
        processResponse --> checkReady
        checkReady -->|"Yes"| sendJob
        sendJob --> moreJobs
        checkReady -->|"No"| moreJobs
        moreJobs -->|"Yes"| waitWorker
    end
```

Sources: [jobsched/server.rkt:183-311]()

#### Main Execution Loop

The server's main execution loop handles three primary cases:

1. **Worker is ready**: When a worker signals it's ready, the server assigns it a job from the queue
2. **Worker completed job**: When a worker returns a job result, the server processes it and marks the worker as ready
3. **Worker terminated**: If a worker unexpectedly terminates, the server requeues its job and starts a new worker

Sources: [jobsched/server.rkt:246-311]()

### Managing Workers

The server creates workers using `start-worker`, which spawns a new OS process for each worker:

```mermaid
sequenceDiagram
    participant Server
    participant OS
    participant Worker
    
    Server->>OS: process*/ports(cmd)
    OS->>Worker: Start worker process
    OS-->>Server: Return communication ports & process info
    Server->>Server: Create worker struct
```

Workers can be closed gracefully using `worker-close` or forcibly terminated using `worker-kill`.

Sources: [jobsched/server.rkt:120-158]()

## Higher-Level APIs

The server component provides several higher-level APIs for common use cases:

### make-server

`make-server` creates a scheduler with a specified worker file:

```mermaid
flowchart LR
    makeServer["make-server"]
    makeWorkerCmd["create worker command function"]
    makeScheduler["make-scheduler"]
    startServer["server-start (optional)"]
    
    makeServer --> makeWorkerCmd
    makeWorkerCmd --> makeScheduler
    makeScheduler --> startServer
```

Sources: [jobsched/server.rkt:326-341]()

### server-start

`server-start` provides a simpler interface for starting a scheduler with a list of job data:

```mermaid
flowchart LR
    serverStart["server-start"]
    addJobs["Add jobs from data-list"]
    schedStart["scheduler-start"]
    
    serverStart --> addJobs
    addJobs --> schedStart
```

Sources: [jobsched/server.rkt:344-354]()

### start-simple-server

`start-simple-server` combines `make-server`, `server-start`, and `server-close` into a single function for the most common use case:

```mermaid
flowchart LR
    simpleServer["start-simple-server"]
    makeServer["make-server"]
    serverStart["server-start"]
    serverClose["server-close"]
    
    simpleServer --> makeServer
    makeServer --> serverStart
    serverStart --> serverClose
```

Sources: [jobsched/server.rkt:362-375](), [jobsched/scribblings/jobsched.scrbl:88-112]()

## Communication Protocol

The server component communicates with workers through input/output ports using a message-based protocol:

| Message Type | Direction | Purpose |
|--------------|-----------|---------|
| `message:ask-ready` | Server → Worker | Ask if worker is ready to receive jobs |
| `message:ready` | Worker → Server | Indicate worker is ready for jobs |
| `message:close-worker` | Server → Worker | Instruct worker to close |
| Job data | Server → Worker | Send job to worker for processing |
| Job result | Worker → Server | Return job result to server |

Sources: [jobsched/server.rkt:127-136](), [jobsched/server.rkt:254-288]()

## Integration with LTS-CM

Within the levintreesearch_cm system, the server component is used to distribute search tasks and coordinate optimization:

```mermaid
sequenceDiagram
    participant Main as "server-main (LTS-CM)"
    participant Sched as "scheduler (JobSched)"
    participant Workers as "Workers"
    
    Main->>Sched: make-server(worker-file)
    Main->>Sched: server-start(data-list)
    Sched->>Workers: Spawn worker processes
    Sched->>Workers: Distribute search tasks
    Workers-->>Sched: Return solution results
    Sched-->>Main: Process results
    Main->>Sched: server-close()
```

Sources: [jobsched/scribblings/jobsched.scrbl:177-234]()

## Error Handling and Recovery

The server component includes mechanisms for handling worker failures:

1. If a worker terminates unexpectedly, the server:
   - Detects the EOF on the worker's output port
   - Retrieves the job that was assigned to the worker
   - Returns the job to the queue
   - Starts a new worker process to replace the failed one

Sources: [jobsched/server.rkt:254-265]()

---

