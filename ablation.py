import json
import os
import jieba
from neo4j import GraphDatabase

desktop = os.path.expanduser("~/Desktop")
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "weibize110325"

driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

with open(os.path.join(desktop, "dongba_dict.json"), "r", encoding="utf-8") as f:
    dictionary = json.load(f)

with open(os.path.join(desktop, "testset.json"), "r", encoding="utf-8") as f:
    testset = json.load(f)

# ===== 完整版DPKG =====
def dpkg_full(query, top_k=5):
    search_term = query[:15]
    words = [w for w in jieba.cut(query) if len(w) > 1]
    with driver.session() as session:
        result = session.run("""
            MATCH (c:Character)-[:BELONGS_TO]->(cat:Category)
            WHERE c.meaning CONTAINS $search_term
            OR c.phonetic CONTAINS $search_term
            OR cat.name CONTAINS $search_term
            WITH c, cat,
                CASE WHEN c.meaning CONTAINS $search_term THEN 3 ELSE 0 END +
                CASE WHEN c.phonetic CONTAINS $search_term THEN 2 ELSE 0 END +
                CASE WHEN cat.name CONTAINS $search_term THEN 2 ELSE 0 END +
                CASE WHEN c.scripture_relevance = 'high' THEN 1 ELSE 0 END as score
            RETURN c.id as id, score ORDER BY score DESC LIMIT 20
        """, search_term=search_term)
        kg_results = {r["id"]: r["score"] for r in result}
    for entry in dictionary:
        if entry["id"] not in kg_results:
            meaning = entry.get("meaning", "")
            score = sum(1 for w in words if w in meaning)
            if score > 0:
                kg_results[entry["id"]] = score * 0.5
    return sorted(kg_results.keys(), key=lambda x: kg_results[x], reverse=True)[:top_k]

# ===== 去掉scripture_relevance =====
def dpkg_no_scripture(query, top_k=5):
    search_term = query[:15]
    words = [w for w in jieba.cut(query) if len(w) > 1]
    with driver.session() as session:
        result = session.run("""
            MATCH (c:Character)-[:BELONGS_TO]->(cat:Category)
            WHERE c.meaning CONTAINS $search_term
            OR c.phonetic CONTAINS $search_term
            OR cat.name CONTAINS $search_term
            WITH c,
                CASE WHEN c.meaning CONTAINS $search_term THEN 3 ELSE 0 END +
                CASE WHEN c.phonetic CONTAINS $search_term THEN 2 ELSE 0 END +
                CASE WHEN cat.name CONTAINS $search_term THEN 2 ELSE 0 END as score
            RETURN c.id as id, score ORDER BY score DESC LIMIT 20
        """, search_term=search_term)
        kg_results = {r["id"]: r["score"] for r in result}
    for entry in dictionary:
        if entry["id"] not in kg_results:
            meaning = entry.get("meaning", "")
            score = sum(1 for w in words if w in meaning)
            if score > 0:
                kg_results[entry["id"]] = score * 0.5
    return sorted(kg_results.keys(), key=lambda x: kg_results[x], reverse=True)[:top_k]

# ===== 去掉分类匹配 =====
def dpkg_no_category(query, top_k=5):
    search_term = query[:15]
    words = [w for w in jieba.cut(query) if len(w) > 1]
    with driver.session() as session:
        result = session.run("""
            MATCH (c:Character)
            WHERE c.meaning CONTAINS $search_term
            OR c.phonetic CONTAINS $search_term
            WITH c,
                CASE WHEN c.meaning CONTAINS $search_term THEN 3 ELSE 0 END +
                CASE WHEN c.phonetic CONTAINS $search_term THEN 2 ELSE 0 END +
                CASE WHEN c.scripture_relevance = 'high' THEN 1 ELSE 0 END as score
            RETURN c.id as id, score ORDER BY score DESC LIMIT 20
        """, search_term=search_term)
        kg_results = {r["id"]: r["score"] for r in result}
    for entry in dictionary:
        if entry["id"] not in kg_results:
            meaning = entry.get("meaning", "")
            score = sum(1 for w in words if w in meaning)
            if score > 0:
                kg_results[entry["id"]] = score * 0.5
    return sorted(kg_results.keys(), key=lambda x: kg_results[x], reverse=True)[:top_k]

# ===== 去掉GLM-4V语义标注 =====
def dpkg_no_glmv(query, top_k=5):
    search_term = query[:15]
    words = [w for w in jieba.cut(query) if len(w) > 1]
    with driver.session() as session:
        result = session.run("""
            MATCH (c:Character)
            WHERE c.meaning CONTAINS $search_term
            OR c.phonetic CONTAINS $search_term
            WITH c,
                CASE WHEN c.meaning CONTAINS $search_term THEN 3 ELSE 0 END +
                CASE WHEN c.phonetic CONTAINS $search_term THEN 2 ELSE 0 END as score
            RETURN c.id as id, score ORDER BY score DESC LIMIT 20
        """, search_term=search_term)
        kg_results = {r["id"]: r["score"] for r in result}
    for entry in dictionary:
        if entry["id"] not in kg_results:
            meaning = entry.get("meaning", "")
            score = sum(1 for w in words if w in meaning)
            if score > 0:
                kg_results[entry["id"]] = score * 0.5
    return sorted(kg_results.keys(),
                  key=lambda x: kg_results[x], reverse=True)[:top_k]

# ===== 去掉jieba扩展 =====
def dpkg_no_jieba(query, top_k=5):
    search_term = query[:15]
    with driver.session() as session:
        result = session.run("""
            MATCH (c:Character)-[:BELONGS_TO]->(cat:Category)
            WHERE c.meaning CONTAINS $search_term
            OR c.phonetic CONTAINS $search_term
            OR cat.name CONTAINS $search_term
            WITH c, cat,
                CASE WHEN c.meaning CONTAINS $search_term THEN 3 ELSE 0 END +
                CASE WHEN c.phonetic CONTAINS $search_term THEN 2 ELSE 0 END +
                CASE WHEN cat.name CONTAINS $search_term THEN 2 ELSE 0 END +
                CASE WHEN c.scripture_relevance = 'high' THEN 1 ELSE 0 END as score
            RETURN c.id as id, score ORDER BY score DESC LIMIT 20
        """, search_term=search_term)
        kg_results = {r["id"]: r["score"] for r in result}
    return sorted(kg_results.keys(), key=lambda x: kg_results[x], reverse=True)[:top_k]

# ===== 评估 =====
def evaluate(fn, name):
    tp = fp = fn_count = 0
    for item in testset:
        retrieved = fn(item["query"])
        if item["answer_id"] in retrieved:
            tp += 1
        else:
            fn_count += 1
            fp += len(retrieved)
    p = tp / (tp + fp) if (tp + fp) > 0 else 0
    r = tp / (tp + fn_count) if (tp + fn_count) > 0 else 0
    f1 = 2*p*r / (p+r) if (p+r) > 0 else 0
    print(f"{name}: P={p*100:.1f}% R={r*100:.1f}% F1={f1*100:.1f}%")
    return {"system": name, "precision": round(p,4), "recall": round(r,4), "f1": round(f1,4)}

print("\n消融实验开始")
print("="*50)
results = []
results.append(evaluate(dpkg_full,         "DPKG (Full)"))
results.append(evaluate(dpkg_no_scripture, "w/o Scripture Relevance"))
results.append(evaluate(dpkg_no_category,  "w/o Category Matching"))
results.append(evaluate(dpkg_no_glmv,      "w/o GLM-4V Annotation"))
results.append(evaluate(dpkg_no_jieba,     "w/o Jieba Expansion"))

with open(os.path.join(desktop, "ablation_results.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n结果保存在：ablation_results.json")
driver.close()