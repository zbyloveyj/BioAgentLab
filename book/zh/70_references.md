# 参考资料与继续阅读

正文使用R编号定位资料。本表优先列原始论文、作者资源与官方文档；接口资料访问核验日期为2026年10月4日。预印本明确指向本书讨论的版本，不据此断言该工作之后没有更新。论文中的系统性能不等于本教材代码的性能。

## 模型、检索与科学智能体

**[R01]** Vaswani A, Shazeer N, Parmar N, et al. Attention Is All You Need. 2017. arXiv:1706.03762. 原始论文入口：<https://arxiv.org/abs/1706.03762>。用于理解Transformer与注意力机制。

**[R02]** Yao S, Zhao J, Yu D, et al. ReAct: Synergizing Reasoning and Acting in Language Models. ICLR, 2023；arXiv:2210.03629，v3. <https://arxiv.org/abs/2210.03629>。用于理解推理、行动与观察交替的控制方式。

**[R03]** Lewis P, Perez E, Piktus A, et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. 2020. arXiv:2005.11401. <https://arxiv.org/abs/2005.11401>。本书据此介绍外部检索与生成的结合，不将检索相似度解释成证据可靠度。

**[R04]** Shinn N, Cassano F, Berman E, et al. Reflexion: Language Agents with Verbal Reinforcement Learning. 2023. arXiv:2303.11366，v4. <https://arxiv.org/abs/2303.11366>。讨论语言反馈与情节记忆，不等同于更新模型权重。

**[R05]** Gottweis J, Weng W H, Daryin A, et al. Towards an AI co-scientist. 2025. arXiv:2502.18864. <https://arxiv.org/abs/2502.18864>。本书讨论2025年预印本中的生成、辩论、进化与资源组织思路。

**[R06]** Huang K, Zhang S, Wang H, et al. Biomni: A General-Purpose Biomedical AI Agent. bioRxiv, 2025-06-02，v1. DOI:10.1101/2025.05.30.656746. <https://www.biorxiv.org/content/10.1101/2025.05.30.656746v1>。本书讨论该预印本版本的行动空间发现与工具组织。

**[R07]** Wang Z, Jin Q, Wei C H, et al. GeneAgent: self-verification language agent for gene-set analysis using domain databases. Nature Methods, 2025, 22:1677–1685. DOI:10.1038/s41592-025-02748-6. <https://www.nature.com/articles/s41592-025-02748-6>。已同行评议；用于理解claim拆分与领域数据库核验。

**[R08]** Zhao W, Wu C, Fan Y, et al. An agentic system for rare disease diagnosis with traceable reasoning. Nature, 2026, 651:775–784. DOI:10.1038/s41586-025-10097-9. <https://www.nature.com/articles/s41586-025-10097-9>。2026年2月18日在线发表，已同行评议；本书仅讨论证据追踪与系统组织，不提供临床诊断功能。

## 编程、接口与运行环境

**[R09]** Python Software Foundation. Python documentation: dataclasses, venv and the standard library. 官方文档。<https://docs.python.org/3/library/dataclasses.html>；<https://docs.python.org/3/library/venv.html>。使用时核对本地Python版本。

**[R10]** National Center for Biotechnology Information. Entrez Programming Utilities Help: A General Introduction to the E-utilities. 官方文档。<https://www.ncbi.nlm.nih.gov/books/NBK25497/>。用于请求格式、工具标识与限速要求。摘要与全文的使用仍受来源版权和条件约束。

**[R11]** Model Context Protocol. Specification: Server Tools，2025-06-18版本；官方工具注解说明。<https://modelcontextprotocol.io/specification/2025-06-18/server/tools>；<https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/>。协议与注解不替代客户端权限控制。

**[R12]** Scanpy developers. Scanpy tutorials and clustering workflow. 官方文档。<https://scanpy.readthedocs.io/en/stable/tutorials/index.html>；<https://scanpy.readthedocs.io/en/latest/tutorials/basics/clustering.html>。用于AnnData、预处理与单细胞工作流接口，具体参数依研究条件确定。

**[R17]** scikit-learn developers. Common pitfalls and recommended practices. 官方文档。<https://scikit-learn.org/stable/common_pitfalls.html>。用于预处理一致性、训练验证分离与数据泄漏检查。

**[R18]** Nextflow developers / Seqera. Caching and resuming. 官方文档。<https://docs.seqera.io/nextflow/cache-and-resume>。用于理解科学工作流缓存、恢复与任务身份。

**[R19]** GitHub. Store and share data with workflow artifacts. 官方文档。<https://docs.github.com/en/actions/tutorials/store-and-share-data>。构建产物的保留期限与仓库文件是不同概念。

**[R20]** OpenAI. Function calling and Responses API documentation. 官方文档。<https://developers.openai.com/api/docs/guides/function-calling>；<https://developers.openai.com/api/reference/resources/responses/methods/create>。模型和接口能力可能变化；本项目不硬编码一个长期有效的模型名称。

**[R21]** Anthropic. Tool use overview. 官方文档。<https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview>。用于比较工具调用接口思想，不表示本版实现了所有供应商适配。

## 生物统计、测量与复现

**[R13]** Squair J W, Gautier M, Kathe C, et al. Confronting false discoveries in single-cell differential expression. Nature Communications, 2021, 12:5692. DOI:10.1038/s41467-021-25960-2. <https://www.nature.com/articles/s41467-021-25960-2>。用于供体层级推断与伪重复问题。

**[R14]** Beghini F, McIver L J, Blanco-Míguez A, et al. Integrating taxonomic, functional, and strain-level profiling of diverse microbial communities with bioBakery 3. eLife, 2021, 10:e65088. DOI:10.7554/eLife.65088. <https://elifesciences.org/articles/65088>。用于区分分类、功能与菌株分析层级。

**[R15]** Silverman J D, Washburne A D, Mukherjee S, David L A. A phylogenetic transform enhances analysis of compositional microbiota data. eLife, 2017, 6:e21887. DOI:10.7554/eLife.21887. <https://elifesciences.org/articles/21887>。用于理解微生物组成数据与对数比分析。

**[R16]** Benjamini Y, Hochberg Y. Controlling the False Discovery Rate: A Practical and Powerful Approach to Multiple Testing. Journal of the Royal Statistical Society: Series B, 1995, 57(1):289–300. DOI:10.1111/j.2517-6161.1995.tb02031.x. <https://doi.org/10.1111/j.2517-6161.1995.tb02031.x>。错误控制有相应条件，不能修复无效的原始检验。

**[R22]** Wilkinson M D, Dumontier M, Aalbersberg I J, et al. The FAIR Guiding Principles for scientific data management and stewardship. Scientific Data, 2016, 3:160018. DOI:10.1038/sdata.2016.18. <https://www.nature.com/articles/sdata.2016.18>。用于数据、代码和工作流的可复用性管理。

**[R23]** Hernán M A, Robins J M. Causal Inference: What If. 作者维护的教材页面：<https://miguelhernan.org/whatifbook>。用于进一步学习因果图、混杂、选择偏差与识别假设；本书第27章的教学说明不能替代具体研究的统计审查。

**[R24]** Sumner L W, Amberg A, Barrett D, et al. Proposed minimum reporting standards for chemical analysis. Metabolomics, 2007, 3:211–221. DOI:10.1007/s11306-007-0082-2. <https://link.springer.com/article/10.1007/s11306-007-0082-2>。用于理解代谢物鉴定与报告等级。

## 阅读顺序建议

先读R02、R03和R04建立行动、检索与反馈概念，再读R05—R08比较科研系统的任务和验证边界。进入真实生物数据之前，结合R13—R16和R24检查测量、独立单位与多重检验。部署前核对R09—R12与R17—R21的实际版本。

不要把参考资料数量当作证据强度。每个具体研究结论仍需要与其直接对应的原始证据，不能用本表中的方法论文为一个未验证的生物机制背书。
