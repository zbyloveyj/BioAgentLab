from __future__ import annotations

import os
import textwrap
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf"
BOOK = ROOT / "book"
PDF_PATH = OUT / "BioAgentLab_中文教材.pdf"
MD_PATH = BOOK / "BioAgentLab_中文教材.md"


CHAPTERS = [
    ("第一篇 基础", "从 LLM 到科学 Agent", [
        "语言模型不是事实数据库", "Agent 的感知—推理—行动闭环", "科学任务与通用聊天的差异",
        "状态、动作和环境反馈", "工具调用与权限边界", "结构化输出与数据契约",
        "失败为何必须可见", "成本、延迟与信息增益", "最小可用科学 Agent",
    ]),
    ("第一篇 基础", "生物学问题的可计算表达", [
        "从宽泛主题到研究问题", "PICO、PECO 与机制问题", "观察单位与分析单位",
        "暴露、结局和混杂变量", "因果图与替代解释", "把机制写成可证伪预测",
        "阴性对照和阳性对照", "数据可得性审计", "预注册式任务说明书",
    ]),
    ("第二篇 架构", "Generation：构建假设空间", [
        "为何需要多候选而非单答案", "机制家族与竞争性假设", "形态学搜索与概念组合",
        "约束条件下的发散", "先验知识与新颖性的张力", "把反例一并生成",
        "生成结果的模式坍缩", "温度不是多样性的全部", "假设卡片模板",
    ]),
    ("第二篇 架构", "Reflection 与 Evidence Verification", [
        "自我批评不能等同于核验", "声明拆分与原子化", "来源、证据和结论的映射",
        "支持证据与反对证据", "相关、预测与机制的等级", "引用存在不等于引用支持",
        "时间、物种和实验体系的外推", "证据冲突的保留", "可审计反思记录",
    ]),
    ("第二篇 架构", "Ranking、Evolution 与 Proximity", [
        "评分量表的可操作定义", "成对比较与绝对评分", "Elo 与 Bradley–Terry 直觉",
        "避免评审者位置偏差", "从批评生成后代假设", "探索—利用平衡",
        "语义相似不等于科学等价", "机制去重与谱系记录", "停止条件与帕累托前沿",
    ]),
    ("第三篇 证据", "RAG：让检索服务于论证", [
        "问题分解与检索计划", "关键词、主题词与引用网络", "文献去重和版本识别",
        "摘要不能替代全文", "段落级证据定位", "Claim–Evidence Graph",
        "检索召回率与精确率", "反证优先检索", "可复现检索日志",
    ]),
    ("第三篇 证据", "工具、记忆与行动发现", [
        "工具描述就是行为边界", "只读、可逆与不可逆动作", "短期工作记忆",
        "长期记忆的污染风险", "研究对象与任务状态分离", "从失败中发现新动作",
        "工具选择的效用模型", "权限升级和人工审批", "可重放行动轨迹",
    ]),
    ("第四篇 科学方法", "统计、因果与可复现性", [
        "效应量先于 P 值", "多重比较与发现率", "交叉验证的泄漏陷阱",
        "批次效应与站点效应", "缺失数据与选择偏倚", "敏感性分析与稳健性",
        "因果估计的识别假设", "外部验证与可迁移性", "计算环境和数据谱系",
    ]),
    ("第四篇 科学方法", "多智能体科学辩论", [
        "角色多样性不等于人格扮演", "支持方、反方和方法评审", "证据共享与信息隔离",
        "轮次设计和发言预算", "何时共识是危险信号", "少数意见的保存",
        "元评审与仲裁", "辩论评估指标", "人类专家的最终责任",
    ]),
    ("第五篇 生物学工作流", "微生物组 Agent", [
        "组成型数据的约束", "测序深度与检测概率", "物种、菌株和功能层级",
        "共现网络的解释边界", "宏基因组装配质量", "功能注释的不确定性",
        "跨队列 meta-analysis", "阴性对照与伪关联", "从差异丰度到机制候选",
    ]),
    ("第五篇 生物学工作流", "单细胞与多组学 Agent", [
        "细胞质控和双细胞", "归一化与批次整合", "细胞类型注释的证据层级",
        "差异表达与伪重复", "轨迹不是时间", "配体—受体推断",
        "多组学因子模型", "空间信息与组织结构", "跨模态结论的闭环验证",
    ]),
    ("第六篇 多智能体发现", "Scientific Supervisor", [
        "任务图和依赖关系", "预算、并发与终止规则", "生成者和评审者隔离",
        "失败恢复与降级路径", "工具输出的模式校验", "审计日志与可追溯性",
        "风险分级与人工门", "基准任务和回归测试", "从原型到可靠系统",
    ]),
    ("第七篇 综合实战", "全球生态机会与 HGT 背景", [
        "研究故事与竞争解释", "Global Ecological Opportunity Network", "跨研究共现与比例性",
        "功能生态组织图谱", "GutMetaNet 参考网络", "常见交换与异常交换",
        "生态机会的必要非充分性", "数据字典与统一标识", "发现集和验证集的冻结",
    ]),
    ("第七篇 综合实战", "机会校正的遗传流网络", [
        "WAAFLE 事件图谱", "断点级验证策略", "Expected HGT 模型",
        "Opportunity-adjusted Propensity", "丰度和测序质量校正", "有向 source–sink 网络",
        "HGT hub 与 genetic broker", "边重连和模块变化", "负对照与置换检验",
    ]),
    ("第七篇 综合实战", "功能迁移、临床耦合与证据收敛", [
        "donor–cargo–recipient 三元组", "Functional Relocation", "功能来源分解",
        "跨疾病共享与特异成分", "Genetic Remodeling Modules", "菌株与泛基因组验证",
        "适应性选择证据", "HAMD、MCCB 与脑影像", "Adaptive Transfer Units",
    ]),
]


REFERENCES = [
    "Lewis P, Perez D, Piktus A, et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS, 2020.",
    "Yao S, Zhao J, Yu D, et al. ReAct: Synergizing Reasoning and Acting in Language Models. ICLR, 2023.",
    "Shinn N, Cassano F, Gopinath A, et al. Reflexion: Language Agents with Verbal Reinforcement Learning. NeurIPS, 2023.",
    "Liu P, Yuan W, Fu J, et al. Pre-train, Prompt, and Predict: A Systematic Survey of Prompting Methods in NLP. ACM Computing Surveys, 2023.",
    "Wilkinson MD, Dumontier M, Aalbersberg IJJ, et al. The FAIR Guiding Principles for scientific data management. Scientific Data, 2016.",
    "Peng RD. Reproducible Research in Computational Science. Science, 2011.",
    "Quinn TP, Erb I, Richardson MF, Crowley TM. Understanding sequencing data as compositions. Bioinformatics, 2018.",
    "Gloor GB, Macklaim JM, Pawlowsky-Glahn V, Egozcue JJ. Microbiome datasets are compositional. Frontiers in Microbiology, 2017.",
    "Hawinkel S, Mattiello F, Bijnens L, Thas O. A broken promise: microbiome differential abundance methods. Briefings in Bioinformatics, 2019.",
    "Luecken MD, Theis FJ. Current best practices in single-cell RNA-seq analysis. Molecular Systems Biology, 2019.",
    "Squair JW, Gautier M, Kathe C, et al. Confronting false discoveries in single-cell differential expression. Nature Communications, 2021.",
    "Szklarczyk D, Kirsch R, Koutrouli M, et al. The STRING database in 2023. Nucleic Acids Research, 2023.",
    "Beghini F, McIver LJ, Blanco-Míguez A, et al. Integrating taxonomic, functional, and strain-level profiling of diverse microbial communities. eLife, 2021.",
    "Franzosa EA, Sirota-Madi A, Avila-Pacheco J, et al. Gut microbiome structure and metabolic activity in inflammatory bowel disease. Nature Microbiology, 2019.",
    "Gelman A, Carlin JB. Beyond Power Calculations: Assessing Type S and Type M Errors. Perspectives on Psychological Science, 2014.",
    "Wasserstein RL, Lazar NA. The ASA Statement on p-Values. The American Statistician, 2016.",
    "Pearl J. Causality: Models, Reasoning, and Inference. Cambridge University Press, 2009.",
    "Hernán MA, Robins JM. Causal Inference: What If. Chapman & Hall/CRC, 2020.",
]


def register_fonts() -> tuple[str, str, str]:
    candidates = [
        (r"C:\Windows\Fonts\NotoSerifSC-VF.ttf", r"C:\Windows\Fonts\NotoSansSC-VF.ttf"),
        (r"C:\Windows\Fonts\simsun.ttc", r"C:\Windows\Fonts\msyh.ttc"),
    ]
    for serif, sans in candidates:
        if os.path.exists(serif) and os.path.exists(sans):
            pdfmetrics.registerFont(TTFont("BookSerif", serif, subfontIndex=0))
            pdfmetrics.registerFont(TTFont("BookSans", sans, subfontIndex=0))
            break
    else:
        raise FileNotFoundError("No Chinese font found")
    mono = r"C:\Windows\Fonts\consola.ttf"
    pdfmetrics.registerFont(TTFont("BookMono", mono))
    return "BookSerif", "BookSans", "BookMono"


def styles():
    serif, sans, mono = register_fonts()
    base = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle("cover", parent=base["Title"], fontName=sans, fontSize=25, leading=35, alignment=TA_CENTER, textColor=colors.HexColor("#143D59"), spaceAfter=10*mm),
        "subtitle": ParagraphStyle("subtitle", fontName=serif, fontSize=12, leading=20, alignment=TA_CENTER, textColor=colors.HexColor("#456268")),
        "part": ParagraphStyle("part", fontName=sans, fontSize=12, leading=17, textColor=colors.HexColor("#E07A5F"), spaceAfter=4*mm),
        "chapter": ParagraphStyle("chapter", fontName=sans, fontSize=21, leading=29, textColor=colors.HexColor("#143D59"), spaceAfter=8*mm),
        "h1": ParagraphStyle("h1", fontName=sans, fontSize=15, leading=21, textColor=colors.HexColor("#143D59"), spaceAfter=4*mm),
        "h2": ParagraphStyle("h2", fontName=sans, fontSize=11, leading=16, textColor=colors.HexColor("#E07A5F"), spaceBefore=3*mm, spaceAfter=2*mm),
        "body": ParagraphStyle("body", fontName=serif, fontSize=9.2, leading=15.2, alignment=TA_JUSTIFY, firstLineIndent=18, textColor=colors.HexColor("#263238"), spaceAfter=2.4*mm, allowWidows=0, allowOrphans=0),
        "small": ParagraphStyle("small", fontName=serif, fontSize=8, leading=12, textColor=colors.HexColor("#455A64")),
        "callout": ParagraphStyle("callout", fontName=serif, fontSize=8.7, leading=14, leftIndent=5*mm, rightIndent=5*mm, borderColor=colors.HexColor("#81B29A"), borderWidth=0.8, borderPadding=7, backColor=colors.HexColor("#F2F7F5"), spaceBefore=2*mm, spaceAfter=3*mm),
        "code": ParagraphStyle("code", fontName=mono, fontSize=6.8, leading=9.2, leftIndent=3*mm, rightIndent=3*mm, borderPadding=6, backColor=colors.HexColor("#F4F4F4"), textColor=colors.HexColor("#273043")),
        "toc": ParagraphStyle("toc", fontName=serif, fontSize=9.5, leading=15, leftIndent=4*mm),
    }


def clean(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def unit_text(chapter: str, topic: str, unit: str, idx: int) -> dict[str, object]:
    contexts = {
        "微生物": "组成型丰度、检测下限、批次效应与菌株异质性会同时改变观察到的信号",
        "单细胞": "细胞并非独立生物学重复，供体、样本和批次必须进入统计设计",
        "HGT": "donor、recipient、cargo、断点证据和生态接触机会必须被分别记录",
        "证据": "声明必须能回到具体来源、适用体系、方向和不确定性",
        "Agent": "模型输出只是候选动作，环境反馈和验证器决定它能否进入下一阶段",
    }
    context = next((v for k, v in contexts.items() if k in chapter or k in unit), "研究问题、数据、模型和结论之间必须保持可追溯关系")
    principle = (
        f"“{unit}”不是一个装饰性步骤，而是决定系统能否给出可信科学结论的控制点。{context}。"
        "如果 Agent 只追求流畅答案，它会把未知条件补成看似合理的叙事；可靠流程则要求每个关键判断都留下输入、假设、动作、输出与失败原因。"
    )
    method = (
        f"实践中可把该环节写成四列协议：对象、允许的操作、通过标准、失败后的下一步。以“{topic}”为任务背景时，"
        "先冻结分析单位和数据版本，再定义可证伪预测；随后用独立验证器检查结构、统计与证据，最后才允许总结。"
        "这种顺序会牺牲少量速度，却显著降低循环论证、数据泄漏和事后解释。"
    )
    caveat = (
        "常见错误是把工具成功执行当成科学问题已经解决。命令无报错只能证明计算完成，不能证明输入合理、比较公平或外推成立。"
        "第二类错误是把多个弱证据相加后称为机制；真正的证据收敛应要求不同误差结构的资料在方向上相容，并保留冲突。"
    )
    case = (
        f"贯穿案例：在精神疾病相关肠道 HGT 研究中，{unit}应落到预先定义的数据字段或检验上。"
        "例如把“疾病改变遗传交换”拆成生态接触机会、观测事件、机会校正偏离和断点复核四层。只有校正后偏离、负对照和独立复核同时支持，才能把结论从描述升级为遗传流重塑候选。"
    )
    checklist = [
        f"写出“{unit}”的输入和输出模式；",
        "指定至少一个可导致结论被否定的观测；",
        "把数据质量、模型假设与生物学解释分别记录；",
        "确认模拟演示、真实分析和待验证假设有清晰标签；",
    ]
    code = None
    if idx % 3 == 0:
        code = textwrap.dedent(f"""
        task = {{
            "stage": "{unit}",
            "inputs": ["data_version", "question", "constraints"],
            "gates": ["schema", "negative_control", "evidence"],
            "status": "requires_human_review",
        }}
        assert task["gates"]
        """).strip()
    return {"principle": principle, "method": method, "caveat": caveat, "case": case, "checklist": checklist, "code": code}


class BookDoc(BaseDocTemplate):
    def __init__(self, filename: str, style_map: dict[str, ParagraphStyle]):
        super().__init__(filename, pagesize=A5, leftMargin=18*mm, rightMargin=16*mm, topMargin=18*mm, bottomMargin=18*mm, title="BioAgentLab：面向生物学发现的证据型 AI Agent", author="BioAgentLab Project")
        self.style_map = style_map
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        self.addPageTemplates([
            PageTemplate(id="plain", frames=frame, onPage=self.draw_plain),
            PageTemplate(id="body", frames=frame, onPage=self.draw_body),
        ])

    def draw_plain(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#143D59"))
        canvas.rect(0, A5[1]-6*mm, A5[0], 6*mm, fill=1, stroke=0)
        canvas.restoreState()

    def draw_body(self, canvas, doc):
        canvas.saveState()
        canvas.setFont("BookSans", 7.5)
        canvas.setFillColor(colors.HexColor("#607D8B"))
        canvas.drawString(18*mm, A5[1]-10*mm, "BioAgentLab · 证据型科学 Agent")
        canvas.drawRightString(A5[0]-16*mm, 10*mm, str(doc.page))
        canvas.setStrokeColor(colors.HexColor("#D8E2E5"))
        canvas.line(18*mm, A5[1]-12*mm, A5[0]-16*mm, A5[1]-12*mm)
        canvas.restoreState()


def build_markdown() -> None:
    lines = ["# BioAgentLab：面向生物学发现的证据型 AI Agent", "", "版本：v0.1 教材版", "", "## 使用说明", "", "本书将模拟、方法建议和真实证据严格分开。贯穿案例用于展示研究设计，不预设阳性结果。", ""]
    for n, (part, chapter, units) in enumerate(CHAPTERS, 1):
        lines += [f"# 第{n}章 {chapter}", "", f"**所属：{part}**", ""]
        for i, unit in enumerate(units, 1):
            payload = unit_text(chapter, chapter, unit, i)
            lines += [f"## {n}.{i} {unit}", "", payload["principle"], "", payload["method"], "", f"**风险提示。** {payload['caveat']}", "", f"**贯穿案例。** {payload['case']}", "", "检查表：", ""]
            lines += [f"- {item}" for item in payload["checklist"]]
            if payload["code"]:
                lines += ["", "```python", payload["code"], "```"]
            lines.append("")
    lines += ["# 参考文献", ""] + [f"{i}. {ref}" for i, ref in enumerate(REFERENCES, 1)]
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def build_pdf(toc_pages: list[int] | None = None) -> None:
    s = styles()
    story = [
        NextPageTemplate("plain"), Spacer(1, 28*mm),
        Paragraph("BioAgentLab", s["cover"]),
        Paragraph("面向生物学发现的证据型 AI Agent", s["cover"]),
        Paragraph("从生成、反思与证据核验，到微生物组、单细胞和多智能体科研工作流", s["subtitle"]),
        Spacer(1, 30*mm),
        Paragraph("v0.1 教材版 · 2026", s["subtitle"]), PageBreak(),
        Paragraph("版权与使用说明", s["chapter"]),
        Paragraph("本书用于教学、研究设计与可复现计算。示例结果不构成医学建议；未明确标注为真实数据分析的数字和结论均为教学模拟。使用受限人类数据时，应遵守伦理审批、数据使用协议与隐私保护要求。", s["body"]),
        Paragraph("阅读路径", s["h1"]),
        Paragraph("初学者可依次阅读第一至第四篇，再选择微生物组或单细胞章节；有工程经验的读者可从 Scientific Supervisor 进入，并回查证据和统计章节；希望复现贯穿案例的读者应先完成组成型数据、批次效应与负对照部分。", s["body"]),
        Paragraph("符号约定", s["h1"]),
        Paragraph("【真实资料】表示可追溯到公开文献或数据；【教学模拟】表示用于说明流程的合成示例；【待验证假设】表示需要真实数据、独立复核或实验验证的命题。", s["callout"]), PageBreak(),
        Paragraph("目录", s["chapter"]),
    ]
    toc_rows = []
    for i, (part, chapter, units) in enumerate(CHAPTERS, 1):
        shown_page = toc_pages[i - 1] if toc_pages else "·"
        toc_rows.append([Paragraph(f"第{i}章  {clean(chapter)}", s["toc"]), Paragraph(str(shown_page), s["toc"])])
    table = Table(toc_rows, colWidths=[95*mm, 12*mm], repeatRows=0)
    table.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("LINEBELOW", (0,0), (-1,-1), 0.25, colors.HexColor("#D8E2E5")), ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 0)]))
    story += [table, PageBreak(), NextPageTemplate("body")]
    for n, (part, chapter, units) in enumerate(CHAPTERS, 1):
        story += [
            Spacer(1, 22*mm), Paragraph(clean(part), s["part"]),
            Paragraph(f"第{n}章<br/>{clean(chapter)}", s["chapter"]),
            Paragraph("本章学习目标", s["h1"]),
            Paragraph("理解本章概念在科学 Agent 中的位置；能把概念转换为可执行的数据契约与验证门；能识别常见失败模式；能将方法迁移到贯穿 HGT 案例，同时不把设计目标误写成研究结果。", s["body"]),
            Paragraph("章末产出", s["h1"]),
            Paragraph(f"完成一张“{clean(chapter)}”协议卡：包括输入、输出、证据等级、失败条件、人工审批点和可复现记录。", s["callout"]),
            PageBreak(),
        ]
        for i, unit in enumerate(units, 1):
            payload = unit_text(chapter, chapter, unit, i)
            story += [Paragraph(f"{n}.{i}  {clean(unit)}", s["h1"]), Paragraph(clean(payload["principle"]), s["body"]), Paragraph("操作方法", s["h2"]), Paragraph(clean(payload["method"]), s["body"]), Paragraph("易错点", s["h2"]), Paragraph(clean(payload["caveat"]), s["callout"]), Paragraph("贯穿案例", s["h2"]), Paragraph(clean(payload["case"]), s["body"])]
            if payload["code"]:
                story += [Preformatted(payload["code"], s["code"]), Spacer(1, 2*mm)]
            checks = "<br/>".join(f"□ {clean(item)}" for item in payload["checklist"])
            story += [Paragraph("执行检查表", s["h2"]), Paragraph(checks, s["small"]), Spacer(1, 2*mm), Paragraph("思考与练习", s["h2"]), Paragraph(f"1. 为“{clean(unit)}”设计一个失败案例。<br/>2. 写出一个能改变当前结论的反证。<br/>3. 指出哪一步必须由人类专家审批。", s["small"]), PageBreak()]
    story += [Paragraph("附录 A：项目实施清单", s["chapter"])]
    for title, body in [
        ("问题冻结", "记录问题版本、主要结局、分析单位、数据截止日期和禁止事后修改的部分。"),
        ("数据审计", "记录许可、隐私、样本独立性、缺失、批次、测序与组装质量。"),
        ("证据审计", "逐条保存声明、来源、支持方向、适用体系、证据等级和冲突。"),
        ("模型审计", "记录训练与测试分割、超参数、随机种子、阴性对照和校准。"),
        ("Agent 审计", "记录提示词、工具版本、动作轨迹、失败恢复、预算和人工审批。"),
    ]:
        story += [Paragraph(title, s["h1"]), Paragraph(body, s["body"])]
    story += [PageBreak(), Paragraph("附录 B：HGT 研究最小数据字典", s["chapter"])]
    rows = [["字段", "含义", "最低检查"], ["sample_id", "去标识样本编号", "唯一且可追溯"], ["donor / recipient", "方向可信的物种标识", "统一 taxonomy 版本"], ["cargo", "转移基因或区段", "注释版本与置信度"], ["breakpoint", "断点证据", "reads 或局部组装复核"], ["opportunity", "生态接触机会", "跨研究稳定性"], ["quality", "测序和组装质量", "预设阈值"], ["phenotype", "疾病与深表型", "盲法和缺失机制"]]
    t = Table([[Paragraph(clean(c), s["small"]) for c in row] for row in rows], colWidths=[27*mm, 46*mm, 34*mm], repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#143D59")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#AAB7B8")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("FONTNAME", (0,0), (-1,-1), "BookSerif"), ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4)]))
    story += [t, PageBreak(), Paragraph("参考文献", s["chapter"])]
    for i, ref in enumerate(REFERENCES, 1):
        story.append(Paragraph(f"{i}. {clean(ref)}", s["small"]))
        story.append(Spacer(1, 2*mm))
    doc = BookDoc(str(PDF_PATH), s)
    doc.build(story)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    BOOK.mkdir(parents=True, exist_ok=True)
    build_markdown()
    build_pdf()
    from pypdf import PdfReader
    reader = PdfReader(str(PDF_PATH))
    extracted = [(index + 1, page.extract_text() or "") for index, page in enumerate(reader.pages)]
    toc_pages = []
    for number, (_, chapter, _) in enumerate(CHAPTERS, 1):
        marker = f"第{number}章"
        match = next((page_no for page_no, text in extracted if page_no > 3 and marker in text and chapter in text), None)
        if match is None:
            raise RuntimeError(f"Could not locate chapter page: {marker} {chapter}")
        toc_pages.append(match)
    build_pdf(toc_pages)
    print(PDF_PATH)

