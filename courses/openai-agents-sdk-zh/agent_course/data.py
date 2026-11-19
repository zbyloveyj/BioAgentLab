"""本地教学模拟数据：不是任何疾病的科学结论。"""
from __future__ import annotations

MICROBES = {
    "Akkermansia muciniphila": {
        "description": "一种与肠道黏液层相关的细菌，常被研究其生态功能。",
        "note": "此处只用于演示工具调用，不能推断疾病风险或治疗作用。",
    },
    "Faecalibacterium prausnitzii": {
        "description": "肠道中常被研究的丁酸相关细菌。",
        "note": "不同分类与实验条件可能影响观察结果，应核对原始论文。",
    },
    "Bacteroides fragilis": {
        "description": "拟杆菌属的一个成员，可用于演示菌种级信息检索。",
        "note": "不可把菌种名称直接等同于特定临床效应。",
    },
}

LOCAL_NOTES = [
    {
        "id": "DEMO-001",
        "title": "菌种与功能并非一一对应",
        "text": "相同菌种在不同菌株、环境和宿主中可能存在不同的功能特征；需注意菌株水平差异。",
        "source": "教学说明（非论文）",
    },
    {
        "id": "DEMO-002",
        "title": "宏基因组与16S的区别",
        "text": "16S rRNA测序主要用于细菌群落标记基因分析；shotgun宏基因组测序更适合观察群落遗传组成和功能潜力。",
        "source": "教学说明（非论文）",
    },
    {
        "id": "DEMO-003",
        "title": "相关性不能直接证明因果",
        "text": "某种细菌与抑郁症相关，并不意味着菌种本身导致疾病。需考虑混杂因素、研究设计及因果证据。",
        "source": "教学说明（非论文）",
    },
    {
        "id": "DEMO-004",
        "title": "研究证据需要可追溯",
        "text": "文献记录至少保留PMID、题名、发表日期、摘要与检索日期，以便核对来源和更新。",
        "source": "教学说明（非论文）",
    },
]
