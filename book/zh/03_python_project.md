# 第3章 建立可以重复运行的 Python 项目

## 3.1 学 Agent 之前需要多少编程知识

你不必先成为软件工程师，但应能区分变量、函数、模块、文件和进程。更重要的是读懂一个函数的契约：它接受什么，返回什么，在什么情况下报错。科研智能体的复杂性往往来自许多简单函数之间的连接，而不是某一行特别深奥的代码。

本书的核心演示尽量使用 Python 标准库，使你可以先理解原理。涉及单细胞、统计建模和真实模型接口时，再使用独立的可选依赖。这样的安排不是认为专业库不重要，而是为了避免刚开始学习就被环境安装问题淹没。

项目的可重复性还要求区分“代码版本”和“环境版本”。同一份代码，在不同依赖版本下可能产生不同结果。版本记录也不能只写“Python 3”：至少应保存实际 Python 版本、安装包版本、操作系统以及相关外部软件版本。

## 3.2 建立隔离环境

在仓库根目录创建虚拟环境，可以减少不同项目间的依赖冲突。下面分别列出常用平台的启动方式。命令应在终端执行，而不是放进 Python 解释器。[R09]

```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

python -m pip install -e ".[dev]"
python -m pytest
```

如果 Windows 的执行策略阻止激活脚本，不必为了本项目修改整个系统的安全策略。可以直接使用虚拟环境中的解释器，例如 `.venv\Scripts\python.exe -m pip install -e .`。关键是确认后续命令使用的是同一个解释器。

`-e` 表示可编辑安装，修改源文件后不必反复重新安装项目。`.[dev]` 表示同时安装开发所需的可选依赖。生产运行环境不一定需要测试和排版工具，应把不同用途的依赖分开。

## 3.3 路径不是一个随意拼接的字符串

一个常见错误是让程序依赖当前工作目录。你在仓库根目录运行成功，换到 notebook 目录就找不到数据。另一个错误是直接信任模型生成的文件路径，从而意外读写工作目录之外的文件。

`pathlib` 提供了清晰的路径操作方式。下面的函数要求目标位于指定根目录内；它是一项防护，不是完整沙箱。真实多用户服务还需要操作系统级权限隔离。

```python
from pathlib import Path


def inside_root(root: Path, relative: str) -> Path:
    root = root.resolve()
    target = (root / relative).resolve()
    if target != root and root not in target.parents:
        raise ValueError("Path escapes workspace")
    return target


workspace = Path("runs/demo")
output = inside_root(workspace, "report.json")
output.parent.mkdir(parents=True, exist_ok=True)
```

这里使用 `resolve()` 是为了规范化路径，并处理符号链接带来的部分问题。需要注意，检查后到打开文件前仍可能存在竞争条件；高风险环境不能只靠这几行代码保障隔离。教学程序应明确自己的保护范围。

## 3.4 用数据类定义研究对象

科研系统不应把所有东西都放进一大段字符串。假设、证据、任务和输出文件具有不同字段。使用数据类可以让这些字段显式化，并减少手工维护构造函数的负担。类型注解主要帮助阅读与静态分析，不会自动执行完整的运行时校验。[R09]

```python
from dataclasses import dataclass, field

@dataclass
class ResearchTask:
    task_id: str
    question: str
    required_evidence: list[str] = field(
        default_factory=list
    )
    status: str = "pending"

    def __post_init__(self):
        if not self.task_id.strip():
            raise ValueError("Missing task id")
        if not self.question.strip():
            raise ValueError("Missing question")
```

为什么不能把列表直接写成共享默认值？因为不同任务应该拥有不同的证据列表。`default_factory=list` 表示每次实例化都新建一个列表。这类细节看起来与 AI 无关，却可能决定多个任务是否在无意间污染彼此的数据。

## 3.5 错误要成为信息

不要用一个宽泛的 `except Exception: pass` 把错误吞掉。这样做会让系统继续生成报告，甚至声称任务已经完成。应该区分输入错误、临时网络错误、权限错误和分析方法错误。

输入错误通常应停止并提示修正；临时网络错误可以有限重试；权限错误不应通过不断换路径绕过；分析错误则可能要求重新检查数据假设，而不是简单重复运行。错误类别会影响下一步行动，因此它属于 Agent 状态的一部分。

下面是一种适合教学项目的结构化返回方式。`ok=False` 不应与空结果混为一谈。

```python
result = {
    "ok": False,
    "error_type": "invalid_input",
    "message": "Duplicate sample identifiers",
    "retryable": False,
    "artifacts": [],
}
```

## 3.6 从 notebook 走向模块

Notebook 适合探索和教学，但隐藏执行顺序容易造成“本机能跑，别人不能跑”。例如某个变量由几小时前执行的单元格创建，当前 notebook 中却没有对应代码。正式交付前，应从空内核自上而下运行全部单元格。

可复用函数应放到 Python 模块中，notebook 负责调用、展示和解释。这样同一套逻辑既能在命令行运行，也能在测试中验证。不要在 notebook 中复制多个略有不同的统计函数，否则很难知道报告究竟来自哪一个版本。

本书配套 notebook 不保存 API 密钥，也不默认调用收费服务。需要联网的单元格明确标注；离线单元格可在无网络条件下运行。对于真实数据，notebook 中应使用相对路径或配置项，不应包含个人电脑的绝对路径。

## 3.7 第一个可重复产物

一个分析任务至少应生成结果、配置和环境三种记录。结果告诉你算出了什么，配置告诉你选择了哪些参数，环境告诉你使用什么软件。再加上输入文件的摘要哈希，可以判断两次运行是否真的使用相同材料。

```python
import hashlib
import json
import platform
from pathlib import Path

path = Path("data/example.csv")
if path.exists():
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
else:
    digest = None

manifest = {
    "python": platform.python_version(),
    "input_sha256": digest,
    "mode": "synthetic_demo",
    "seed": 42,
}
Path("manifest.json").write_text(
    json.dumps(manifest, indent=2), encoding="utf-8"
)
```

哈希不是数据质量保证，也不是访问权限控制。它只回答“字节内容是否相同”这一类问题。真实项目应避免把敏感路径、受试者标识或密钥写入公共清单。

## 3.8 练习与参考思路

**练习一：**把一个依赖 notebook 全局变量的函数改写为纯函数。参考思路是把所有输入作为参数，把结果作为返回值，不在函数内部依赖隐藏的单元格状态。

**练习二：**运行日志出现“文件不存在”，下一步应重新询问模型还是检查文件路径？参考思路是先用确定性检查确认路径与权限，只有问题需要解释或重新规划时再调用模型。语言模型不是文件系统的替代品。

**本章要点：**环境隔离、明确路径、数据契约和结构化错误，是科研 Agent 能够可靠运行的基础设施。
