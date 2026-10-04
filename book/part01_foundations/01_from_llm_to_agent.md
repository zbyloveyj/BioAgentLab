# Chapter 1 — 从 LLM 到 AI Agent

## 1. 为什么会有 Agent

大语言模型最擅长的是：给定上下文，生成接下来最合适的语言序列。它可以解释概念、写代码、总结论文，也能够表现出一定程度的推理能力。

但真正的科研任务通常不是一次问答。例如：

“判断某种肠道微生物是否可能通过代谢物改变免疫细胞状态，并进一步影响神经系统表型。”

完成这个问题需要系统能够：

1. 把问题拆成可检验的子问题；
2. 搜索文献和数据库；
3. 判断哪些证据可靠；
4. 运行真实的生物信息学工具；
5. 比较多个机制假设；
6. 发现证据不足后再次搜索；
7. 记录失败过程；
8. 最终形成可复现、可验证的结论。

这就是 Agent 出现的原因。

## 2. 一个简单定义

可以把 AI Agent 粗略理解为：

~~~text
Agent =
    Model
  + State
  + Memory
  + Tools
  + Planning
  + Feedback
~~~

LLM 只是其中的一个核心组件。

Model 负责理解语言、提出方案、做决策和解释结果。

State 记录任务当前进行到哪里。

Memory 保存之前发生过什么，以及长期有价值的信息。

Tools 让 Agent 不再只能说，而是能够真正行动，例如 PubMed、Python、Scanpy、MetaPhlAn、HUMAnN、R、KEGG、UniProt 和 NCBI。

Planning 决定任务应该怎样拆解以及先做什么、后做什么。

Feedback 根据工具结果、错误、审稿意见或其他 Agent 的批评调整下一步。

## 3. Chatbot 与 Agent 的核心区别

普通 chatbot 更接近：

~~~text
User -> LLM -> Answer
~~~

Agent 更接近：

~~~text
Goal
  |
  v
Observe -> Decide -> Act -> Observe
  ^                     |
  |_____________________|
~~~

关键变化是：输出不一定是最终答案，也可能是下一步行动。

例如模型判断当前证据不足，于是下一步不是继续生成一段听起来合理的解释，而是调用文献检索工具。

## 4. 为什么 Biology 特别需要 Agent

生物医学研究有四个突出特点。

第一，知识高度分散。一个问题可能同时涉及论文、基因数据库、代谢数据库、药物数据库和实验 protocol。

第二，工具高度专业。单细胞、宏基因组、蛋白结构、GWAS 和代谢组都有完全不同的软件生态。

第三，证据质量差异巨大。体外实验、小鼠实验、横断面人群关联、纵向队列和随机对照实验不能被当作同一级别证据。

第四，科研结论必须可验证。听起来合理远远不够。一个科学假设至少需要 evidence、falsifiability、reproducibility 和 experimental feasibility。

因此 BioAgentLab 的核心思想不是让 LLM 替代生物信息学软件，而是：

**LLM 负责科研决策和工具组织，专业计算工具负责数值分析，数据库负责证据，多 Agent 负责互相质疑。**

## 5. 第一个科研 Agent Loop

~~~text
Research Question
      |
      v
Question Decomposition
      |
      v
Select Tool / Database
      |
      v
Execute
      |
      v
Inspect Evidence
      |
      +------ insufficient ------+
      |                          |
      v                          |
Generate Hypothesis              |
      |                          |
      v                          |
Reflection ----------------------+
      |
      v
Final / Next Experiment
~~~

真正的科研不是一次生成答案，而是不断提出、检验、失败、修正和再检验。

## 6. 一个重要误区：Agent 不是 Prompt 套娃

如果系统只是 Prompt A → Prompt B → Prompt C，它更像固定 workflow，不一定是强意义上的 Agent。

更成熟的 Agent 应该能够根据环境结果改变行为。例如：证据弱就继续搜索；假设冲突就启动 debate；计算失败就检查错误并重新规划；只有在证据足够时才进入综合结论。

因此，条件驱动的行动选择比固定提示词链条更重要。

## 7. Biology Agent 的可靠性原则

BioAgentLab 从第一天开始遵循五条原则：

1. Evidence-grounded：重要生物学结论必须能够追溯证据。
2. Tool-grounded：数值计算尽量交给可信的专业工具。
3. Inspectable：Agent 为什么做这个决定应该能被检查。
4. Reproducible：数据、参数、软件版本和随机种子应尽量记录。
5. Self-critical：系统必须具有主动寻找反例和失败模式的机制。

## 8. 本章小项目

请思考下面任务：

“分析一个 scRNA-seq 数据集并解释疾病相关免疫细胞变化。”

先不要立即写代码。先把它拆成 Agent 的 Goal、State、Tools、Memory、Planning 和 Feedback。

一个合理的起点是：

~~~text
Goal
  -> 数据质控
  -> 预处理
  -> 降维/聚类
  -> 细胞注释
  -> 差异分析
  -> 通路分析
  -> 证据核验
  -> 生物学解释
~~~

下一章将讨论：LLM 如何通过 Prompt、Context 与 structured state 获得任务信息。
