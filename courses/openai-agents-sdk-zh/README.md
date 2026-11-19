# OpenAI Agents SDK 中文实战学院｜从零到生物科研 Agent

> 从 Python 零基础逐步学习智能体：配置、首次调用、工具、结构化输出、记忆、PubMed、RAG、多智能体、流式输出、护栏、科研导出。每节都有中文说明、可运行 Python 脚本、Jupyter Notebook。

本项目属于 BioAgentLab 仓库的**独立子项目**：`courses/openai-agents-sdk-zh/`，不改动原科研主工程。

## 五分钟入门（Windows PowerShell）

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

若 PowerShell 不允许激活，直接用 `.\.venv\Scripts\python.exe` 运行命令，或看 `docs/01_环境安装.md`。

**到这里无需 API Key**。然后在 `.env` 里配置自己的 `OPENAI_API_KEY`（绝不可上传到 GitHub），运行：

```powershell
python lessons/01_first_agent.py
python lessons/02_function_tools.py
python -m jupyter lab
```

先打开 `notebooks/00_开始之前.ipynb`，然后按编号学习。macOS / Linux 换成 `python3 -m venv .venv`、`source .venv/bin/activate`、`cp .env.example .env`。

## 全课程路线

| 阶段 | 文件 | 学习目标 | 外部依赖 |
|---|---|---|---|
| 00 环境 | `lessons/00_environment_check.py` | Python、配置、安装检查 | 离线 |
| 01 第一个 Agent | `lessons/01_first_agent.py` | Agent / Runner | OpenAI API |
| 02 函数工具 | `lessons/02_function_tools.py` | `@function_tool` | OpenAI API |
| 03 结构化输出 | `lessons/03_structured_output.py` | Pydantic `output_type` | OpenAI API |
| 04 会话记忆 | `lessons/04_session_memory.py` | SQLiteSession | OpenAI API |
| 05 PubMed | `lessons/05_pubmed_search.py` | ESearch / EFetch / PMID | NCBI + OpenAI API |
| 06 本地 RAG | `lessons/06_local_rag.py` | 检索增强 | OpenAI API |
| 07 交接 | `lessons/07_handoffs.py` | 专家路由 | OpenAI API |
| 08 子 Agent 工具 | `lessons/08_agents_as_tools.py` | 总控 + 专员 | OpenAI API |
| 09 流式输出 | `lessons/09_streaming.py` | 事件与增量 | OpenAI API |
| 10 输入护栏 | `lessons/10_guardrails.py` | Guardrail / tripwire | OpenAI API |
| 11 科研导出 | `lessons/11_research_pipeline.py` | 文献检索与 CSV/JSON 导出 | NCBI + OpenAI API |
| 12 离线科研练习 | `lessons/12_offline_research.py` | 没有密钥也能完成证据整理 | 离线 |

## 最重要的理解

```text
用户需求
   ↓
Agent（研究目标、任务规则、可用工具）
   ↓
Runner（与模型交互并管理工具调用循环）
   ├── 本地教学知识库查询
   ├── PubMed E-utilities 官方接口
   ├── 会话记录与结构化输出
   └── 专业子 Agent
   ↓
有来源的文献摘要与结构化结果
```

注意装饰器的官方正确写法是 `from agents import function_tool`，然后使用 `@function_tool`；不要使用其他教程里的 `from agents.decorators import tool`。

## 文件说明

- `lessons/`：每课一个可直接运行的 Python 文件
- `notebooks/`：逐章节说明、代码示例和练习；也可复制脚本代码到 Notebook
- `agent_course/`：配置、微生物教学数据、本地 RAG、PubMed 和导出
- `docs/`：概念、安装、RAG、多 Agent、隐私/费用、故障排查
- `tests/`：不需要网络或 OpenAI API 的单元测试
- `.env.example`：环境变量示例，真实 `.env` 永远不上传

## 特别说明

- `OPENAI_MODEL` 默认使用 `gpt-5-mini`，若账户不可用请改为自己有权限调用的模型。
- 在线 SDK 使用 OpenAI API，按实际请求产生费用，不属于 ChatGPT 订阅的免费额度。
- `NCBI_EMAIL` 必须填真实可联系邮箱；程序不使用假邮箱、不伪造文献 PMID。真实在线检索可能受到网络、NCBI 速率或检索命中情况的影响。
- `agent_course/data.py` 中的微生物资料明确为**教学数据**；不可当成论文、临床结论或真实 PubMed 结果。
- `OPENAI_AGENTS_DISABLE_TRACING=1` 供初学者选择关闭远程追踪，防止意外发送研究文本到追踪后端；处理真实敏感科研数据前还需要伦理审查与数据治理。

## 官方参考

- https://openai.github.io/openai-agents-python/zh/quickstart/
- https://openai.github.io/openai-agents-python/zh/tools/
- https://openai.github.io/openai-agents-python/zh/sessions/
- https://openai.github.io/openai-agents-python/zh/handoffs/
- https://www.ncbi.nlm.nih.gov/books/NBK25499/

