# Agent Directory

Complete directory of all agents in the ITC Enterprise Multi-Agent System.

## Orchestration Layer

| Agent ID | Name | Role | Directory |
|----------|------|------|-----------|
| `agent.project.manager` | Project Manager Agent | Task orchestration, state machine, DAG, scheduling | `agents/project-manager/` |
| `agent.critic.reviewer` | Critic Agent | Cross-cutting quality review, devil's advocate | `agents/critic/` |

## Domain Expert Layer

| Agent ID | Name | Domain | Key Skills | Directory |
|----------|------|--------|------------|-----------|
| `agent.acoustic.simulation` | Acoustic Simulation Agent | Array directivity, room acoustics, COMSOL | FEM/BEM/ray tracing, SPL mapping | `agents/acoustic-simulation/` |
| `agent.dsp.algorithm` | DSP Algorithm Agent | Beamforming, fixed-point, psychoacoustics | DSB/MVDR/GSC, Q-format optimization | `agents/dsp-algorithm/` |
| `agent.hardware.design` | Hardware Design Agent | Schematics, BOM, EMC, thermal | Power design, ADC/DAC, PCB guidance | `agents/hardware-design/` |
| `agent.structure.engineer` | Structure Engineer Agent | CAD, enclosure acoustics, DFM | 3D modeling, vibration control, sealing | `agents/structure/` |
| `agent.testing.validation` | Testing Agent | Test case generation, data analysis | Audio testing, environmental, automation | `agents/testing/` |
| `agent.literature.patent` | Literature & Patent Agent | Paper tracking, patent monitoring, risk warning | FTO analysis, technology trends | `agents/literature-patent/` |
| `agent.project.document` | Project Document Agent | Report generation, knowledge base maintenance | Technical writing, version control | `agents/project-document/` |

## Tool Layer

| Agent ID | Name | Function | Interface | Directory |
|----------|------|----------|-----------|-----------|
| `tool.code.execution` | Code Execution Agent | Python/MATLAB/C sandbox execution | JSON-RPC, Docker sandbox | `tools/code-execution/` |
| `tool.cad.interface` | CAD Interface Agent | SolidWorks/Fusion 360/CATIA integration | CAD API, file conversion | `tools/cad-interface/` |
| `tool.matlab.engine` | MATLAB Agent | Signal processing, numerical computation | MATLAB Engine API | `tools/matlab/` |
| `tool.database` | Database Agent | Structured data storage, query, analysis | SQL/REST, ACID transactions | `tools/database/` |
| `tool.web.search` | Web Search & Visualization Agent | Web search, scraping, chart generation | Search API, Plotly/Matplotlib | `tools/web-search/` |

## Human Layer

| Role | Responsibilities | Interaction Points |
|------|-----------------|-------------------|
| Chief Engineer (Human) | Final decision, key node review | 4 mandatory gates: Plan Approval, Architecture Review, Prototype Go/No-Go, Final Approval |

## Communication Matrix

```
                    CTO(Human)
                       |
                       v
              +--------+--------+
              | Project Manager |
              +--------+--------+
                       |
       +---------------+---------------+---------------+
       |               |               |               |
       v               v               v               v
+------+------+ +-----+-----+ +-----+-----+ +-----+-----+
|   Acoustic  | |    DSP    | |  Hardware | | Structure |
+------+------+ +-----+-----+ +-----+-----+ +-----+-----+
       |               |               |               |
       |               |    Critic     |               |
       +--------------->(Cross-Cutting)<----------------+
                       |               |
                       v               v
              +--------+--------+ +----+-----+
              |     Testing     | | Literature |
              +-----------------+ +-----+------+
                                        |
                                        v
                                 +------+------+
                                 |  Document   |
                                 +-------------+
```

Legend:
- `—>` = Task dispatch (solid line)
- `==>` = Review feedback (dashed line)
- `-o>` = Human review gate
