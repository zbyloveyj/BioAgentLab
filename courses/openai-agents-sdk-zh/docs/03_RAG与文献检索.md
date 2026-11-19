# 03 RAG 和 PubMed：从“会回答”到“有证据”

RAG（检索增强生成）不是让模型“自动学会”论文，而是先用程序找到相关内容，再把原文片段作为回答依据。本课程先使用 `agent_course/rag.py` 做词项匹配，这样每一步都可观测，不用向量数据库或显卡。

## 本地练习

```python
from agent_course.rag import retrieve
print(retrieve("宏基因组与16S区别"))
```

返回包含 `id/title/text/source` 的资料列表。注意这些卡片标注了「教学说明（非论文）」，不能变成 PubMed 参考文献。

## 真实 PubMed 接口

使用 NCBI E-utilities 的两步：ESearch 查 PMID；EFetch 获取 XML 并提取题名、摘要与发表日期。课程的 `agent_course/pubmed.py` 用 `httpx` 发请求，用 `xml.etree.ElementTree` 解析；会留下检索时间和 PubMed 网页链接。

```python
from agent_course.pubmed import search_pubmed
records = search_pubmed("gut microbiome AND depression", max_results=3)
for row in records:
    print(row["pmid"], row["title"], row["url"])
```

使用前必须在 `.env` 中设置 **NCBI_EMAIL（真实邮箱）**。本文查询字符串是练习题，不意味着存在某一具体的因果结论。摘要缺失时应空值处理，不能让大模型补写“论文摘要”。

## 模型可以总结什么？

可让模型根据返回的摘要抽取「研究对象、研究类型、观察到的关联」，但这些是自动抽取结果，需要人工核查。不要把标题和摘要里的相关性结果写成疾病因果机制。

## 有哪些进阶方向

- 语义检索：向量嵌入、向量库、chunk 分割、reranking、文献版本管理。
- 结构化核证：检索结果与提取结果逐 PMID 映射，标记原文证据位置。
- 评测：命中率、精确率、抽取一致性、幻觉率、不可回答问题的拒答率。

官方 E-utilities：https://www.ncbi.nlm.nih.gov/books/NBK25499/
