# 附录B 项目接口与文件速查

## 先选择正确入口

阅读教材从 `book/zh/` 开始，运行综合案例使用 `python -m bioagent demo`，检查行为使用pytest。旧的 `scientific_agents.py` 与 `supervisor.py` 保留为入门示例；证据管理应优先使用新的 `evidence.py`、`research.py` 与 `demo.py`。

默认演示不需要外部密钥。联网PubMed与文本模型适配是可选能力，必须由使用者明确选择。它们的本版测试包括本地解析与契约，不把未执行的真实网络调用算成成功。

## 命令行

```bash
# 安装与测试
python -m pip install -e ".[dev]"
python -m pytest -q

# 离线教学工作流
python -m bioagent demo --out runs/example

# 有限预算，可能返回部分报告和非零退出状态
python -m bioagent demo --out runs/limited --budget 5

# 明确覆盖教学输出；谨慎使用
python -m bioagent demo --out runs/example --overwrite

# 显式联网：仅检索PubMed元数据
python -m bioagent pubmed "microbiome AND metabolomics" \
  --email researcher@example.org --limit 5 --out runs/search.json
```

最后一条命令中的邮箱只是示例，实际使用必须填写有效联系地址。不要把密钥放进命令文本或公共日志。

## 证据接口

`Evidence`要求证据ID、研究ID、claim ID、文本和来源；方向限定为supports、contradicts或unknown。context表达适用情境，synthetic保留模拟标记。所有必填字符串不能为空。

`EvidenceLedger.add`拒绝重复证据标识；`check_citations`拒绝未知引用；`assess`可以按情境筛选，默认排除合成材料，并按研究标识聚合支持与反对；`assess_candidate`逐条检查候选必需关系。

```python
from bioagent.evidence import Candidate, EvidenceLedger

candidate = Candidate("H1", "a testable candidate", ("C1", "C2"))
result = EvidenceLedger().assess_candidate(candidate)
assert result["unresolved"] == ["C1", "C2"]
assert result["causal_validation"] is False
```

台账不自动验证网页真实性，也不自动阅读全文判断方向。输入注释必须由可靠过程获得。context的精确匹配只是教学实现，真实项目可以扩展为物种、组织、暴露与设计等结构字段。

## 检索与相近性

`Document(identifier, text, source)`保存本地资料；`BM25Index(documents)`建立索引；`search(query, top_k)`返回文档与检索分数。分数用于检索排序，不等于证据质量。

`terms`支持英文词项与中文双字片段；`jaccard`提供轻量相似度。它们不具备完整生物医学实体理解，机制方向与同义关系仍需结构化核对。

## 数值工具

`clr(values, pseudocount=None)`返回对数比向量；输入必须有限、非负且非全零；含零时必须明确处理。`bh_adjust(values)`保留输入顺序返回调整值，拒绝非法P值。

`audit_sample_ids(rows)`检查非空与唯一标识；`align_by_id(left,right)`根据标识连接并返回未匹配对象。它不自动检查采样时间，真实纵向数据需要扩展连接条件。

`pseudobulk(cells)`按donor_id与cell_type聚合整数原始计数，检查cell_id唯一、维度一致和字段完整。输出不是差异表达结果，不包含计数模型拟合。

## 运行时与角色

`Budget`记录动作额度；`ToolRegistry`校验工具名、签名与审批后执行；`safe_path`限制工作区路径；`EventLog`写入单进程JSONL；`topological_order`检查依赖图。

`ResearchAgents`提供JSON契约的生成、反思与修订接口。`Candidate.revise`创建新版本并清空旧核验链接。`elo_pair`与`tournament`组织成对偏好，None表示无法比较而不是平局。

这些模块可以独立使用，不要求全部任务都调用模型。例如样本标识检查直接使用数值或数据函数即可。

## 产物格式

`report.json`保存机器可读状态、证据与结果；`report.md`保存阅读版说明；`trace.jsonl`保存事件；`manifest.json`保存版本和产物摘要。修改结果后需重新形成版本，而不是偷偷修改哈希。

构建教材使用 `scripts/build_book.py`。它读取排好顺序的Markdown，经Pandoc与XeLaTeX生成PDF，并记录实际页数和源文字数。`--min-pages 200`只检查结果，不会自动插入空页。

## 已实现与未验证边界

本版实现的是教学框架、离线证据聚合、轻量检索、基础数值函数、模型接口和测试。没有宣称实现完整宏基因组流水线、正式单细胞差异分析、自动实验执行、临床诊断或经独立队列验证的自主发现。

升级时以具体测试与运行记录为准。目录中出现一个领域名称，不代表该领域全部分析已经接入。
