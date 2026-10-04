"""Generate eight self-contained offline notebooks; optionally execute all cells."""
from pathlib import Path
import argparse
import hashlib
import json
import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
LESSONS = [
('01_tools_and_contracts', '工具与契约', '先验证输入，再消耗预算与执行。此例不联网。', [
('注册一个有限数值均值工具。', '''import math
from bioagent.runtime import Tool, ToolRegistry, Budget

def mean(values):
    return sum(values) / len(values)
def validate(args):
    xs=args['values']
    if not xs or any(isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) for x in xs):
        raise ValueError('Invalid values')
registry=ToolRegistry()
registry.register(Tool('mean',mean,validate))
budget=Budget(2)
assert registry.call('mean',{'values':[1,2,3]},budget=budget)==2
print('Used actions:',budget.used)'''),
('错误参数必须在执行前拒绝。', '''try:
    registry.call('mean',{'values':[]},budget=budget)
except ValueError:
    print('Empty input correctly rejected')
assert budget.used==1''')]),
('02_retrieval_and_evidence', '本地检索与证据台账', '所有文档均为合成；检索分数不是证据概率。', [
('检索中文与英文材料。', '''from bioagent.retrieval import Document,BM25Index
from bioagent.evidence import Evidence,EvidenceLedger
index=BM25Index([Document('D1','微生物代谢 metabolite','synthetic://1'),Document('D2','宿主细胞 immune','synthetic://2')])
hits=index.search('微生物代谢')
assert hits[0].document.identifier=='D1'
print([(h.document.identifier,h.score) for h in hits])'''),
('同研究片段只算一个研究，合成材料默认不算真实支持。', '''ledger=EvidenceLedger([
 Evidence('E1','S1','C1','synthetic text','synthetic://1','supports','demo',True),
 Evidence('E2','S1','C1','synthetic fragment','synthetic://2','supports','demo',True)])
assert ledger.assess('C1')['verdict']=='insufficient'
result=ledger.assess('C1',include_synthetic=True)
assert result['support_studies']==['S1']
print(result)''')]),
('03_scientific_roles', '生成、反思与修订', '脚本模型用于验证控制流，不代表真实LLM能力。', [
('生成三个结构化候选。', '''from bioagent.demo import DemoModel,CLAIMS
from bioagent.research import ResearchAgents
from bioagent.evidence import EvidenceLedger
agents=ResearchAgents(DemoModel(),set(CLAIMS))
candidates=agents.generate('微生物—代谢物—宿主研究')
assert len(candidates)==3
for h in candidates: print(h.identifier,h.statement)'''),
('反思和修订不能保留旧核验状态。', '''parent=candidates[0]
assessment=EvidenceLedger().assess_candidate(parent)
critiques=agents.reflect(parent,assessment)
child=agents.evolve(parent,critiques)
assert child.version==2 and not child.verified_links and parent.version==1
print(critiques)
print(child)''')]),
('04_debate_and_elo', '成对辩论与Elo', '使用测试替身核对辩论接口；排名不是科学真值概率。', [
('验证Elo算术。', '''from bioagent.ranking import elo_pair,tournament
assert elo_pair(1000,1000,1)==(1012,988)
assert elo_pair(1000,1000,.5)==(1000,1000)
print(tournament(['A','B','C'],lambda a,b:.5))'''),
('两次位置互换评审；这个测试模型只返回平局。', '''import json
from bioagent.debate import DebateAgent
from bioagent.core import CallableLLMClient
from bioagent.evidence import Candidate,EvidenceLedger
from bioagent.runtime import Budget

def model(prompt):
    obj=json.loads(prompt)
    if obj['task']=='debate_advocate':
        return json.dumps({'argument':'A testable candidate','limitations':['No real evidence'],'evidence_ids':[]})
    return json.dumps({'winner':'draw','reason':'Evidence absent','evidence_ids':[]})
result=DebateAgent(CallableLLMClient(model)).compare(Candidate('A','first',('C1',)),Candidate('B','second',('C2',)),EvidenceLedger(),budget=Budget(4))
assert result['outcome']==.5
print(result)''')]),
('05_compositional_data', '微生物组成与多重检验', '小向量用于验证数值性质，不是疾病研究结果。', [
('CLR的中心化和尺度性质。', '''from bioagent.biology import clr,bh_adjust
x=clr([1,2,4]); y=clr([10,20,40])
assert abs(sum(x))<1e-12
assert all(abs(a-b)<1e-12 for a,b in zip(x,y))
print(x)
for p in [.01,.1,1.0]: print(p,clr([0,2,4],p))'''),
('核对已知BH结果。', '''q=bh_adjust([.01,.04,.03,.002])
expected=[.02,.04,.04,.008]
assert all(abs(a-b)<1e-12 for a,b in zip(q,expected))
print(q)''')]),
('06_donor_pseudobulk', '供体聚合与样本对齐', '细胞数不等于独立供体数。', [
('按供体与细胞类型聚合原始计数。', '''from bioagent.biology import pseudobulk,align_by_id
cells=[{'cell_id':'a','donor_id':'D1','cell_type':'C','counts':[1,2]},
       {'cell_id':'b','donor_id':'D1','cell_type':'C','counts':[3,4]},
       {'cell_id':'c','donor_id':'D2','cell_type':'C','counts':[5,6]}]
result=pseudobulk(cells)
assert result[('D1','C')]==[4,6]
assert [sum(v[i] for v in result.values()) for i in range(2)]==[9,12]
print(result)'''),
('按标识而非行号连接。', '''left=[{'sample_id':'D2'},{'sample_id':'D1'}]
right=[{'sample_id':'D1'},{'sample_id':'D3'}]
aligned=align_by_id(left,right)
assert aligned['pairs'][0][0]['sample_id']=='D1'
assert aligned['left_only']==['D2']
print(aligned)''')]),
('07_failure_and_budget', '故障、路径与预算', '正确拒绝是一项成功行为。', [
('验证预算停止与依赖环拒绝。', '''from bioagent.runtime import Budget,BudgetExceeded,topological_order,safe_path
from tempfile import TemporaryDirectory
from pathlib import Path
budget=Budget(1); budget.consume()
try: budget.consume()
except BudgetExceeded: print('Budget correctly exhausted')
try: topological_order({'A':{'B'},'B':{'A'}})
except ValueError: print('Cycle rejected')
with TemporaryDirectory() as directory:
    try: safe_path(Path(directory),'../escape.json')
    except PermissionError: print('Workspace escape rejected')'''),
('运行一个预算不足的完整流程，仍保存有边界的部分报告。', '''from bioagent.demo import run_demo
with TemporaryDirectory() as directory:
    report=run_demo(Path(directory)/'partial',budget_limit=5)
    assert report['stop_reason']=='budget_exhausted'
    assert not report['real_biological_validation']
    print(report['completed_steps'])''')]),
('08_capstone_report_audit', '综合案例与报告审计', '全流程默认离线、合成且不作真实机制结论。', [
('执行、核对状态并验证产物哈希。', '''from tempfile import TemporaryDirectory
from pathlib import Path
import hashlib,json
from bioagent.demo import run_demo
with TemporaryDirectory() as directory:
    root=Path(directory)/'complete'
    report=run_demo(root)
    assert report['stop_reason'].startswith('completed_teaching')
    assert all(a['unresolved'] for a in report['real_evidence_assessment'])
    assert report['revision']['verified_links']==()
    manifest=json.loads((root/'manifest.json').read_text())
    for name,digest in manifest['files'].items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest
    print(report['conclusion'])
    print(report['budget'])
    print(report['preference_tournament'])'''),
('检查证据边界。', '''assert report['mode']=='synthetic_offline_teaching'
assert report['real_biological_validation'] is False
assert all(e['synthetic'] for e in report['evidence'])
assert report['preference_tournament']['interpretation']=='relative_preference_not_truth_probability'
print('All report boundary checks passed')''')]),
]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    out=ROOT/'notebooks'; out.mkdir(exist_ok=True)
    verified=[]
    for name,title,intro,sections in LESSONS:
        cells=[nbf.v4.new_markdown_cell(f'# {title}\n\n{intro}\n\n先在仓库根目录安装项目。所有数据为教学构造。')]
        for explanation,code in sections:
            cells += [nbf.v4.new_markdown_cell(explanation),nbf.v4.new_code_cell(code)]
        cells.append(nbf.v4.new_markdown_cell('## 练习\n修改一个输入使其违反契约，确认系统拒绝；说明这个测试不能证明哪些科学结论。'))
        for i,cell in enumerate(cells):
            cell['id']=hashlib.sha256((name+str(i)+cell.source).encode()).hexdigest()[:12]
        nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}})
        if args.execute:
            from nbclient import NotebookClient
            NotebookClient(nb,timeout=120,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
            verified.append(name)
        nbf.write(nb,out/(name+'.ipynb'))
    (out/'README.md').write_text('# 离线Notebook课程\n\n'+ '\n'.join(f'- [{title}]({name}.ipynb)' for name,title,_,_ in LESSONS)+'\n\n生成与逐个执行：`python scripts/build_notebooks.py --execute`。\n',encoding='utf-8')
    info={'generated':len(LESSONS),'executed':len(verified),'notebooks':verified,'mode':'offline_synthetic'}
    (ROOT/'build').mkdir(exist_ok=True)
    (ROOT/'build/notebook_verification.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
    print(json.dumps(info,indent=2))


if __name__=='__main__': main()
