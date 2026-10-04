# BioAgentLab

BioAgentLab 是一个面向生物学、生物信息学和生物医学发现的、证据约束的 AI Agent 教学与软件项目。

## 当前版本

- 中文教材《BioAgentLab：面向生物学发现的证据型 AI Agent》
- 生成、反思、排序、进化、相似性去重、元评审与科学总控模块
- 证据声明、可证伪性检查和离线假设竞赛示例
- 以精神疾病相关肠道微生物水平基因流为贯穿案例
- 自动构建 A5 版 PDF，并检查页数、字体与文本可提取性

## 快速开始

```powershell
python -m pip install -r requirements.txt
python examples/hypothesis_tournament.py
python scripts/build_book.py
python scripts/verify_pdf.py output/pdf/BioAgentLab_中文教材.pdf
```

## 内容边界

本项目用于教学、研究设计与可复现分析。教材中的示例结果若未明确标注为真实数据分析，均不得作为生物医学结论、临床建议或实验事实引用。

## 目录

- `book/`：可版本控制的教材源稿
- `bioagent/`：Agent 核心实现
- `examples/`：无需 API Key 的离线示例
- `scripts/`：书稿与 PDF 构建、验收脚本
- `output/pdf/`：可下载 PDF 成品
- `tests/`：基础自动化测试

