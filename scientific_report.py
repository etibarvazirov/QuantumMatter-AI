from io import BytesIO
from datetime import datetime, timezone
from xml.sax.saxutils import escape
import json
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Draw
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from engine import ROOT, CFG, features, predict, outside, walk

def build_report(m, membership, time=1., start=0, screening=None, source='Held-out reference candidates'):
    out=BytesIO(); styles=getSampleStyleSheet(); story=[]
    def p(s,style='BodyText'): story.append(Paragraph(escape(str(s)),styles[style]))
    def table(headers,rows,widths=None):
        data=[[Paragraph(escape(str(x)),styles['BodyText']) for x in r] for r in [headers]+list(rows)]
        t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT'); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#cce9e5')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f1f5f9')]),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story.append(t);story.append(Spacer(1,10))
    def image(mol,highlight=None):
        b=BytesIO(); Draw.MolToImage(mol,size=(900,480),highlightAtoms=highlight or []).save(b,format='PNG');b.seek(0);story.append(Image(b,width=440,height=235))
    p('QuantumMatter AI','Title');p('Full Scientific Report','Heading1');p(datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'))
    p('Research prototype: PCE is a computed screening proxy, not measured device efficiency. Quantum walks are graph simulations, not physical electron trajectories.')
    p('1. Molecular explorer','Heading1');p('Canonical SMILES: '+Chem.MolToSmiles(m));p('Dataset membership: '+membership);p('Descriptor range warnings: '+(', '.join(outside(m)) or 'None detected; this is not a guarantee of applicability.'));image(m)
    vals=features(m)[:21];table(['Descriptor','Value','Descriptor','Value'],[[CFG['descriptor_names'][i],f'{vals[i]:.4g}',CFG['descriptor_names'][i+11] if i+11<21 else '',f'{vals[i+11]:.4g}' if i+11<21 else ''] for i in range(11)],[145,70,145,70])
    story.append(PageBreak());p('2. AI property prediction','Heading1');pred=predict([m]); rows=[]
    for t in ['HOMO','LUMO','Energy_Gap','PCE']:
        v=float(pred[t][0]);w=CFG['interval_half_width'][t];rows.append([t,f'{v:.4f}',f'{v-w:.4f} to {v+w:.4f}','%' if t=='PCE' else 'eV'])
    table(['Target','Prediction','90% nominal interval','Unit'],rows,[100,90,170,60]);p('Gap = predicted LUMO minus predicted HOMO. Intervals are calibrated on validation data; coverage is not guaranteed in new chemical domains.')
    p('3. Quantum walk simulation','Heading1');c,q=walk(m,time,start);p(f'Dimensionless time: {time:.2f}; initial atom: {start}; classical sum: {sum(c):.8f}; quantum sum: {sum(q):.8f}.')
    d=Drawing(450,175);d.add(String(10,160,'Classical (blue) / Quantum (teal)',fontSize=10));d.add(Line(35,25,440,25));scale=120/max(float(max(c)),float(max(q)),1e-12);step=400/len(c)
    for i,(a,b) in enumerate(zip(c,q)):
        x=35+i*step;d.add(Rect(x,25,step*.42,float(a)*scale,fillColor=colors.HexColor('#2563eb'),strokeColor=None));d.add(Rect(x+step*.43,25,step*.42,float(b)*scale,fillColor=colors.HexColor('#0d9488'),strokeColor=None))
        if len(c)<=30 or i%10==0:d.add(String(x,12,str(i),fontSize=6))
    story.append(d);m2=Chem.Mol(m)
    for a in m2.GetAtoms():a.SetProp('atomNote',str(a.GetIdx()))
    image(m2,[start]);p('Chemically weighted, mean-normalized graph Laplacian. Bars show probabilities by atom index.')
    story.append(PageBreak());p('4. Material screening','Heading1');p('Source: '+source);df=screening if screening is not None else pd.read_csv(ROOT/'data/screening_ranked.csv');df=df.sort_values('PCE_pred',ascending=False);p(f'{len(df)} candidates in current selection; top 10 shown. Ranking is based on predicted computed PCE.')
    table(['Rank','Canonical SMILES','PCE (%)','Gap (eV)'],[[i+1,r.Canonical_SMILES,f'{r.PCE_pred:.3f}',f'{r.Energy_Gap_pred:.3f}'] for i,r in enumerate(df.head(10).itertuples())],[35,275,60,60]);p('Reference candidates are held-out dataset molecules, not newly discovered materials.')
    story.append(PageBreak());p('5. Research and experiments','Heading1');p('Training: 35,031; calibration: 7,469; held-out test: 7,500. Generic scaffolds are disjoint across these partitions. Models use 21 RDKit descriptors and 2,048 Morgan bits; three XGBoost models per target.')
    df=pd.read_csv(ROOT/'data/app_test_metrics.csv');table(['Target','MAE','RMSE','R2','Coverage'],[[r.target,f'{r.MAE:.4f}',f'{r.RMSE:.4f}',f'{r.R2:.4f}',f'{r.coverage:.1%}'] for r in df.itertuples()],[100,80,80,80,80]);sm=json.loads((ROOT/'data/screening_metrics.json').read_text());p(f'Precision@100: {sm["top_k_precision_reference_top_decile"]:.0%}; top 100 mean reference PCE: {sm["mean_reference_PCE_top"]:.2f}%; all test mean reference PCE: {sm["mean_reference_PCE_all"]:.2f}%. Retrospective computed labels.')
    df=pd.read_csv(ROOT/'data/test_metrics.csv').groupby(['target','strategy']).MAE.agg(['mean','std']).reset_index();table(['Target','Strategy','Mean MAE','SD'],[[r.target,r.strategy,f'{r.mean:.5f}',f'{r.std:.5f}'] for r in df.itertuples()],[80,180,80,80]);p('Quantum hybrid did not meet the 5% improvement criterion; paired confidence intervals include zero. No quantum advantage established.')
    for t in ['HOMO','LUMO','Energy_Gap','PCE']:
        story.append(PageBreak());p(t+' - held-out prediction results','Heading1');im=Image(str(ROOT/f'data/app_{t}_scatter.png'));im._restrictSize(450,550);story.append(im)
    p('Data source: CEPDB mirror, huggingface.co/datasets/Tommy-DING/organic-solar-cell-molecule-property-prediction. No experimental device validation is claimed.')
    def footer(canvas,doc):canvas.setFont('Helvetica',9);canvas.setFillColor(colors.HexColor('#475569'));canvas.drawString(40,25,'QuantumMatter AI | Scientific report');canvas.drawRightString(555,25,str(doc.page))
    SimpleDocTemplate(out,pagesize=A4,leftMargin=40,rightMargin=40,topMargin=40,bottomMargin=42).build(story,onFirstPage=footer,onLaterPages=footer);return out.getvalue()
