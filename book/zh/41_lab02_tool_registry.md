# 实训二 注册一个工具，并验证它不能越权

## 目标与工具设计

本实训实现一个简单的均值工具。选择简单数值函数，是为了把注意力放在契约与权限，而不是复杂统计。你需要定义输入、检查、执行和失败行为，并证明模型或调用者不能通过未知参数改变功能。

均值工具接受有限数值列表，拒绝空列表、布尔值和非有限数值。它不读取文件、不访问网络、不写入外部系统。即使功能很小，也要把这些边界明确下来。

```python
import math
from bioagent.runtime import Tool, ToolRegistry, Budget


def average(values):
    return math.fsum(values) / len(values)


def validate_average(args):
    values = args["values"]
    if not isinstance(values, list) or not values:
        raise ValueError("Non-empty list required")
    if any(isinstance(x, bool) or not isinstance(x, (int, float))
           or not math.isfinite(x) for x in values):
        raise ValueError("Finite numbers required")

registry = ToolRegistry()
registry.register(Tool("average", average, validate_average))
budget = Budget(3)
print(registry.call("average", {"values": [1, 2, 3]}, budget=budget))
```

## 正常结果只是第一项验收

结果应为2，预算使用量应增加1。现在分别尝试空列表、NaN、未知参数和未知工具。输入校验失败时不应执行函数；未知工具应在注册表阶段被拒绝。

```python
bad_calls = [
    ("average", {"values": []}),
    ("average", {"values": [float("nan")]}),
    ("average", {"values": [1, 2], "hidden": True}),
    ("not_registered", {"values": [1, 2]}),
]
for name, args in bad_calls:
    try:
        registry.call(name, args, budget=budget)
    except (ValueError, TypeError) as error:
        print(type(error).__name__)
```

不要用一个宽泛的异常捕获把失败转换为0。均值为0是可能的真实结果，不能与错误混淆。调用者需要知道是否执行成功，才能作下一步决定。

## 加入审批要求

为了模拟有副作用的工具，可以给同一个函数添加审批标记。这里仍不执行任何危险动作，只观察权限逻辑。未批准时应抛出权限错误，批准后才消耗预算并执行。

```python
registry.register(Tool(
    "approved_average", average, validate_average,
    approval_required=True,
))
try:
    registry.call("approved_average", {"values": [2, 4]}, budget=budget)
except PermissionError:
    print("Approval gate works")

print(registry.call(
    "approved_average", {"values": [2, 4]},
    budget=budget, approved=True,
))
```

审批参数必须由应用控制，不应直接使用模型返回的 `approved: true`。否则模型只需在参数中声明批准，就绕过了权限边界。真实系统应将用户确认或策略批准转换为受控状态。

## 预算测试

使用预算为0的新对象调用合法工具，应该在执行前停止。使用一个有计数副作用的测试函数，可以证明没有发生实际调用。这种测试比只查看错误信息更强。

```python
from bioagent.runtime import BudgetExceeded
calls = []
def tracked(values):
    calls.append(1)
    return sum(values)
registry.register(Tool("tracked", tracked, validate_average))
try:
    registry.call("tracked", {"values": [1]}, budget=Budget(0))
except BudgetExceeded:
    pass
assert calls == []
```

这里的列表只用于测试观察。生产工具的副作用可能是文件写入、网络请求或费用，因此前置检查更重要。

## 科研迁移

把均值工具换成CLR、样本审计或专业软件适配器时，结构保持不变，但契约应更具体。例如CLR需要明确零值处理；计数聚合需要供体与细胞类型；序列工具需要数据库与输入阶段。

工具注册表并不是完整沙箱。一个已经注册的错误函数仍可能越权，因此还需要实现审查、隔离和操作系统权限。本实训证明的是应用层闸门按预期工作，不是证明所有执行风险已经消失。

## 提交与参考答案

提交工具定义、四种错误输入的测试、审批测试和预算测试。说明哪些错误发生在函数执行之前，哪些属于函数内部。

参考答案应强调：模型提出工具名，程序查注册表；参数绑定与验证先于执行；审批来源受控；失败不能伪装成正常数值；预算拒绝不能产生副作用。
