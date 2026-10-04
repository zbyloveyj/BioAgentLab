# BioAgentLab

## AI Agent for Biology：生物科研智能体原理与实践

一套面向生物学与生物信息学研究者的 **中文教材 + PDF + Python教学项目 + Notebook + 自动测试**。贯穿案例是 **微生物—代谢物—宿主单细胞**。

**[阅读教材目录](book/README.md) · [下载中文PDF](docs/pdf/AI_Agent_for_Biology_ZH.pdf) · [Notebook课程](notebooks/README.md) · [功能边界](docs/CAPABILITIES.md) · [构建与测试记录](docs/verification.json)**

教材包含 **32章正文、10项实训、术语与接口速查、故障排查和24项参考资料**。PDF采用A5单栏、中文衬线正文、镜像页边距、页眉页码、公式与可点击目录。实际页数和SHA-256见 [PDF构建记录](docs/pdf/AI_Agent_for_Biology_ZH.build.json)。构建流程要求不少于200页，不自动插空页。

## 从哪里开始

先读[第1章](book/zh/01_agent_foundations.md)，再运行下面的离线例子。每章包含解释、例子、常见错误和练习；十项实训将概念接成完整工作流。

```bash
git clone https://github.com/zbyloveyj/BioAgentLab.git
cd BioAgentLab
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest -q
python -m bioagent demo --out runs/micrometacell
```

**默认演示不联网、不需要API key，只使用合成数据与脚本模型。** 输出为 `report.json`、`report.md`、`trace.jsonl` 和 `manifest.json`。同名输出目录默认不会被覆盖。

## 学习路径

| 部分 | 内容 |
|---|---|
| 第1—8章 | Agent、LLM、Python、任务契约、状态、工具、规划与运行时 |
| 第9—12章 | RAG、证据台账、知识图谱、行动发现与MCP |
| 第13—19章 | 假设生成、反思、辩论、Elo、修订、去重、调度与评估 |
| 第20—28章 | 文献、宏基因组、生态、代谢组、单细胞、多组学、因果与安全 |
| 第29—32章 | 模型接入、综合项目、Benchmark、报告与发布 |
| 十项实训 | 工具权限、检索、证据、角色、排序、数值、供体聚合、失败和报告审计 |

## 本版实际实现

Python标准库核心包括：工具注册与预算、DAG检查、运行日志、本地BM25、双语相近性、来源和情境感知的证据聚合、版本化候选、JSON契约的生成/反思/修订、受引用约束的成对辩论接口与顺序复评、Elo、CLR、BH校正、供体pseudobulk、样本对齐，以及MicroMetaCell离线综合演示。

可选接口包括 **PubMed只读检索/记录解析** 和 **OpenAI Responses文本适配**。联网必须显式选择；本版不把离线解析测试当成真实服务端到端验证。供应商密钥不进入仓库。

**重要区别：**综合演示中的排序使用透明的合成注释启发式，不冒充真实LLM科学辩论；`bioagent/debate.py`是独立可接模型的辩论接口。证据台账聚合已提供注释，不自动证明原文支持与科学因果。

## 仓库结构

```text
book/zh/          完整中文正文、实训、附录与参考资料
bioagent/         教学模块与可选网络适配
notebooks/        八个可独立执行的离线Notebook
examples/         入门示例
workflows/        工作流说明
tests/            数值、契约、边界和端到端测试
benchmark/        评价说明
scripts/          教材、Notebook与发布包构建
 docs/pdf/        PDF及实际构建记录
```

## 重新构建教材

需要Pandoc、XeLaTeX/ctex及Noto CJK、Liberation、DejaVu系统字体。Linux示例与完整过程见[构建说明](docs/BUILD.md)。字体文件不打包进仓库。

```bash
python -m pip install -e ".[dev,book,notebooks]"
python scripts/build_notebooks.py --execute
python scripts/build_book.py --min-pages 200
python scripts/verify_release.py
python scripts/package_release.py
```

## 科学与使用边界

本仓库是可运行的学习项目，**不是经过独立真实队列验证的自主发现平台**。它不提供完整宏基因组生产流水线、正式单细胞差异表达、自动湿实验或临床诊断。真实数据接入需要另行核验方法、隐私、权限、工具与结论。

教材介绍Biomni、AI co-scientist、GeneAgent和DeepRare时区分论文版本与本项目实现，不声称复制其性能。所有关键概念强调：执行成功、分析适当与结论成立是三个不同层次。

## 许可

项目拥有者尚未选择统一开源许可证。公开可读不等于已经授予任意再使用许可。第三方论文、软件和数据遵循各自条件。
