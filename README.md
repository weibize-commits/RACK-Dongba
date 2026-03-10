# RACK-Dongba
Dongba Script Knowledge Graph Dataset and Code
import json, csv, os

desktop = os.path.expanduser("~/Desktop")
out = os.path.join(desktop, "RACK-Dongba-release")
os.makedirs(out, exist_ok=True)
os.makedirs(os.path.join(out, "data"), exist_ok=True)
os.makedirs(os.path.join(out, "code"), exist_ok=True)

# 1. 读取原始数据
with open(os.path.join(desktop, "dongba_dict.json"), encoding="utf-8") as f:
    entries = json.load(f)

with open(os.path.join(desktop, "testset.json"), encoding="utf-8") as f:
    testset = json.load(f)

with open(os.path.join(desktop, "ahp_results.json"), encoding="utf-8") as f:
    ahp = json.load(f)

# 2. 生成 char_metadata.csv（只含id+类别+统计，不含原文释义）
with open(os.path.join(out, "data", "char_metadata.csv"),
          "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "category", "scripture_relevance",
                     "audience_level", "novice_load_level",
                     "meaning_length", "has_phonetic"])
    for e in entries:
        meaning = e.get("meaning", "") or ""
        writer.writerow([
            e.get("id", ""),
            e.get("category", ""),
            e.get("scripture_relevance", "low"),
            e.get("audience_level", ""),
            e.get("novice_load_level", ""),
            len(meaning),
            1 if e.get("phonetic") else 0
        ])

# 3. 生成 ritual_events.json
ritual_events = {
    "scripture": "普蛊鸟路的故事 (The Story of Pugubirdway)",
    "events": [
        {"id": "RE1", "name": "Conflict Event",
         "name_zh": "争斗事件",
         "description": "Human conflict and confrontation scenes",
         "primary_category": "人文", "linked_chars": 325,
         "confidence": 0.85},
        {"id": "RE2", "name": "Offering Event",
         "name_zh": "祭祀供奉事件",
         "description": "Food offering and ancestral ritual scenes",
         "primary_category": "饮食", "linked_chars": 97,
         "confidence": 0.82},
        {"id": "RE3", "name": "Ritual Chanting Event",
         "name_zh": "仪式念经事件",
         "description": "Dongba priest chanting and deity communication",
         "primary_category": "若喀字", "linked_chars": 59,
         "confidence": 0.91}
    ]
}
with open(os.path.join(out, "data", "ritual_events.json"),
          "w", encoding="utf-8") as f:
    json.dump(ritual_events, f, ensure_ascii=False, indent=2)

# 4. 生成 cognitive_load_rules.json
rules = {
    "description": "SWRL-based cognitive load classification rules for novice users",
    "rules": [
        {"rule_id": "R1", "condition": "category IN [若喀字,宗教,神,鬼怪,东巴龙王] AND meaning_length > 20",
         "label": "high", "rationale": "Ritual-specific characters unfamiliar to novices"},
        {"rule_id": "R2", "condition": "scripture_relevance = high AND has_ritual_keyword = True",
         "label": "high", "rationale": "Characters appearing in ritual contexts"},
        {"rule_id": "R3", "condition": "category IN [人体,植物,饮食,兽,鸟]",
         "label": "low", "rationale": "Everyday semantic categories accessible to novices"},
        {"rule_id": "R4", "condition": "otherwise",
         "label": "medium", "rationale": "Default classification"}
    ],
    "distribution": {"high": 161, "medium": 1081, "low": 546}
}
with open(os.path.join(out, "data", "cognitive_load_rules.json"),
          "w", encoding="utf-8") as f:
    json.dump(rules, f, ensure_ascii=False, indent=2)

# 5. 生成 testset_public.json（只含查询和ID，不含完整释义）
testset_public = []
for item in testset:
    testset_public.append({
        "id": item.get("id", ""),
        "query": item.get("query", ""),
        "query_type": item.get("query_type", ""),
        "correct_id": item.get("correct_id", "")
    })
with open(os.path.join(out, "data", "testset_public.json"),
          "w", encoding="utf-8") as f:
    json.dump(testset_public, f, ensure_ascii=False, indent=2)

# 6. 生成 dataset_statistics.json
from collections import Counter
categories = [e.get("category","") for e in entries]
cat_count = Counter(categories)
stats = {
    "total_characters": len(entries),
    "categories": dict(cat_count),
    "scripture_high_relevance": sum(1 for e in entries if e.get("scripture_relevance")=="high"),
    "ritual_events": 3,
    "novice_load_distribution": {"high": 161, "medium": 1081, "low": 546},
    "source": "Dongba Script Dictionary (云南人民出版社)",
    "note": "Full character entries available upon reasonable request due to copyright restrictions"
}
with open(os.path.join(out, "data", "dataset_statistics.json"),
          "w", encoding="utf-8") as f:
    json.dump(stats, f, ensure_ascii=False, indent=2)

# 7. 生成 AHP结果
with open(os.path.join(out, "data", "ahp_results.json"),
          "w", encoding="utf-8") as f:
    json.dump(ahp, f, ensure_ascii=False, indent=2)

# 8. 生成 README.md
readme = """# RACK-Dongba: Ritual-Aware Cognitive-Adaptive Knowledge Graph for Dongba Script Heritage

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
"""

with open(os.path.join(out, "README.md"), "w", encoding="utf-8") as f:
    f.write(readme)

print("=" * 50)
print(f"Release files generated at: {out}")
print("\nFiles created:")
for root, dirs, files in os.walk(out):
    level = root.replace(out, '').count(os.sep)
    indent = '  ' * level
    for file in files:
        print(f"{indent}  {file}")
print("=" * 50)
print("\nNext: Upload these files to GitHub")
