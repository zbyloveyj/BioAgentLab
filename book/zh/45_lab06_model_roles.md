# 实训六 用模型接口连接生成、反思与修订

## 目标与离线模型

本实训使用脚本模型测试角色契约。它不会真正发现新机制，而是返回预定JSON，让你检查生成、反思和修订之间的字段与状态。先把接口正确性与模型能力分开，之后再接入外部模型。

```python
from bioagent.demo import DemoModel, CLAIMS
from bioagent.research import ResearchAgents
from bioagent.evidence import EvidenceLedger

agents = ResearchAgents(DemoModel(), set(CLAIMS))
candidates = agents.generate("核对微生物—代谢物—宿主候选关系")
for candidate in candidates:
    print(candidate.identifier, candidate.claim_ids)
```

预期得到三个候选，每个只引用已注册claim。模型不能通过输出一个新编号就让它自动成为已知关系。

## 让证据状态进入反思

使用空台账评估第一个候选。所有必需claim都应显示不足。把这个状态交给反思模块，检查批评是否与当前缺口一致，而不只是泛泛称赞。

```python
ledger = EvidenceLedger()
parent = candidates[0]
assessment = ledger.assess_candidate(parent)
critiques = agents.reflect(parent, assessment)
print(assessment["unresolved"])
print(critiques)
```

脚本模型的批评只是教学预定文本。真实模型接入后，必须检查它是否准确描述台账，是否提出不存在的问题，以及是否添加未经核验的新来源。

## 修订产生新版本

将批评交给进化模块，新候选应有更高版本号、父版本记录和空的核验链接。旧候选不应被修改。这个性质可以用断言检查。

```python
child = agents.evolve(parent, critiques)
assert child.version == parent.version + 1
assert child.parent == f"{parent.identifier}:v{parent.version}"
assert child.verified_links == ()
assert parent.version == 1
print(child.statement)
print(ledger.assess_candidate(child)["unresolved"])
```

如果修订只是把“相关”改成“导致”，却保留原支持状态，系统会发生证据层级提升。版本化本身不能防止这种错误，但重新核验可以暴露变化。

## 流畅但不符合契约的输出

创建一个返回自然语言的模型。虽然输出看起来友好，但因为没有满足JSON契约，程序应该拒绝。不要在解析失败时用正则随意猜出字段，再继续执行高风险动作。

```python
from bioagent.core import CallableLLMClient
from bioagent.research import ContractError

bad = ResearchAgents(
    CallableLLMClient(lambda prompt: "我已经仔细分析，结论非常可靠。"),
    set(CLAIMS),
)
try:
    bad.generate("test")
except ContractError:
    print("Non-JSON response rejected")
```

真实系统可以进行一次受约束的格式修复，但应保存原始错误，并确保修复不添加事实。格式修复与科学核验是不同阶段。

## 未知claim注入

让模型返回格式正确、但claim不存在的JSON。程序应同样拒绝。这展示了语法正确并不意味着语义引用有效。

```python
import json
payload = {"candidates": [{
    "id": "H9", "statement": "a candidate",
    "claim_ids": ["NOT_REGISTERED"],
}]}
model = CallableLLMClient(lambda prompt: json.dumps(payload))
try:
    ResearchAgents(model, set(CLAIMS)).generate("test")
except ContractError:
    print("Unknown claim rejected")
```

## 接入真实模型时保留哪些规则

替换 `DemoModel` 时，不删除JSON校验、claim白名单、证据台账和预算。模型更强并不意味着这些规则不再需要。相反，输出越复杂，越需要明确边界。

外部模型只能在明确授权的数据范围内调用。先使用合成问题验证网络适配，再考虑真实材料。没有实际在线测试时，报告应写适配器已实现、离线解析已测试，而不是声称真实服务已验证。

## 提交与参考答案

提交正常生成与修订结果、自然语言错误输出和未知claim错误输出。说明哪一层负责语言生成，哪一层负责字段检查，哪一层负责证据判断。

参考答案应强调：脚本模型验证流程，不验证智能水平；新版本不继承旧核验；格式正确、引用存在与来源支持仍是三道不同门。
