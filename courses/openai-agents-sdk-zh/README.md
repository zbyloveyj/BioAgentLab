# OpenAI Agents SDK 中文实战学院｜从零到生物科研 Agent

> **面向 Python / Jupyter 初学者的可运行课程**。先理解大模型、SDK、工具调用与智能体循环，再亲手构建 PubMed 文献检索与证据整理工作流。所有示例按教学顺序组织，中文解释配套 Python 脚本与 Notebook。

**项目位置**：BioAgentLab 仓库的独立子项目 `courses/openai-agents-sdk-zh/`，不会改动原项目的 `bioagent/`、`book/`、`examples/` 等文件。

## 先运行起来（Windows PowerShell）

```powershell
git clone https://github.com/zbyloveyj/BioAgentLab.git
cd BioAgentLab/courses/openai-agents-sdk-zh
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[notebook,dev]"
Copy-Item .env.example .env
python lessons/00_environment_check.py
pytest -q
```

如果系统提示执行策略阻止激活虚拟环境，请参考 `docs/01_环境安装.md`；也可以不激活，直接使用 `.venv\Scripts\python.exe` 执行后续命令。**以上离线检查和单元测试无需 API Key**。

在 `.env` 中填写你的 `OPENAI_API_KEY`（不要上传），然后运行：

```powershell
python lessons/01_first_agent.py
python lessons/02_function_tools.py
python -m jupyter lab
```

Jupyter Lab 启动后打开 `notebooks/00_开始之前.ipynb`，逐节运行；代码单元里使用 `await Runner.run(...)`，而独立 Python 脚本使用 `Runner.run_sync(...)` 或 `asyncio.run(...)`。

macOS / Linux：用 `python3 -m venv .venv`、`source .venv/bin/activate`、`cp .env.example .env`，其余命令相同。

## 课程导航

| 阶段 | 可运行脚本 / Notebook | 能学到什么 | 是否需要联网/API |
|---|---|---|---|
| 00 环境 | `lessons/00_environment_check.py` | Python、配置与诊断 | 不需要 |
| 01 第一个 Agent | `lessons/01_first_agent.py` | Agent、instructions、Runner | OpenAI API |
| 02 自定义工具 | `lessons/02_function_tools.py` | Python 函数工具、模型决策 | OpenAI API |
| 03 结构化输出 | `lessons/03_structured_output.py` | Pydantic、可验证数据模型 | OpenAI API |
| 04 会话记忆 | `lessons/04_session_memory.py` | SQLiteSession、多轮对话 | OpenAI API |
| 05 PubMed | `lessons/05_pubmed_search.py` | NCBI E-utilities、PMID、摘要 | NCBI + OpenAI API |
| 06 本地 RAG | `lessons/06_local_rag.py` | 先检索本地资料再回答 | OpenAI API；本地库离线可查 |
| 07 Handoff | `lessons/07_handoffs.py` | 分流到专业 Agent | OpenAI API |
| 08 Agents as tools | `lessons/08_agents_as_tools.py` | 总控 Agent 调用子 Agent | OpenAI API |
| 09 Streaming | `lessons/09_streaming.py` | 流式显示执行进度 | OpenAI API |
| 10 Guardrails | `lessons/10_guardrails.py` | 输入防护，敏感任务限制 | OpenAI API |
| 11 科研工作流 | `lessons/11_research_pipeline.py` | 检索、整理、导出 CSV/JSON | NCBI + OpenAI API |
| 12 离线研究导出 | `lessons/12_offline_research.py` | 在无密钥情况下练习可复现输出 | 不需要 |

> 建议每次运行一节，不要一开始运行全部联网脚本。Notebook 按同样顺序组织；包含解释、练习问题和对应脚本入口。

## 理解整个系统

```text
研究问题
   ↓
Agent：理解任务 / 遵守科研证据规则
   ↓
Runner：持续调用模型并执行工具请求
   ├─ 本地资料检索（无网络，教学语料）
   ├─ PubMed E-utilities（真实检索，必须设置 NCBI_EMAIL）
   ├─ 多轮会话 / 结构化输出
   └─ 子 Agent：证据梳理、表达审校
   ↓
可追踪的 JSON / CSV / 报告
```

**必须区分：** `@tool` 让 Python 函数成为 SDK 能使用的工具；并不意味着模型已经获得无限文件/网络访问。Agent 的“自主”只在你明确提供的工具范围内发生。

## 课程资源

- `notebooks/`：按节运行的交互式 Notebook（含讲解及练习）。
- `lessons/`：终端可以运行的独立 Python 脚本。
- `agent_course/`：可复用的配置、模拟数据、本地检索、PubMed 接口、报告导出。
- `docs/`：环境、概念、执行链、RAG、科研证据、费用、安全、常见错误。
- `tests/`：**不需要 API Key** 的离线单元测试。
- `outputs/`：程序运行时生成（被 Git 忽略）。
- `.github/workflows/`：该子项目内的参考 CI 工作流模板。由于这是 monorepo 的子目录，GitHub Actions 的实际生效配置仍应放在仓库根目录 `.github/workflows/`；当前只提供可移植样例，不自动修改 BioAgentLab 原来的工作流。

## 关键配置

```ini
OPENAI_API_KEY=你的密钥
OPENAI_MODEL=gpt-5-mini
NCBI_EMAIL=你本人用于NCBI检索联系的电子邮箱
# NCBI_API_KEY=可选
OPENAI_AGENTS_DISABLE_TRACING=1
```

`OPENAI_MODEL` 可按你账户可用模型更改。模型名不一定对所有账号开放。SDK 与 API 用量按实际请求计费，ChatGPT 订阅不自动包含 API 费用。保持 `OPENAI_AGENTS_DISABLE_TRACING=1` 适合初期学习，避免意外上传输入输出到追踪后端；需要调试时可自行开启。

## 如何判断自己真正学会了

学完 01 能说明 `Agent` 与 `Runner` 的分工；学完 02 能新建一个自己的 `@tool`；学完 03 知道为什么科学数据应使用结构化输出；学完 05 能提供 PMID 且区分元数据和摘要；学完 11 能把研究问题变成一个**有来源、有格式、有校验**的可复现输出过程。

## 科研数据真实性与安全

- 本地语料为**教学示例**，不是经过审查的学术证据；不要引用为疾病关联结论。
- PubMed 在线功能通过 NCBI 官方 E-utilities 拉取**实际记录**，但联网环境、文章是否含摘要、可访问性以及 API 限额会影响结果。
- `05`、`11` 明确检查 `NCBI_EMAIL`，不伪造通讯邮箱，不捏造 PMID。NCBI 默认总请求速率建议不超过每秒 3 次（无 NCBI API key）。
- LLM 的生成文本不是实验结果；**来源题名、摘要与模型解释必须分开保存**。
- 不要输入患者隐私、未公开的队列数据、密码等；在真正的科研环境中应进一步增加审批、访问控制与审计。
- `.env`、`outputs/`、`*.sqlite3` 等不进 Git；如果不慎提交密钥，请立即撤销/轮换。

## 官方参考

- 中文快速开始：https://openai.github.io/openai-agents-python/zh/quickstart/
- 工具：https://openai.github.io/openai-agents-python/zh/tools/
- 会话：https://openai.github.io/openai-agents-python/zh/sessions/
- 流式输出：https://openai.github.io/openai-agents-python/zh/streaming/
- 追踪：https://openai.github.io/openai-agents-python/zh/tracing/
- NCBI E-utilities：https://www.ncbi.nlm.nih.gov/books/NBK25499/

本教材以 2026 年 11 月核对的 Agents SDK 官方文档为依据；SDK 后续更新时，优先核对文档和本项目的 `docs/06_故障排查.md`。
