# 实训一 从空环境到第一份可追溯报告

## 目标与准备

本实训要求你完成一次离线运行，并证明报告来自当前代码，而不是复制来的示例文本。需要Python 3.10或更高版本、仓库源码和终端。第一次安装开发依赖可能需要网络；核心演示本身不调用外部服务。

先确认当前目录包含 `pyproject.toml` 与 `bioagent/`。不要在下载压缩包后直接进入某个子目录运行全部命令，否则可能使用错误路径。保存本次运行使用的源码版本；通过Git获得源码时，可以记录提交标识。

```bash
python --version
python -m venv .venv
# 按第3章说明激活当前平台的虚拟环境
python -m pip install -e ".[dev]"
python -m pytest -q
python -m bioagent demo --out runs/lab01
```

## 先检查产物，不急着读结论

运行后查看 `report.json`、`report.md`、`trace.jsonl` 和 `manifest.json`。JSON用于程序检查，Markdown用于阅读，JSONL记录事件，manifest用于核对产物摘要。四个文件的职责不同。

打开报告，确认模式为 `synthetic_offline_teaching`，并且真实生物学验证字段为false。这个检查不是形式要求：如果一个教学系统丢失了模拟标记，读者很容易把后面的分值与机制描述当成研究结果。

```python
import json
from pathlib import Path

root = Path("runs/lab01")
report = json.loads((root / "report.json").read_text(encoding="utf-8"))
assert report["mode"] == "synthetic_offline_teaching"
assert report["real_biological_validation"] is False
print(report["stop_reason"])
print(report["completed_steps"])
```

## 检查报告与日志是否一致

事件日志应从开始记录到报告生成，中间包含工具和检索动作。报告中的完成步骤应该能够在日志或对应产物中找到依据。不能因为报告列出了某个模块名称，就假设它已经执行。

```python
rows = [json.loads(line) for line in
        (root / "trace.jsonl").read_text(encoding="utf-8").splitlines()]
assert rows[0]["action"] == "start"
assert rows[-1]["action"] == "report"
assert [r["sequence"] for r in rows] == list(range(1, len(rows) + 1))
for row in rows:
    print(row["sequence"], row["action"])
```

这里验证的是事件顺序，不是事件内容一定科学正确。若某条记录说工具成功，仍需检查工具输出验收。可追溯性让核验成为可能，但不代替核验。

## 验证哈希

修改报告中的一个字符，再执行摘要核对，应该发现不一致。这个实验说明哈希能够检测字节变化。它不能告诉你变化是否合理，也不能证明原报告正确。

```python
import hashlib
manifest = json.loads((root / "manifest.json").read_text())
for name, expected in manifest["files"].items():
    actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
    print(name, actual == expected)
```

完成实验后重新运行到新的目录，不要手工修改manifest来掩盖变化。研究产物需要修订时，应创建新版本并说明原因。

## 故意触发覆盖保护

再次运行同一输出目录，默认应拒绝覆盖。这避免你在不知情时替换旧结果。明确需要重跑时，可以选择新目录，或使用 `--overwrite`；后者只适合你确认可以替换的教学产物。

```bash
python -m bioagent demo --out runs/lab01
python -m bioagent demo --out runs/lab01_repeat
```

观察两次运行的结构化科学结果是否一致。时间戳和相应日志哈希可能不同，这是预期行为，不表示计算不稳定。比较时应区分内容结果与运行元数据。

## 提交与参考答案

提交一段说明：使用的Python与源码版本、测试是否完成、四类产物的作用，以及为什么报告不能当成真实机制结论。附上一个被覆盖保护正确拒绝的终端记录。

参考答案应指出：示例使用合成输入和脚本模型；台账只聚合已提供注释；最终真实证据不足；哈希保证内容对应而不保证科学真值。只截图一个成功提示，不足以完成实训。

扩展任务是把输出目录改到另一个位置，并确认路径变化不会改变核心结果。不要在这一步接入真实患者或组学数据，先把工程闭环理解清楚。
