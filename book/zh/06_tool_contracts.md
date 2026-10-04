# 第6章 工具调用：让模型行动，但不让它越界

## 6.1 工具调用分为两次决定

当模型提出 `search_pubmed(query=...)` 时，它只是在建议调用某个工具。真正是否执行，应由应用程序决定。程序需要确认工具存在、参数有效、权限满足、预算允许，然后才将请求交给工具。

这个区别非常重要。模型输出的函数名不应直接变成 Python 的 `eval()` 或 shell 命令。否则一个语法错误可能变成执行错误，一段恶意材料也可能被转化为越权操作。工具注册表相当于一份允许执行的能力清单。

不同模型供应商提供不同形式的工具调用接口，但核心过程相似：给出工具描述与参数结构，接收模型提出的调用，执行经过检查的工具，再把结果返回模型。[R20,R21]

## 6.2 一个好的工具契约

工具描述不只是“这个函数做什么”。还应说明输入单位、实体类型、返回格式、失败条件和副作用。例如，`metabolite_lookup` 应明确输入是名称还是稳定标识，返回的是同义词、化学结构还是生物反应关系。

对分析工具，尤其要说明输入处于什么阶段。一个需要原始计数的函数，不能接受已经对数转换的表达矩阵。模型很容易因为文件名里出现 `expression` 就认为可以使用；契约应把这种隐含知识显式化。

下面给出教学用工具规范。它是应用层的数据结构，不代表某个特定供应商的 API。

```python
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    required_args: tuple[str, ...]
    read_only: bool
    needs_approval: bool
    handler: Callable
```

`read_only` 与 `needs_approval` 不能代替实际权限控制。它们帮助程序作决定，但工具实现仍可能存在错误。真实执行环境应按最小权限原则配置。[R11]

## 6.3 输入校验要在执行之前

假设工具需要 `sample_id`、`method` 和 `input_path`。应拒绝缺失字段、未知方法、越界路径以及不符合数据要求的输入。不要期待工具运行后才发现错误，也不要让模型通过反复尝试参数“撞出”一个能运行的组合。

```python
TOOLS = {}


def register(spec):
    if spec.name in TOOLS:
        raise ValueError("Duplicate tool name")
    TOOLS[spec.name] = spec


def execute(name, arguments, approved=False):
    if name not in TOOLS:
        raise ValueError("Tool is not registered")
    spec = TOOLS[name]
    missing = set(spec.required_args) - set(arguments)
    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")
    if spec.needs_approval and not approved:
        raise PermissionError("Approval required")
    return spec.handler(**arguments)
```

这个简化示例还需要类型、取值范围和未知参数检查。对高成本任务，应在启动前估计输入规模；对写入任务，应记录目标位置和预期副作用。未知字段不应被静默丢弃，否则模型可能误以为它们已经生效。

## 6.4 输出同样需要校验

工具退出码为零，不一定表示科学结果有效。输出文件可能为空，样本数可能减少，列名可能变化，统计结果可能全部为缺失。每个工具都应有完成条件。

以丰度转换为例，输出应具有与输入一致的样本标识，数值有限，矩阵维度符合预期。以检索工具为例，空列表可以是正常结果，但网络错误不能伪装为空列表。以模型拟合为例，还需要检查收敛状态和数据假设。

一个统一的输出信封可以包含 `ok`、`data`、`artifacts`、`warnings`、`error` 和 `provenance`。这样 Supervisor 不必从一段随意的字符串里猜测执行是否成功。

## 6.5 不要让模型随意生成 shell

生物信息学软件常通过命令行运行，但这不意味着应该直接执行模型生成的一整条命令字符串。更稳妥的是用固定命令模板和参数列表，关闭 shell 解释，并限制可执行文件与工作目录。

```python
import subprocess


def run_version(executable: str):
    allowed = {"python", "python3"}
    if executable not in allowed:
        raise PermissionError("Executable not allowed")
    return subprocess.run(
        [executable, "--version"],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
        shell=False,
    ).stdout.strip()
```

即使使用 `shell=False`，被调用程序本身仍可能读写文件或访问网络。安全边界最终应由隔离环境、文件权限和网络策略共同提供，而不是依靠一个参数。

## 6.6 超时、重试与预算

工具可能卡住，因此应设置超时。临时服务错误可以重试，但应设置最大次数和退避间隔。输入无效、认证失败或权限不足通常不应自动重复。重试之前，应考虑操作是否幂等。

预算不仅是 token 数，还包括调用次数、计算时间、磁盘空间和外部服务费用。一个简单工具被循环调用几百次，也可能使任务失控。Supervisor 应在每次执行前检查剩余预算，而不是等任务结束才统计费用。

对远程模型服务，还要记录供应商返回的使用量与本地估计之间的区别。估计值可以帮助预警，但最终费用应以服务记录为准，不应在教材中写死可能变化的价格。

## 6.7 工具发现不等于工具授权

当系统发现一个新数据库或软件，它获得的是候选能力，不是自动执行权限。新工具应先经过来源检查、契约审查、测试和权限配置，再进入注册表。这个过程类似实验室引入新仪器：知道仪器存在，与让它直接控制研究流程之间，还隔着一套验证程序。

工具描述也可能误导模型。一个名字很像“分析完整通路”的函数，实际可能只做字符串检索。评估工具选择时，应检查工具能力与任务需求是否匹配，而不是只检查名称相关性。

## 6.8 练习与参考思路

**练习一：**工具返回 `[]`，但实际上因为网络超时而失败，为什么危险？参考思路：后续 Agent 可能把基础设施故障解释为“没有相关研究”，使错误进入科学结论。

**练习二：**模型提出删除旧结果目录以节省空间。参考思路：删除是有副作用的动作，应明确范围、检查是否存在未备份产物并要求批准；不能因为模型说“这是临时文件”就直接执行。

**本章要点：**模型提议行动，应用程序授权执行；输入、输出、权限与预算都属于工具契约。
