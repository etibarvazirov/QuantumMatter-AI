import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from rdkit import Chem, rdBase
from rdkit.Chem import Draw, AllChem
from scientific_report import build_report
from learning import module_help, academy
from localize import style, name, PAGES
from engine import ROOT,CFG,molecule,predict,outside,walk,features
st.set_page_config(page_title='QuantumMatter AI',page_icon='⚛️',layout='wide')
style()
lang=st.sidebar.selectbox('Language / Dil / Язык',['English','Azərbaycan','Русский'])
def tr(e,a,r):return dict(English=e,Azərbaycan=a,Русский=r)[lang]
st.markdown('<div class="qmhero"><div class="qmkicker">MATERIALS SCIENCE / AI / GRAPH SIMULATION</div><h1>⚛ QuantumMatter AI</h1><p>'+tr('Virtual Materials Laboratory · Organic photovoltaic screening','Virtual material laboratoriyası · Üzvi fotovoltaik material seçimi','Виртуальная лаборатория · Отбор органических фотоэлектрических материалов')+'</p></div>',unsafe_allow_html=True)
st.info(tr('Research prototype. PCE is a computed molecular screening proxy, not measured device efficiency. Quantum walks are graph simulations, not physical electron trajectories.','Tədqiqat prototipi. PCE hesablanmış göstəricidir, real cihaz səmərəliliyi deyil. Kvant gəzintisi qraf simulyasiyasıdır.','Исследовательский прототип. PCE — расчётный показатель, не измеренный КПД устройства. Квантовое блуждание — симуляция графа.'))
@st.cache_data
def table(n):return pd.read_csv(ROOT/'data'/n)
rank=table('screening_ranked.csv'); known=table('known.csv').set_index('Canonical_SMILES').split.to_dict()
page=st.sidebar.radio(tr('Module','Modul','Модуль'),PAGES,format_func=lambda p:name(p,lang),key='module')
if rdBase.rdkitVersion!=CFG['rdkit_version']:st.sidebar.warning(f'RDKit runtime {rdBase.rdkitVersion}; training {CFG["rdkit_version"]}. Feature compatibility should be checked.')
st.sidebar.caption(tr('Explore · Predict · Learn','Araşdır · Proqnozlaşdır · Öyrən','Исследуй · Прогнозируй · Учись'))
st.header(name(page,lang))
module_help(page,lang)
if page == 'Öyrənmə mərkəzi':
    academy(lang)
elif page in ['Molecular Explorer','AI Property Prediction','Quantum Walk Simulator']:
    sample=st.selectbox(tr('Reference example','Nümunə','Пример'),list(range(1,6)),format_func=lambda i:f'CEPDB candidate #{i}')
    s=st.text_area('SMILES',rank.iloc[sample-1].Canonical_SMILES,key=f'smiles_{sample}')
    try:m=molecule(s)
    except ValueError as e:st.error(str(e));st.stop()
    canonical=Chem.MolToSmiles(m); st.session_state["report_smiles"]=canonical; st.caption(tr('Dataset membership','Dataset mənsubiyyəti','Принадлежность к выборке')+': '+known.get(canonical,'not found'))
    flags=outside(m)
    if flags:st.warning(tr('Outside training descriptor ranges','Təlim diapazonundan kənar','Вне диапазона обучения')+': '+', '.join(flags))
    st.caption(tr('Descriptor-range check is only a coarse applicability warning, not a guarantee.','Parametr diapazonu yalnız ilkin xəbərdarlıqdır, zəmanət deyil.','Проверка диапазона — лишь предварительное предупреждение, не гарантия.'))
    if page=='Molecular Explorer':
        a,b=st.columns(2); a.image(Draw.MolToImage(m,size=(650,420)),caption=tr('2D molecular structure','2D molekul strukturu','2D-структура молекулы'))
        with b:
            if st.button(tr('Generate 3D conformer','3D forma yarat','Создать 3D-конформер')):
                h=Chem.AddHs(m); params=AllChem.ETKDGv3();params.randomSeed=42
                if AllChem.EmbedMolecule(h,params)!=0:st.warning(tr('3D embedding failed for this molecule.','3D forma yaradıla bilmədi.','Не удалось создать 3D-форму.'))
                else:
                    xyz=h.GetConformer().GetPositions(); fig=go.Figure(); colors={'C':'#64748b','H':'#cbd5e1','N':'#2563eb','O':'#ef4444','S':'#eab308'}
                    for bond in h.GetBonds():
                        q=xyz[[bond.GetBeginAtomIdx(),bond.GetEndAtomIdx()]];fig.add_trace(go.Scatter3d(x=q[:,0],y=q[:,1],z=q[:,2],mode='lines',line=dict(color='#94a3b8',width=5),showlegend=False,hoverinfo='skip'))
                    sy=[a.GetSymbol() for a in h.GetAtoms()];fig.add_trace(go.Scatter3d(x=xyz[:,0],y=xyz[:,1],z=xyz[:,2],mode='markers',text=sy,marker=dict(size=[3 if x=='H' else 7 for x in sy],color=[colors.get(x,'#a855f7') for x in sy]),showlegend=False));fig.update_layout(scene=dict(aspectmode='data'),margin=dict(l=0,r=0,t=0,b=0));st.plotly_chart(fig,use_container_width=True);st.caption(tr('Illustrative RDKit conformer, not a quantum-optimized geometry.','RDKit ilə yaradılmış nümunəvi forma, kvant optimallaşdırması deyil.','Иллюстративный конформер RDKit, не квантовая оптимизация.'))
        st.dataframe(pd.DataFrame({'Descriptor':CFG['descriptor_names'],'Value':features(m)[:21]}),hide_index=True)
    elif page=='AI Property Prediction':
        p=predict([m]); cols=st.columns(4)
        for c,t in zip(cols,['HOMO','LUMO','Energy_Gap','PCE']):
            v=float(p[t][0]);w=CFG['interval_half_width'][t];unit='%' if t=='PCE' else 'eV';c.metric(t,f'{v:.3f} {unit}');c.caption(tr('90% nominal interval','90% nominal interval','90% номинальный интервал')+f': [{v-w:.3f}, {v+w:.3f}]')
        fig=go.Figure();
        for t,col in [('HOMO','#2563eb'),('LUMO','#0d9488')]:
            v=float(p[t][0]);fig.add_trace(go.Scatter(x=[0,1],y=[v,v],mode='lines+text',text=['',t],line=dict(color=col,width=5),name=t))
        fig.update_layout(yaxis_title=tr('Energy (eV)','Enerji (eV)','Энергия (эВ)'),xaxis=dict(visible=False),height=350);st.plotly_chart(fig,use_container_width=True);st.caption(tr('Gap = LUMO − HOMO. Intervals calibrated on validation data; coverage is not guaranteed for new chemical domains.','Gap = LUMO − HOMO. İntervallar kalibrasiya edilib; yeni kimyəvi sahələrdə zəmanət yoxdur.','Gap = LUMO − HOMO. Интервалы калиброваны; покрытие в новых химических областях не гарантируется.'))
    else:
        t=st.slider(tr('Dimensionless walk time','Ölçüsüz zaman','Безразмерное время'),0.,8.,1.,.1);start=st.selectbox(tr('Initial atom','Başlanğıc atomu','Начальный атом'),range(m.GetNumAtoms()),format_func=lambda i:f'{i}: {m.GetAtomWithIdx(i).GetSymbol()}');c,q=walk(m,t,start); st.session_state["report_walk"]=(canonical,t,start)
        st.latex(r'P_Q(j,t)=|[e^{-itL}]_{ji}|^2,\quad P_C(j,t)=[e^{-tL}]_{ji}')
        fig=go.Figure();fig.add_bar(x=list(range(len(c))),y=c,name=tr('Classical','Klassik','Классическое'));fig.add_bar(x=list(range(len(q))),y=q,name=tr('Quantum','Kvant','Квантовое'));fig.update_layout(barmode='group',xaxis_title=tr('Atom index','Atom indeksi','Индекс атома'),yaxis_title=tr('Probability','Ehtimal','Вероятность'));st.plotly_chart(fig,use_container_width=True)
        m2=Chem.Mol(m)
        for atom in m2.GetAtoms():atom.SetProp('atomNote',str(atom.GetIdx()))
        st.image(Draw.MolToImage(m2,size=(650,400),highlightAtoms=[start]),caption=tr('Atom indices and initial atom','Atom indeksləri və başlanğıc atomu','Индексы и начальный атом'));st.caption(tr('Probability sums','Ehtimalların cəmi','Суммы вероятностей')+f': {sum(c):.8f} / {sum(q):.8f}. '+tr('Chemically weighted, mean-normalized Laplacian.','Kimyəvi çəkili, orta çəkiyə görə normallaşdırılmış Laplasian.','Химически взвешенный лапласиан с нормировкой по среднему.'))
elif page=='Material Screening':
    mode=st.radio(tr('Source','Mənbə','Источник'),['Held-out reference candidates','Upload CSV / paste SMILES'],format_func=lambda x:tr('Held-out reference candidates','Test namizədləri','Отложенные кандидаты') if x=='Held-out reference candidates' else tr('Upload CSV / paste SMILES','CSV yüklə / SMILES daxil et','Загрузить CSV / вставить SMILES'));
    if mode=='Held-out reference candidates':df=rank.copy();st.caption(tr('Precomputed predictions for held-out CEPDB candidates; not new discoveries.','Test molekulları üçün əvvəlcədən hesablanmış proqnozlar; yeni kəşflər deyil.','Готовые прогнозы для отложенных молекул CEPDB; не новые открытия.'))
    else:
        upload=st.file_uploader(tr('CSV with smiles column','smiles sütunlu CSV','CSV со столбцом smiles'),type='csv');txt=st.text_area(tr('Or one SMILES per line','Və ya hər sətirdə bir SMILES','Или один SMILES на строку'));df=None
        if st.button(tr('Screen candidates','Namizədləri qiymətləndir','Оценить кандидатов')):
            try:
                if upload:
                    if upload.size>2_000_000:raise ValueError('CSV exceeds 2 MB.')
                    raw=pd.read_csv(upload); col=next((c for c in raw if c.lower() in ['smiles','canonical_smiles']),None)
                    if col is None:raise ValueError('CSV requires a smiles column.')
                    ss=raw[col].tolist()
                else:ss=txt.splitlines()
                if len(ss)>500:raise ValueError('Maximum 500 candidates per batch.')
                ms=[];rows=[];errors=[];seen=set()
                for i,s in enumerate(ss):
                    try:
                        m=molecule(s);can=Chem.MolToSmiles(m)
                        if can in seen:continue
                        seen.add(can);flags=outside(m);ms.append(m);rows.append({'Canonical_SMILES':can,'domain_warning':'; '.join(flags),'dataset_membership':known.get(can,'not found')})
                    except Exception as e:errors.append({'row':i+1,'error':str(e)})
                if errors:st.dataframe(pd.DataFrame(errors))
                if not ms:raise ValueError('No valid candidates.')
                df=pd.DataFrame(rows)
                for k,v in predict(ms).items():df[k+'_pred']=v;df[k+'_lower']=v-CFG['interval_half_width'][k];df[k+'_upper']=v+CFG['interval_half_width'][k]
                st.session_state['screen']=df
            except Exception as e:st.error(str(e))
        df=st.session_state.get('screen')
    if df is not None:
        cutoff=st.number_input(tr('Minimum predicted PCE (%)','Minimum proqnoz PCE (%)','Минимальный прогноз PCE (%)'),value=0.0);n=st.slider(tr('Maximum displayed candidates','Maksimum göstərilən namizəd sayı','Максимум отображаемых кандидатов'),10,500,100);df=df[df.PCE_pred>=cutoff].sort_values('PCE_pred',ascending=False).head(n);st.session_state['report_screen']=df.copy();st.session_state['report_source']=mode;st.dataframe(df,hide_index=True);st.download_button(tr('Download ranked CSV','Sıralanmış CSV-ni endir','Скачать CSV рейтинга'),df.to_csv(index=False),'ranked_candidates.csv','text/csv')
else:
    st.subheader(tr('Held-out evaluation · 7,500 molecules','Yekun test · 7 500 molekul','Отложенный тест · 7500 молекул'));st.dataframe(table('app_test_metrics.csv'),hide_index=True)
    import json
    sm=json.loads((ROOT/'data/screening_metrics.json').read_text());a,b,c=st.columns(3);a.metric('Precision@100',f'{sm["top_k_precision_reference_top_decile"]:.0%}');b.metric(tr('Top 100 mean reference PCE','Top 100 orta referens PCE','Средний эталонный PCE топ-100'),f'{sm["mean_reference_PCE_top"]:.2f}%');c.metric(tr('All test mean reference PCE','Bütün test üzrə orta referens PCE','Средний эталонный PCE теста'),f'{sm["mean_reference_PCE_all"]:.2f}%')
    st.caption(tr('Precision@100: fraction of predicted top 100 belonging to the reference top decile. Retrospective computed labels, not experimental discovery.','Precision@100: seçilən 100 molekuldan referens üzrə ilk 10%-ə daxil olanların payı. Hesablanmış etiketlər, laboratoriya kəşfi deyil.','Precision@100: доля выбранных 100 молекул в верхних 10% эталона. Расчётные метки, не экспериментальное открытие.'))
    st.subheader(tr('Active learning','Aktiv öyrənmə','Активное обучение'));st.dataframe(table('test_metrics.csv').groupby(['target','strategy']).MAE.agg(['mean','std']).reset_index(),hide_index=True);st.dataframe(table('paired_comparisons.csv'),hide_index=True);st.warning(tr('Quantum hybrid did not meet the 5% improvement criterion; confidence intervals include zero. No quantum advantage established.','Kvant hibridi 5% meyarına çatmadı; etibar intervalları sıfırı əhatə edir. Kvant üstünlüyü təsdiqlənməyib.','Квантовый гибрид не достиг 5%; интервалы включают ноль. Преимущество не доказано.'))
    for pair in [('HOMO','LUMO'),('Energy_Gap','PCE')]:
        for col,t in zip(st.columns(2),pair):col.image(str(ROOT/f'data/app_{t}_scatter.png'))
    st.markdown('**Method:** 21 RDKit descriptors + 2,048 Morgan bits; three XGBoost models per target. Gap derived from predicted LUMO − HOMO. Training: 35,031; calibration: 7,469; test: 7,500; generic scaffolds disjoint. [CEPDB dataset mirror](https://huggingface.co/datasets/Tommy-DING/organic-solar-cell-molecule-property-prediction).')

with st.sidebar:
    st.divider()
    st.caption(tr('Full report uses the last valid molecule and last displayed screening selection; defaults to reference candidate #1 and time 1 if not selected.','Hesabat son etibarlı molekulu və son seçim siyahısını istifadə edir. İlkin nümunə: 1-ci namizəd, zaman 1.','Отчёт использует последнюю допустимую молекулу и список отбора. По умолчанию кандидат №1 и время 1.'))
    if st.button(tr('Prepare scientific report','Elmi hesabatı hazırla','Подготовить научный отчёт')):
        try:
            rm=molecule(st.session_state.get('report_smiles',rank.iloc[0].Canonical_SMILES)); rc=Chem.MolToSmiles(rm)
            wc,wt,ws=st.session_state.get('report_walk',('',1.,0))
            if wc!=rc:wt,ws=1.,0
            st.session_state['report_pdf']=build_report(rm,known.get(rc,'not found'),wt,ws,st.session_state.get('report_screen'),st.session_state.get('report_source','Held-out reference candidates'))
        except Exception as e:st.error(f'Report generation failed: {e}')
    if 'report_pdf' in st.session_state:
        st.download_button(tr('Download Full Scientific Report','Tam elmi hesabatı endir','Скачать полный научный отчёт'),st.session_state['report_pdf'],'QuantumMatter_Scientific_Report.pdf','application/pdf')
        st.caption(tr('Prepare again after changing inputs to refresh the PDF.','Girişləri dəyişdikdən sonra PDF-i yenidən hazırla.','После изменения входов подготовьте PDF заново.'))
