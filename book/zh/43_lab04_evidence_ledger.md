# 实训四 建立支持、冲突与缺失并存的证据台账

## 目标与规则

本实训用少量人工编写记录，检查台账是否尊重研究独立性、情境和模拟标记。所有文本仍为教学材料。为了观察规则，代码中会同时使用真实标记与合成标记的测试对象；这些布尔值仅是测试输入，不代表材料成为真实研究。

```python
from bioagent.evidence import Evidence, EvidenceLedger

items = [
    Evidence("E1", "S1", "C1", "test support", "fixture://1", "supports", "human"),
    Evidence("E2", "S1", "C1", "same study fragment", "fixture://2", "supports", "human"),
    Evidence("E3", "S2", "C1", "test conflict", "fixture://3", "contradicts", "human"),
    Evidence("E4", "S3", "C1", "other context", "fixture://4", "supports", "mouse"),
    Evidence("E5", "S4", "C2", "synthetic only", "synthetic://5", "supports", "human", True),
]
ledger = EvidenceLedger(items)
print(ledger.assess("C1", context="human"))
```

## 研究数量与片段数量

C1在人群情境下有两条支持片段，但都来自S1，因此支持研究集合只有一个元素。另一个研究S2提供冲突，结果应为 `conflicted`。这比计算三条片段的简单多数更合理。

检查 `evidence_ids` 与 `support_studies` 的长度，说明两个分母不同。实际项目还需处理部分样本重叠；本实训只识别相同研究标识这一种明确重复。

```python
result = ledger.assess("C1", context="human")
assert result["support_studies"] == ["S1"]
assert result["contradicting_studies"] == ["S2"]
assert result["verdict"] == "conflicted"
```

## 情境过滤

改为mouse情境时，只保留E4。这个例子展示情境匹配的必要性，但也展示一个限制：当前实现使用精确字符串匹配。真实情境可能涉及物种、组织、剂量和设计多个字段，不能只靠一个单词表达。

将情境设为None会聚合所有情境。这样的操作在教学中可以观察，但真实报告必须说明它意味着什么。不能无条件把动物和人群结果混在一起后宣称人群关系被支持。

## 合成材料默认不算真实支持

C2只有一条合成证据。默认评估应为不足；显式允许合成后可以观察教学状态，但输出仍带有合成标记。这个开关是为了测试流程，不是让研究者跳过证据核验。

```python
assert ledger.assess("C2", context="human")["verdict"] == "insufficient"
teaching = ledger.assess("C2", context="human", include_synthetic=True)
assert teaching["synthetic_included"] is True
```

把真实研究接入台账时，必须检查来源和方向注释。当前程序相信输入注释，不会自动阅读全文判断是否支持。因此 `supported_in_context` 的含义是“按已提供注释聚合后支持”，不是独立语义验证的完成证明。

## 未知引用与重复标识

尝试引用不存在的E999，应被拒绝。尝试再次加入E1，也应被拒绝。这些是最基本的完整性检查，但不能代替检查E1内容是否正确。

```python
try:
    ledger.check_citations(["E999"])
except ValueError:
    print("Unknown citation rejected")
try:
    ledger.add(items[0])
except ValueError:
    print("Duplicate evidence ID rejected")
```

## 假设修订后重新核验

创建一个绑定C1的候选，随后把claim改为C2。新版本应清空旧核验链接，保留父版本，并按C2重新评估。旧文档仍在台账，但与新陈述的支持关系不能自动继承。

```python
from bioagent.evidence import Candidate
old = Candidate("H1", "old statement", ("C1",), verified_links=("E1",))
new = old.revise("new statement", ("C2",))
assert old.verified_links == ("E1",)
assert new.verified_links == ()
print(ledger.assess_candidate(new, context="human"))
```

## 提交与参考答案

提交一张表，分别记录C1在人群、动物与不限定情境下的结果，以及C2是否允许合成时的结果。解释哪些变化来自证据，哪些只是聚合规则变化。

参考答案应强调：方向注释需要外部核验；相同研究片段不能重复计数；冲突与缺失不是同义词；修改布尔字段不改变材料真实性；假设修订需要重新建立支持关系。
