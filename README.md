# RACK-Dongba: Ritual-Aware Cognitive-Adaptive Knowledge Graph for Dongba Script Heritage

## Overview
This repository contains the dataset, code, and supplementary materials for the paper:

> **RACK-Dongba: A Ritual-Aware Cognitive-Adaptive Knowledge Graph Framework  
> for Dongba Script Intangible Cultural Heritage Preservation**

## Dataset Statistics
- **2,242** structured character entries across **17** semantic categories
- **481** scripture-relevant characters (linked to ritual contexts)
- **3** RitualEvent nodes (RE1 Conflict / RE2 Offering / RE3 Chanting)
- **Cognitive load labels**: 161 High / 1,081 Medium / 546 Low

## Repository Structure
```
RACK-Dongba/
├── data/
│   ├── char_metadata.csv          # Character metadata (id, category, load level)
│   ├── ritual_events.json         # RitualEvent node definitions
│   ├── cognitive_load_rules.json  # SWRL-based classification rules
│   ├── testset_public.json        # Experiment 1 test queries
│   ├── dataset_statistics.json    # Full dataset statistics
│   └── ahp_results.json           # AHP weight analysis results
├── code/
│   ├── import_neo4j.py            # Knowledge graph construction
│   ├── experiment1.py             # Entity retrieval evaluation
│   └── cognitive_load_rules.py    # Load classification implementation
└── README.md
```

## Data Availability
Character metadata, ritual event structures, cognitive load annotations,  
and experimental code are openly available in this repository.

Full character entries (phonetic transcriptions and semantic descriptions)  
are available upon reasonable request due to copyright restrictions  
on the source dictionary (*Dongba Script Dictionary*, Yunnan People's Publishing House).

## Citation
If you use this dataset, please cite:
```
[Citation will be added upon acceptance]
```

## Knowledge Graph Setup
Requirements: Neo4j 5.x, Python 3.10, conda environment `dongba`
```bash
conda activate dongba
python code/import_neo4j.py
```

## License
Data: CC BY-NC 4.0  
Code: MIT License
