import streamlit as st
LANGS=['English','Azərbaycan','Русский']
def tr(lang,e,a,r): return (e,a,r)[LANGS.index(lang)]
PAGES=['Molecular Explorer','AI Property Prediction','Quantum Walk Simulator','Material Screening','Research & Experiments','Öyrənmə mərkəzi']
NAMES=[('Molecular Explorer','Molekul tədqiqatı','Исследование молекул'),('AI Property Prediction','AI proqnozları','Прогнозы ИИ'),('Quantum Walk Simulator','Kvant gəzintisi','Квантовое блуждание'),('Material Screening','Material seçimi','Отбор материалов'),('Research & Experiments','Tədqiqat və eksperimentlər','Исследования и эксперименты'),('Learning Center','Öyrənmə mərkəzi','Учебный центр')]
def name(page,lang): return tr(lang,*NAMES[PAGES.index(page)])
def style():
    # Native Streamlit theme controls widget surfaces and text together.
    # Custom CSS is restricted to decorative elements with explicit colors.
    st.markdown("""<style>
    .block-container {max-width:1280px;padding-top:2.5rem}
    [data-testid="stMetric"] {border:1px solid #31566b;border-radius:16px;padding:18px}
    [data-testid="stExpander"] {border-radius:12px}
    .qmhero {background:linear-gradient(115deg,#15394d,#164b50);border:1px solid #376779;border-radius:20px;padding:28px;margin-bottom:20px}
    .qmhero h1 {margin:0;color:#f0fcff !important;font-size:2.5rem}
    .qmhero p {color:#e1f2f5 !important;margin:8px 0 0}
    .qmkicker {color:#a5f3e8;font-size:.78rem;letter-spacing:.14em;font-weight:700}
    </style>""",unsafe_allow_html=True)
