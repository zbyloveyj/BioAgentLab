"""Lesson 12：不联网、无 API Key 的证据导出练习。"""
from agent_course.config import output_dir
from agent_course.reports import export_evidence
from agent_course.rag import retrieve

def main() -> None:
    question = "宏基因组与16S有什么不同？"
    notes = retrieve(question)
    print(f"本地检索到 {len(notes)} 条教学笔记：")
    records = []
    for note in notes:
        print(note["id"], note["title"], f"来源：{note['source']}")
        records.append({
            "pmid": "", # 故意不伪造 PMID
            "title": note["title"],
            "pubdate": "",
            "abstract": note["text"],
            "url": "",
            "retrieved_at": "本地教学笔记，非PubMed数据",
        })
    paths = export_evidence(records, output_dir(), stem="local_demo_only")
    print("练习文件：", *paths, sep="\n")

if __name__ == "__main__":
    main()
