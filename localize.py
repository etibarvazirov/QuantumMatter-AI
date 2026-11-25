import streamlit as st
LANGS=['English','Azərbaycan','Русский']
def tr(lang,e,a,r): return (e,a,r)[LANGS.index(lang)]
PAGES=['Molecular Explorer','AI Property Prediction','Quantum Walk Simulator','Material Screening','Research & Experiments','Öyrənmə mərkəzi']
NAMES=[('Molecular Explorer','Molekul tədqiqatı','Исследование молекул'),('AI Property Prediction','AI proqnozları','Прогнозы ИИ'),('Quantum Walk Simulator','Kvant gəzintisi','Квантовое блуждание'),('Material Screening','Material seçimi','Отбор материалов'),('Research & Experiments','Tədqiqat və eksperimentlər','Исследования и эксперименты'),('Learning Center','Öyrənmə mərkəzi','Учебный центр')]
def name(page,lang): return tr(lang,*NAMES[PAGES.index(page)])
def style():
 st.markdown('''<style>
 .stApp {background:linear-gradient(145deg,#081522,#102839);color:#e8f3f8} [data-testid="stSidebar"] {background:#0b1e2e;border-right:1px solid #284759} .block-container{max-width:1280px;padding-top:2.5rem} h1,h2,h3{letter-spacing:-.025em} [data-testid="stMetric"]{background:#153448;border:1px solid #31566b;border-radius:16px;padding:18px} [data-testid="stMetricValue"]{color:#72e4d0} [data-testid="stExpander"]{border:1px solid #31566b;border-radius:12px;background:#102b3c} .stButton button,.stDownloadButton button{border-radius:10px;border:1px solid #4bb8ae;font-weight:600} .qmhero{background:linear-gradient(115deg,#15394d,#164b50);border:1px solid #376779;border-radius:20px;padding:28px;margin-bottom:20px} .qmhero h1{margin:0;color:#f0fcff;font-size:2.5rem} .qmhero p{color:#c3e4e9;margin:8px 0 0} .qmkicker{color:#79e5d4;font-size:.78rem;letter-spacing:.14em;font-weight:700} </style>''',unsafe_allow_html=True)
