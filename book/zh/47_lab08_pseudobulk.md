# 实训八 从细胞到供体：构建并审计Pseudobulk

## 目标与小型数据

本实训使用三位供体、两种细胞类型和两个基因。目标是检查聚合逻辑与独立单位，不进行正式差异表达。所有计数为人工构造。

```python
from bioagent.biology import pseudobulk
cells = [
    {"cell_id":"c1","donor_id":"D1","cell_type":"T","counts":[2,1]},
    {"cell_id":"c2","donor_id":"D1","cell_type":"T","counts":[3,2]},
    {"cell_id":"c3","donor_id":"D1","cell_type":"B","counts":[1,4]},
    {"cell_id":"c4","donor_id":"D2","cell_type":"T","counts":[4,1]},
    {"cell_id":"c5","donor_id":"D2","cell_type":"B","counts":[2,3]},
    {"cell_id":"c6","donor_id":"D3","cell_type":"T","counts":[1,2]},
]
result = pseudobulk(cells)
for group, counts in sorted(result.items()):
    print(group, counts)
```

D1的T细胞应聚合为5、3。D3没有B细胞记录，不应自动生成一个“零表达B细胞”组。未观察到某种细胞与该细胞所有基因表达为零不同。

## 验证计数守恒

分别计算原始细胞与聚合矩阵每个基因的总计数。它们应一致。这项测试可以发现遗漏、重复或错误分组导致的数据损失。

```python
raw_total = [sum(cell["counts"][g] for cell in cells) for g in range(2)]
agg_total = [sum(counts[g] for counts in result.values()) for g in range(2)]
assert raw_total == agg_total
print(raw_total)
```

守恒不证明聚合单位正确。例如把不同供体混合后再求和也可能守恒。因此还要检查键是否确实由供体与细胞类型构成。

## 故意破坏输入

复制一个cell_id，程序应拒绝。删除donor_id，程序应拒绝。把计数变成小数，程序也应拒绝，因为该函数契约要求原始整数计数。

```python
from copy import deepcopy
bad = deepcopy(cells)
bad[1]["cell_id"] = "c1"
try:
    pseudobulk(bad)
except ValueError:
    print("Duplicate cell rejected")

bad = deepcopy(cells)
bad[0]["counts"] = [0.3, 1.7]
try:
    pseudobulk(bad)
except ValueError:
    print("Non-integer counts rejected")
```

不要通过把对数表达四舍五入成整数来绕过检查。类型符合要求不等于数据语义正确，原始计数的来源需要处理历史确认。

## 供体覆盖审计

统计每种细胞类型由多少位供体提供，以及每个供体贡献多少细胞。D3缺少B细胞可能是捕获不足，也可能与真实组成有关；需要额外信息，不应由模型自动决定。

```python
from collections import Counter, defaultdict
n_cells = Counter((c["donor_id"], c["cell_type"]) for c in cells)
donors = defaultdict(set)
for donor, cell_type in n_cells:
    donors[cell_type].add(donor)
print(n_cells)
print({kind: len(ids) for kind, ids in donors.items()})
```

正式统计中，某细胞类型只有很少供体时，不能靠增加同一供体细胞数解决群体推断问题。应报告限制，并结合设计选择后续分析。

## 与另一组学对齐

为D1、D2、D3准备微生物或代谢物摘要，再按donor_id与细胞状态连接。不能把每位供体的代谢物值复制到其所有细胞后，声称获得更多独立观测。

如果代谢样本来自不同时间，应额外检查时间窗口。相同供体不必然代表同一生物状态。对纵向研究，配对键可能需要包含供体、访视与样本类型。

## 正式差异分析前还缺什么

本实训没有拟合计数分布、估计离散度或构建设计矩阵，也没有进行基因过滤与差异检验。它只完成正确聚合与审计。报告必须保留这个范围，不能把聚合矩阵称为差异表达结果。

下一步应使用成熟方法，并明确条件、协变量、重复测量和多重检验。Agent可以组织这些步骤，但方法选择需要具体研究背景。

## 提交与参考答案

提交聚合矩阵、守恒测试、供体覆盖表和三个错误输入案例。参考答案应解释D3缺少B细胞为何不等于零表达，以及为什么不能通过复制供体测量扩大样本量。

扩展任务是把输入顺序随机打乱，确认按组得到的计数不变。这项性质能检验程序是否依赖偶然行顺序。
