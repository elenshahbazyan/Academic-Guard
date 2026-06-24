# app.py  ← Run: streamlit run app.py

import streamlit as st
import time
from orchestrator import Orchestrator
from utils.data_loader import load_dataset
from agents.agent2_expert import ExpertSystemAgent

st.set_page_config(
    page_title="AcademicGuard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;500;600;700&display=swap');

* { font-family: 'Nunito', sans-serif; }
html, body, .stApp, .main { background: #f0f4f8 !important; }
.block-container { padding: 1.5rem 2.5rem; max-width: 1400px; }
#MainMenu, footer, header, .stDeployButton { visibility: hidden; }

/* Top bar */
.topbar {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 18px;
    padding: 1.4rem 2rem;
    margin-bottom: 1.8rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.topbar-title { font-size: 1.4rem; font-weight: 700; color: white; }
.topbar-sub   { font-size: 13px; color: rgba(255,255,255,0.75); margin-top: 3px; }
.topbar-stat  { text-align: center; }
.topbar-stat-val { font-size: 1.4rem; font-weight: 700; color: white; }
.topbar-stat-lbl { font-size: 11px; color: rgba(255,255,255,0.65); margin-top: 2px; }

/* Cards */
.card {
    background: white;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
    border: 1px solid rgba(255,255,255,0.8);
}
.card-title {
    font-size: 13px;
    font-weight: 700;
    color: #4a5568;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 7px;
}

/* Preset buttons */
.preset-row { display: flex; gap: 10px; margin-bottom: 1rem; }
.stButton > button {
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 0.45rem 1rem !important;
    border: 1.5px solid !important;
    transition: all 0.15s !important;
    width: 100% !important;
}

/* Analyze button */
.analyze-btn > button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-size: 15px !important;
    padding: 0.75rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 15px rgba(102,126,234,0.4) !important;
}
.analyze-btn > button:hover {
    box-shadow: 0 6px 20px rgba(102,126,234,0.55) !important;
    transform: translateY(-1px) !important;
}

/* Number inputs */
div[data-testid="stNumberInput"] input {
    border-radius: 10px !important;
    border: 1.5px solid #e2e8f0 !important;
    background: #f8fafc !important;
    font-size: 14px !important;
    color: #2d3748 !important;
}
div[data-testid="stNumberInput"] input:focus {
    border-color: #667eea !important;
    background: white !important;
    box-shadow: 0 0 0 3px rgba(102,126,234,0.15) !important;
}

.stSelectbox > div > div {
    border-radius: 10px !important;
    border: 1.5px solid #e2e8f0 !important;
    background: #f8fafc !important;
}
.stTextInput > div > div > input {
    border-radius: 10px !important;
    border: 1.5px solid #e2e8f0 !important;
    background: #f8fafc !important;
}

/* Labels */
label { font-size: 13px !important; font-weight: 600 !important; color: #4a5568 !important; }

/* Result cards */
.result-card {
    background: white;
    border-radius: 18px;
    padding: 1.5rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07);
    border: 1px solid rgba(255,255,255,0.9);
    height: 100%;
}
.agent-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #f0f4f8;
    border-radius: 20px;
    padding: 4px 12px 4px 6px;
    font-size: 12px;
    font-weight: 600;
    color: #4a5568;
    margin-bottom: 1rem;
}
.agent-dot {
    width: 22px; height: 22px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px;
}

/* Big score */
.big-score {
    font-size: 3.5rem;
    font-weight: 800;
    letter-spacing: -0.05em;
    line-height: 1;
}
.score-label { font-size: 13px; color: #a0aec0; margin-top: 5px; }

/* Score bar */
.sbar-bg { background: #edf2f7; border-radius: 8px; height: 10px; margin: 12px 0 16px; overflow: hidden; }
.sbar-fill { height: 100%; border-radius: 8px; }

/* Feature rows */
.feat { display:flex; align-items:center; gap:10px; margin-bottom:9px; }
.feat-name { font-size:12px; color:#718096; flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.feat-val  { font-size:12px; font-weight:700; color:#2d3748; min-width:24px; text-align:right; }
.fbar-bg   { width:70px; background:#edf2f7; border-radius:4px; height:5px; flex-shrink:0; }
.fbar-fill { height:100%; border-radius:4px; background:#667eea; }

/* Rule pills */
.rule {
    border-radius: 10px;
    padding: 9px 12px;
    margin-bottom: 7px;
    border-left: 3px solid;
}
.rule-CRITICAL { background:#fff5f5; border-color:#fc8181; }
.rule-HIGH     { background:#fffaf0; border-color:#f6ad55; }
.rule-MEDIUM   { background:#fffff0; border-color:#f6e05e; }
.rule-LOW      { background:#f0fff4; border-color:#68d391; }
.rule-name-CRITICAL { font-size:13px; font-weight:700; color:#c53030; }
.rule-name-HIGH     { font-size:13px; font-weight:700; color:#c05621; }
.rule-name-MEDIUM   { font-size:13px; font-weight:700; color:#b7791f; }
.rule-name-LOW      { font-size:13px; font-weight:700; color:#276749; }
.rule-msg { font-size:12px; color:#718096; margin-top:2px; }

/* Step cards */
.step {
    background: #f8fafc;
    border-radius: 12px;
    padding: 11px 13px;
    margin-bottom: 8px;
    display: flex;
    gap: 11px;
    align-items: flex-start;
    border: 1px solid #e2e8f0;
}
.step-n {
    width: 26px; height: 26px; border-radius: 50%;
    background: linear-gradient(135deg,#667eea,#764ba2);
    color: white; font-size: 12px; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.step-act  { font-size: 13px; font-weight: 600; color: #2d3748; }
.step-when { font-size: 11px; color: #a0aec0; margin-top: 3px; }

/* Summary */
.summary {
    background: linear-gradient(135deg, #ebf8ff, #e9d8fd);
    border-radius: 12px;
    padding: 12px 14px;
    font-size: 13px;
    color: #2c5282;
    line-height: 1.65;
    margin-bottom: 12px;
    border: 1px solid rgba(102,126,234,0.2);
}

/* Student message */
.stu-msg {
    background: linear-gradient(135deg, #f0fff4, #e6fffa);
    border-radius: 12px;
    padding: 14px 16px;
    font-size: 14px;
    color: #276749;
    line-height: 1.7;
    font-style: italic;
    border: 1px solid rgba(104,211,145,0.3);
}

/* Final banner */
.final-banner {
    background: white;
    border-radius: 18px;
    padding: 1.4rem 1.8rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07);
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.2rem;
    border: 1px solid rgba(255,255,255,0.9);
}

/* Badges */
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.badge-LOW      { background:#f0fff4; color:#276749; border:1.5px solid #9ae6b4; }
.badge-MEDIUM   { background:#fffaf0; color:#c05621; border:1.5px solid #fbd38d; }
.badge-HIGH     { background:#fffaf0; color:#c05621; border:1.5px solid #f6ad55; }
.badge-CRITICAL { background:#fff5f5; color:#c53030; border:1.5px solid #fc8181; }

/* Alert boxes */
.alert-red {
    background: #fff5f5;
    border: 1.5px solid #fc8181;
    border-radius: 12px;
    padding: 11px 15px;
    color: #c53030;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 1rem;
}
.alert-green {
    background: #f0fff4;
    border: 1.5px solid #9ae6b4;
    border-radius: 12px;
    padding: 11px 15px;
    color: #276749;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 1rem;
}

/* Welcome screen */
.welcome {
    background: white;
    border-radius: 18px;
    padding: 4rem 2rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    border: 1px solid rgba(255,255,255,0.9);
}

/* Section divider label */
.divider-label {
    font-size: 11px;
    font-weight: 700;
    color: #a0aec0;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0.3rem 0 0.7rem;
}
</style>
""", unsafe_allow_html=True)


# ── Load system ───────────────────────────────
@st.cache_resource
def load_system():
    orc = Orchestrator()
    df, fc = load_dataset()
    orc.agent1.train(df, fc)
    return orc, df, fc

with st.spinner("Initializing AcademicGuard..."):
    orc, df, fc = load_system()

# ── Top bar ───────────────────────────────────
st.markdown("""
<div class="topbar">
    <div>
        <div class="topbar-title">🎓 AcademicGuard</div>
        <div class="topbar-sub">Multi-Agent System for Early Academic Risk Prediction</div>
    </div>
    <div style="display:flex; gap:2.5rem;">
        <div class="topbar-stat"><div class="topbar-stat-val">4,424</div><div class="topbar-stat-lbl">Real Students</div></div>
        <div class="topbar-stat"><div class="topbar-stat-val">0.93</div><div class="topbar-stat-lbl">AUC Score</div></div>
        <div class="topbar-stat"><div class="topbar-stat-val">36</div><div class="topbar-stat-lbl">Features</div></div>
        <div class="topbar-stat"><div class="topbar-stat-val">3</div><div class="topbar-stat-lbl">AI Agents</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Two-column layout ─────────────────────────
left, right = st.columns([1, 1.9], gap="large")

# ════════════════════════════════════════
# LEFT — Input Panel
# ════════════════════════════════════════
with left:

    # Preset buttons
    st.markdown('<div class="divider-label">Quick Presets</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    preset = None
    with c1:
        if st.button("🔴  Critical", key="p1"): preset = "critical"
    with c2:
        if st.button("🟡  Medium",   key="p2"): preset = "medium"
    with c3:
        if st.button("🟢  Low Risk", key="p3"): preset = "low"

    P = {
        "critical": dict(sid="STU001",s1e=7,s1a=0,s1g=0.0,s1ev=0,s2e=7,s2a=0,s2g=0.0,tu=0,deb=1,sch=0,age=38,adm=95.0,dis=1),
        "medium":   dict(sid="STU002",s1e=6,s1a=2,s1g=11.0,s1ev=4,s2e=6,s2a=3,s2g=10.5,tu=0,deb=1,sch=0,age=25,adm=110.0,dis=0),
        "low":      dict(sid="STU003",s1e=6,s1a=6,s1g=14.5,s1ev=6,s2e=6,s2a=6,s2g=15.0,tu=1,deb=0,sch=1,age=19,adm=160.0,dis=0),
    }
    if preset:
        for k, v in P[preset].items():
            st.session_state[k] = v

    def sv(k, d): return st.session_state.get(k, d)

    # Identity
    st.markdown('<div class="divider-label" style="margin-top:1rem;">Student Identity</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    sid = st.text_input("Student ID", sv("sid","STU_DEMO"), key="sid")
    st.markdown('</div>', unsafe_allow_html=True)

    # Semester 1
    st.markdown('<div class="divider-label">Semester 1 Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    r1, r2 = st.columns(2)
    with r1:
        s1e  = st.number_input("Enrolled courses",   0, 10, sv("s1e",6),  key="s1e")
        s1a  = st.number_input("Approved courses",   0, 10, sv("s1a",3),  key="s1a")
    with r2:
        s1g  = st.number_input("Average grade (0–20)", 0.0, 20.0, float(sv("s1g",10.0)), 0.5, key="s1g")
        s1ev = st.number_input("Evaluations taken",  0, 10, sv("s1ev",4), key="s1ev")
    st.markdown('</div>', unsafe_allow_html=True)

    # Semester 2
    st.markdown('<div class="divider-label">Semester 2 Performance</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    r1, r2 = st.columns(2)
    with r1:
        s2e = st.number_input("Enrolled courses",    0, 10, sv("s2e",6),  key="s2e")
        s2a = st.number_input("Approved courses",    0, 10, sv("s2a",3),  key="s2a")
    with r2:
        s2g = st.number_input("Average grade (0–20)", 0.0, 20.0, float(sv("s2g",10.0)), 0.5, key="s2g")
    st.markdown('</div>', unsafe_allow_html=True)

    # Financial & Background
    st.markdown('<div class="divider-label">Financial & Background</div>', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    r1, r2 = st.columns(2)
    def to_idx(val, yes_first=False):
        s = str(val)
        is_yes = s in ("1", "Yes", "yes")
        if yes_first:
            return 0 if is_yes else 1
        else:
            return 1 if is_yes else 0

    with r1:
        tu  = st.selectbox("Tuition paid?", ["Yes","No"], index=to_idx(sv("tu",1),  yes_first=True), key="tu")
        deb = st.selectbox("Has debt?",     ["No","Yes"], index=to_idx(sv("deb",0), yes_first=False), key="deb")
        sch = st.selectbox("Scholarship?",  ["No","Yes"], index=to_idx(sv("sch",0), yes_first=False), key="sch")
    with r2:
        age = st.number_input("Age at enrollment", 17, 65, int(float(str(sv("age",22)))), key="age")
        adm = st.number_input("Admission grade", 50.0, 200.0, float(str(sv("adm",120.0))), 1.0, key="adm")
        dis = st.selectbox("Displaced student?", ["No","Yes"], index=to_idx(sv("dis",0), yes_first=False), key="dis")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="analyze-btn">', unsafe_allow_html=True)
    analyze = st.button("▶   Analyze Student Now", key="analyze")
    st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════
# RIGHT — Results Panel
# ════════════════════════════════════════
with right:

    if not analyze:
        st.markdown("""
        <div class="welcome">
            <div style="font-size:3.5rem; margin-bottom:1.2rem;">🎓</div>
            <div style="font-size:1.15rem; font-weight:700; color:#2d3748; margin-bottom:10px;">
                Welcome to AcademicGuard
            </div>
            <div style="font-size:14px; color:#718096; max-width:420px; margin:0 auto; line-height:1.8;">
                Enter a student's academic and financial data on the left,
                or choose a quick preset, then click
                <strong style="color:#667eea;">Analyze Student Now</strong>
                to see all 3 agents work in real time.
            </div>
            <div style="display:flex; justify-content:center; gap:1.5rem; margin-top:2.5rem;">
                <div style="background:#f7f3ff; border-radius:14px; padding:1rem 1.4rem; text-align:center; min-width:110px;">
                    <div style="font-size:1.6rem; font-weight:800; color:#667eea;">RF</div>
                    <div style="font-size:11px; color:#a0aec0; margin-top:4px;">Random Forest</div>
                    <div style="font-size:11px; color:#667eea; font-weight:600; margin-top:2px;">Risk Score</div>
                </div>
                <div style="background:#fff8f0; border-radius:14px; padding:1rem 1.4rem; text-align:center; min-width:110px;">
                    <div style="font-size:1.6rem; font-weight:800; color:#ed8936;">ES</div>
                    <div style="font-size:11px; color:#a0aec0; margin-top:4px;">Expert System</div>
                    <div style="font-size:11px; color:#ed8936; font-weight:600; margin-top:2px;">Root Cause</div>
                </div>
                <div style="background:#f0fff4; border-radius:14px; padding:1rem 1.4rem; text-align:center; min-width:110px;">
                    <div style="font-size:1.6rem; font-weight:800; color:#38a169;">LLM</div>
                    <div style="font-size:11px; color:#a0aec0; margin-top:4px;">Language Model</div>
                    <div style="font-size:11px; color:#38a169; font-weight:600; margin-top:2px;">Action Plan</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        # ── Build student dict ─────────────────
        student = {
            "student_id": sid,
            "Curricular_units_1st_sem_enrolled":            s1e,
            "Curricular_units_1st_sem_approved":            s1a,
            "Curricular_units_1st_sem_grade":               s1g,
            "Curricular_units_1st_sem_evaluations":         s1ev,
            "Curricular_units_1st_sem_credited":            0,
            "Curricular_units_1st_sem_without_evaluations": 0,
            "Curricular_units_2nd_sem_enrolled":            s2e,
            "Curricular_units_2nd_sem_approved":            s2a,
            "Curricular_units_2nd_sem_grade":               s2g,
            "Curricular_units_2nd_sem_evaluations":         s1ev,
            "Curricular_units_2nd_sem_credited":            0,
            "Curricular_units_2nd_sem_without_evaluations": 0,
            "Tuition_fees_up_to_date":  1 if tu=="Yes"  else 0,
            "Debtor":                   1 if deb=="Yes" else 0,
            "Scholarship_holder":       1 if sch=="Yes" else 0,
            "Age_at_enrollment":        age,
            "Admission_grade":          adm,
            "Displaced":                1 if dis=="Yes" else 0,
            "Marital_Status":1,"Application_mode":1,"Application_order":1,
            "Course":1,"Previous_qualification_grade":adm,"Nacionality":1,
            "Mothers_qualification":1,"Fathers_qualification":1,
            "Mothers_occupation":1,"Fathers_occupation":1,
            "Gender":1,"International":0,
            "Unemployment_rate":10.8,"Inflation_rate":1.4,"GDP":1.0,
        }

        # ── Run agents with progress ───────────
        prog = st.progress(0, text="🤖  Agent 1: Random Forest is calculating risk score...")
        ml_result = orc.agent1.predict(student)
        time.sleep(0.2)

        prog.progress(34, text="🧠  Agent 2: Expert system is diagnosing root causes...")
        agent2 = ExpertSystemAgent()
        expert_result = agent2.evaluate(student, ml_result)
        time.sleep(0.2)

        prog.progress(67, text="💬  Agent 3: LLM is generating intervention plan...")
        llm_result = orc.agent3.generate(student, ml_result, expert_result)
        prog.progress(100, text="✅  Analysis complete!")
        time.sleep(0.4)
        prog.empty()

        # ── Derive values ──────────────────────
        final_risk = llm_result.get("final_risk", expert_result.risk_category)
        ml_score   = ml_result["risk_score"]
        escalate   = llm_result.get("escalate", False)

        RC = {"LOW":"#38a169","MEDIUM":"#ed8936","HIGH":"#e53e3e","CRITICAL":"#c53030"}
        fc_ = RC.get(final_risk, "#718096")
        mc_ = RC.get(ml_result["verdict"], "#718096")

        # ── Final risk banner ──────────────────
        st.markdown(f"""
        <div class="final-banner">
            <div>
                <div style="font-size:11px; font-weight:700; color:#a0aec0; text-transform:uppercase; letter-spacing:0.07em;">
                    Final Risk Assessment · {sid}
                </div>
                <div style="font-size:2.2rem; font-weight:800; color:{fc_}; letter-spacing:-0.04em; margin-top:4px; line-height:1;">
                    {final_risk}
                    <span style="margin-left:10px;" class="badge badge-{final_risk}">{final_risk}</span>
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:11px; color:#a0aec0; font-weight:600; text-transform:uppercase; letter-spacing:0.06em;">ML Score</div>
                <div style="font-size:2.4rem; font-weight:800; color:{mc_}; letter-spacing:-0.04em; line-height:1.1; margin-top:4px;">
                    {ml_score}<span style="font-size:1rem; font-weight:500; color:#a0aec0;"> /100</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Escalation status ──────────────────
        if escalate:
            st.markdown('<div class="alert-red">🚨 Human advisor escalation recommended — this student needs immediate personal outreach</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-green">✓ No immediate escalation needed — continue monitoring and follow the intervention plan below</div>', unsafe_allow_html=True)

        # ── Three agent result cards ───────────
        st.markdown('<div class="divider-label">Agent Outputs</div>', unsafe_allow_html=True)
        a1, a2, a3 = st.columns(3, gap="small")

        # ── Agent 1 ────────────────────────────
        with a1:
            sc = RC.get(ml_result["verdict"], "#718096")
            st.markdown(f"""
            <div class="result-card">
                <div class="agent-badge">
                    <div class="agent-dot" style="background:#eef2ff; color:#667eea;">🤖</div>
                    Agent 1 · RF
                </div>
                <div style="font-size:11px; color:#a0aec0; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:4px;">Risk Score</div>
                <div class="big-score" style="color:{sc};">{ml_score}</div>
                <div class="score-label">out of 100 &nbsp; <span class="badge badge-{ml_result['verdict']}">{ml_result['verdict']}</span></div>
                <div class="sbar-bg"><div class="sbar-fill" style="width:{ml_score}%;background:{sc};"></div></div>
                <div style="font-size:11px; color:#a0aec0; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:10px;">Key Features</div>
            """, unsafe_allow_html=True)

            for f in ml_result.get("top_factors", [])[:5]:
                name = f["feature"].replace("Curricular_units_","").replace("_"," ")
                pct  = min(int(f["importance"] * 600), 100)
                st.markdown(f"""
                <div class="feat">
                    <div class="feat-name">{name}</div>
                    <div class="fbar-bg"><div class="fbar-fill" style="width:{pct}%;"></div></div>
                    <div class="feat-val">{f['value']}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # ── Agent 2 ────────────────────────────
        with a2:
            ec = RC.get(expert_result.risk_category, "#718096")
            st.markdown(f"""
            <div class="result-card">
                <div class="agent-badge">
                    <div class="agent-dot" style="background:#fff8f0; color:#ed8936;">🧠</div>
                    Agent 2 · Expert
                </div>
                <div style="font-size:11px; color:#a0aec0; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:4px;">Root Cause</div>
                <div class="big-score" style="color:{ec};">{expert_result.risk_category}</div>
                <div class="score-label">{len(expert_result.fired_rules)} rule{"s" if len(expert_result.fired_rules)!=1 else ""} triggered</div>
                <div style="height:10px;"></div>
            """, unsafe_allow_html=True)

            if expert_result.fired_rules:
                for rule in expert_result.fired_rules:
                    st.markdown(f"""
                    <div class="rule rule-{rule.severity}">
                        <div class="rule-name-{rule.severity}">{rule.name}</div>
                        <div class="rule-msg">{rule.message}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="background:#f0fff4; border-radius:10px; padding:14px; color:#276749; font-size:13px; line-height:1.6;">No critical conditions detected. Student profile appears stable.</div>', unsafe_allow_html=True)

            for flag in expert_result.priority_flags:
                st.markdown(f'<div style="font-size:12px; color:#b7791f; margin-top:6px; font-weight:600;">{flag}</div>', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # ── Agent 3 ────────────────────────────
        with a3:
            st.markdown(f"""
            <div class="result-card">
                <div class="agent-badge">
                    <div class="agent-dot" style="background:#f0fff4; color:#38a169;">💬</div>
                    Agent 3 · LLM
                </div>
                <div style="font-size:11px; color:#a0aec0; font-weight:600; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:8px;">Intervention Plan</div>
            """, unsafe_allow_html=True)

            if llm_result.get("summary"):
                st.markdown(f'<div class="summary">{llm_result["summary"]}</div>', unsafe_allow_html=True)

            for step in llm_result.get("interventions", []):
                st.markdown(f"""
                <div class="step">
                    <div class="step-n">{step.get('step','?')}</div>
                    <div>
                        <div class="step-act">{step.get('action','')}</div>
                        <div class="step-when">{step.get('when','')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        # ── Message to student ─────────────────
        if llm_result.get("message_to_student"):
            st.markdown('<div class="divider-label" style="margin-top:1rem;">Message to Student</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="stu-msg">💬 &nbsp; "{llm_result["message_to_student"]}"</div>', unsafe_allow_html=True)

        # ── JSON report ────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("📋  View Full JSON Report"):
            st.json({
                "student_id": sid,
                "agent1": ml_result,
                "agent2": {
                    "risk_category": expert_result.risk_category,
                    "rules_fired": [{"id":r.id,"name":r.name,"severity":r.severity,"message":r.message} for r in expert_result.fired_rules],
                },
                "agent3": llm_result,
                "final": {"final_risk": final_risk, "escalate": escalate}
            })