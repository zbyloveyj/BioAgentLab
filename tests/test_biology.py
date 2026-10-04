import math
import pytest
from bioagent.biology import clr, bh_adjust, pseudobulk, audit_sample_ids, align_by_id


@pytest.mark.parametrize('bad', [[], [0,0], [-1,2], [float('nan'),1], [float('inf'),1], [True,1], [0,2]])
def test_clr_rejects_bad(bad):
    with pytest.raises(ValueError): clr(bad)


def test_clr_center_and_scale():
    a, b = clr([1,2,4]), clr([10,20,40])
    assert sum(a) == pytest.approx(0, abs=1e-12)
    assert a == pytest.approx(b)
    assert a == pytest.approx([-math.log(2),0,math.log(2)])


def test_clr_explicit_pseudocount():
    assert sum(clr([0,1,2], .1)) == pytest.approx(0, abs=1e-12)


@pytest.mark.parametrize('p', [0,-1,float('nan'),True])
def test_bad_pseudocount(p):
    with pytest.raises(ValueError): clr([1,2],p)


def test_bh_known():
    assert bh_adjust([.01,.04,.03,.002]) == pytest.approx([.02,.04,.04,.008])
    assert bh_adjust([]) == []
    assert bh_adjust([0,1]) == [0,1]


@pytest.mark.parametrize('p', [[-.1],[1.1],[float('nan')],[float('inf')],[True]])
def test_bh_invalid(p):
    with pytest.raises(ValueError): bh_adjust(p)


def cells():
    return [{'cell_id':'a','donor_id':'D1','cell_type':'C','counts':[1,2]},
            {'cell_id':'b','donor_id':'D1','cell_type':'C','counts':[3,4]},
            {'cell_id':'c','donor_id':'D2','cell_type':'C','counts':[5,6]}]


def test_pseudobulk_conservation():
    out = pseudobulk(cells())
    assert out[('D1','C')] == [4,6]
    assert out[('D2','C')] == [5,6]
    assert [sum(v[i] for v in out.values()) for i in range(2)] == [9,12]


@pytest.mark.parametrize('field,value', [('donor_id',''),('cell_type',''),('cell_id',''),('counts',[-1,2]),('counts',[1.2,2]),('counts',[True,2]),('counts',[1])])
def test_pseudobulk_invalid(field,value):
    data=cells(); data[1][field]=value
    with pytest.raises(ValueError): pseudobulk(data)


def test_pseudobulk_duplicate():
    data=cells(); data[1]['cell_id']='a'
    with pytest.raises(ValueError): pseudobulk(data)
    with pytest.raises(ValueError): pseudobulk([])


@pytest.mark.parametrize('rows', [[],[{}],[{'sample_id':''}],[{'sample_id':'A'},{'sample_id':'A'}]])
def test_sample_audit_rejects(rows):
    with pytest.raises(ValueError): audit_sample_ids(rows)


def test_alignment_uses_ids():
    a=[{'sample_id':'B','v':2},{'sample_id':'A','v':1}]
    b=[{'sample_id':'A','v':3},{'sample_id':'C','v':4}]
    out=align_by_id(a,b)
    assert out['pairs'][0][0]['v']==1
    assert out['left_only']==['B'] and out['right_only']==['C']
