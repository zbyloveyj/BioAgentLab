# 实训十 审计最终报告，并形成自己的最小研究项目

## 目标与审计对象

最后一项实训不再增加算法，而是检查最终交付是否值得信任。你将使用离线综合报告，核对模式、证据、版本、预算和文件完整性，并写一页真实项目的接入方案。

一个报告的审计不能只问文字是否通顺。应检查每个事实是否有来源，每个数字是否来自计算，每条假设是否保留不确定，以及所有未完成步骤是否明确。

```python
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from bioagent.demo import run_demo

with TemporaryDirectory() as directory:
    root = Path(directory) / "audit"
    report = run_demo(root)
    assert report["mode"] == "synthetic_offline_teaching"
    assert report["real_biological_validation"] is False
    assert report["budget"]["used"] <= report["budget"]["limit"]
    print(report["conclusion"])
```

## 核对引用与证据集合

报告中的证据标识应全部来自实际台账。若出现未知标识，即使它看起来像正式文献编号，也必须拒绝。然后检查合成标记是否保留，不能只依赖报告开头的一句免责声明。

```python
known_ids = {row["evidence_id"] for row in report.get("evidence", [])}
for assessment in report.get("teaching_assessment", []):
    for claim in assessment["claims"]:
        assert set(claim["evidence_ids"]) <= known_ids
assert all(row["synthetic"] for row in report["evidence"])
assert all(item["unresolved"] for item in report["real_evidence_assessment"])
```

这里的检查保证引用完整性与模式一致，不证明来源内容支持陈述。真实材料接入后，需要进一步核对原文位置、方向和适用条件。

## 审计排名的语言

报告中的Elo结果来自显式教学启发式，不是模型开展真实科学辩论，也不是真实机制概率。找到相应 `judge` 与 `interpretation` 字段，确认报告没有把它们写成“最有可能的真实机制”。

```python
ranking = report["preference_tournament"]
assert ranking["interpretation"] == "relative_preference_not_truth_probability"
assert "synthetic" in ranking["judge"]
print(ranking["ratings"])
```

这项练习强调一种常见错误：代码对数值的定义很谨慎，写作模型却在最终段落中把它升级成更强含义。报告审计必须覆盖这种语义变化。

## 审计修订版本

检查修订候选的版本号、父版本与核验链接。新版本应重新进入证据评估。即使只是教学数据，也应保持这个过程，因为真实任务中的证据继承错误往往发生在同样位置。

```python
revision = report["revision"]
assert revision["version"] == 2
assert revision["parent"].endswith(":v1")
assert not revision["verified_links"]
assert report["revision_recheck"]["unresolved"]
```

若修订后重新核验仍然不足，报告应保留不足，而不是为了展示进化效果强制给出成功。方法效果需要评估，不由演示叙事决定。

## 一页项目接入方案

选择一个足够小的真实问题，例如核验十条微生物功能claim，或审计一个已脱敏的供体样本表。接入方案写明输入来源、授权范围、独立单位、工具、输出和验收标准。

不要一次替换全部模块。可以先保持离线模型，换入合规文献元数据；确认来源与实体映射正确后，再加入模型摘要。也可以先只做数据审计，不计算疾病差异。每次扩展都对应新的测试与限制。

真实项目中最重要的变化，不是把 `synthetic` 改成false，而是建立实际来源和核验过程。未经核实的材料仍应标记为待审，不因为来自真实网页就自动有效。

## 形成发布清单

交付应包括代码版本、任务契约、运行配置、测试结果、产物清单、来源记录和限制。真实数据不能公开时，保留受控访问说明，并提供足以运行的合成替代输入。

README应说清哪些功能已实现，哪些仅有适配接口，哪些尚未验证。一个只读PubMed解析器与完整系统综述工具不是同一种能力；供体聚合与正式差异表达也不是同一种能力。

## 结课提交与参考标准

提交一份经审计的教学报告和一页真实接入方案。审核者应能够从报告返回证据记录，从结果返回代码与输入，从失败返回日志，并看到所有模拟和未验证边界。

参考标准不是报告字数或架构复杂度，而是：输入可追溯、工具有契约、独立单位正确、引用可核对、修订有版本、错误能停止。达到这些条件，才适合进一步研究更复杂的自主决策。
