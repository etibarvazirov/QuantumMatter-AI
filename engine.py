from pathlib import Path
import json
import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors, rdFingerprintGenerator, AllChem
import xgboost as xgb
from functools import lru_cache
ROOT=Path(__file__).resolve().parent
CFG=json.loads((ROOT/'models/app_config.json').read_text())
FP=rdFingerprintGenerator.GetMorganGenerator(radius=CFG['morgan_radius'],fpSize=CFG['morgan_bits'])
EXTRA={'NumAtoms':lambda m:m.GetNumAtoms(),'NumBonds':lambda m:m.GetNumBonds(),'NumConjugatedBonds':lambda m:sum(b.GetIsConjugated() for b in m.GetBonds())}
def molecule(s):
    if not isinstance(s,str) or not s.strip() or len(s)>3000: raise ValueError('Enter a valid SMILES (max 3000 characters).')
    m=Chem.MolFromSmiles(s.strip())
    if m is None or m.GetNumAtoms()==0: raise ValueError('Invalid SMILES.')
    if m.GetNumAtoms()>150 or len(Chem.GetMolFrags(m))!=1: raise ValueError('Use one connected molecule with at most 150 atoms.')
    return Chem.MolFromSmiles(Chem.MolToSmiles(m))
def features(m):
    d=np.array([(EXTRA[n] if n in EXTRA else getattr(Descriptors,n))(m) for n in CFG['descriptor_names']],dtype=np.float32)
    x=np.concatenate([d,FP.GetFingerprintAsNumPy(m)]).astype(np.float32)
    if not np.isfinite(x).all(): raise ValueError('Non-finite descriptors.')
    return x
@lru_cache(maxsize=1)
def models():
    out={}
    for t in CFG['targets']:
        out[t]=[]
        for s in CFG['seeds']:
            b=xgb.Booster(params={'nthread':2}); b.load_model(str(ROOT/f'models/app_{t}_{s}.json')); out[t].append(b)
    return out
def predict(ms):
    X=np.stack([features(m) for m in ms]); D=xgb.DMatrix(X); out={}
    for t,bs in models().items(): out[t]=np.mean([b.predict(D) for b in bs],axis=0)
    out['Energy_Gap']=out['LUMO']-out['HOMO']; return out
@lru_cache(maxsize=1)
def domain():
    with np.load(ROOT/'data/domain.npz') as d:return d['low'],d['high']
def outside(m):
    d=features(m)[:21]; lo,hi=domain(); return [n for n,v,l,h in zip(CFG['descriptor_names'],d,lo,hi) if v<l-1e-5 or v>h+1e-5]
def walk(m,t,start):
    A=np.zeros((m.GetNumAtoms(),m.GetNumAtoms()))
    for b in m.GetBonds():
        i,j=b.GetBeginAtomIdx(),b.GetEndAtomIdx(); zi=m.GetAtomWithIdx(i).GetAtomicNum(); zj=m.GetAtomWithIdx(j).GetAtomicNum()
        A[i,j]=A[j,i]=b.GetBondTypeAsDouble()*(1+.25*int(b.GetIsConjugated()))*(1+.25*abs(zi-zj)/(zi+zj))
    if np.any(A>0): A/=A[A>0].mean()
    e,V=np.linalg.eigh(np.diag(A.sum(1))-A); e=np.maximum(e,0); v=V[start,:]
    return np.maximum(V@(np.exp(-t*e)*v),0),abs(V@(np.exp(-1j*t*e)*v))**2
