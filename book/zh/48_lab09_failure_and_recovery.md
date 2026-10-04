# 实训九 故障注入、预算停止与部分结果

## 目标与成功定义

本实训故意让流程不能全部完成。你的任务不是消除所有错误，而是确认系统没有把未完成的操作写成成功，没有在预算耗尽后继续执行，也没有丢失已经完成的有效结果。

科研任务的失败可能来自输入、工具、权限或证据。一个只有成功路径的程序，遇到真实数据时往往最危险。我们先使用预算耗尽这种可控故障，再检查路径和依赖错误。

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from bioagent.demo import run_demo

with TemporaryDirectory() as directory:
    for limit in [0, 1, 5, 10]:
        result = run_demo(Path(directory) / str(limit), budget_limit=limit)
        assert result["stop_reason"] == "budget_exhausted"
        assert result["budget"]["used"] <= limit
        assert result["real_biological_validation"] is False
        print(limit, result["completed_steps"])
```

## 解释部分完成

预算为0时，不能完成数据审计；预算稍高时，可能已经运行数值工具，但没有完成证据比较。不同输出对应不同进度。不能把最终没有报错理解为全部科研工作完成，因为教学程序会在停止后仍然保存一份部分报告。

查看报告中的 `completed_steps` 与 `stop_reason`。部分报告应说明已做什么、没有做什么、为什么停止。它不应补写未执行步骤的预期结果。

在命令行中，预算耗尽返回非零退出状态，方便自动化流程判断是否需要人工处理。保存报告与退出失败可以同时发生；两者并不矛盾。

## 输入失败与预算失败不能混同

预算不足可能通过增加资源解决，重复样本标识则必须先修复输入。对重复标识一味重试，不会增加任何信息。为错误设置类型，是为了让Supervisor选择正确处理路径。

```python
from bioagent.biology import audit_sample_ids

bad_samples = [{"sample_id": "D1"}, {"sample_id": "D1"}]
try:
    audit_sample_ids(bad_samples)
except ValueError as error:
    print("Input rejected:", error)
```

不要让模型把重复记录自动合并，除非研究规则明确允许且可以核对来源。重复可能代表同一文件重复导入，也可能代表不同时间点误用了同一标识，两者处理不同。

## 依赖环与未知依赖

建立一个A等待B、B等待A的工作流。正确行为是拒绝，而不是无限等待。再加入一个不存在的依赖，检查错误能否在执行前被发现。

```python
from bioagent.runtime import topological_order

graphs = [
    {"A": {"B"}, "B": {"A"}},
    {"A": {"missing_task"}},
]
for graph in graphs:
    try:
        topological_order(graph)
    except ValueError as error:
        print(error)
```

这些错误属于计划结构，不需要让语言模型反复解释。可以先用确定性校验找出问题，再由模型辅助重新组织计划。

## 路径边界

用隔离临时目录检查工作区路径。正常相对路径应被接受，试图走出根目录的路径应被拒绝。此测试不执行任何删除，也不读真实敏感文件。

```python
from bioagent.runtime import safe_path

with TemporaryDirectory() as directory:
    root = Path(directory)
    print(safe_path(root, "report.json"))
    try:
        safe_path(root, "../outside.json")
    except PermissionError:
        print("Workspace escape rejected")
```

这只是应用层路径保护。多用户服务仍需操作系统权限、容器或其他隔离。测试通过不能被写成“已经完全安全”。

## 恢复应该创建什么记录

增加预算后重新运行，建议创建新目录，并记录它对应哪次失败。不要覆盖失败记录，否则无法解释第一次为何没有完成。对大型流程，未来可以实现经过验收的中间产物恢复；本版教学演示采用重新运行，不声称已经实现生产级断点续跑。

若复用中间结果，缓存键至少应包含输入、参数和工具版本。只看文件名存在就跳过任务，会把错误或过期产物当成有效结果。

## 提交与参考答案

提交四种预算下的完成步骤、两个依赖错误与一个路径越界拒绝。写明哪些问题可以通过增加预算解决，哪些需要修复数据或计划。

参考答案应指出：正确停止是可靠行为；部分报告不能冒充完整结论；恢复必须保存版本；程序控制问题优先用确定性规则处理，而不是无限反思。
