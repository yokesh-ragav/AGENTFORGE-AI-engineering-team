import streamlit as st
import subprocess
import sys
import os
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AgentForge | AI Engineering Team",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #070b14 0%, #0d1220 50%, #111827 100%);
        color: #f8fafc;
    }

    .hero {
        padding: 35px 10px 20px 10px;
        text-align: center;
    }

    .hero-title {
        font-size: 52px;
        font-weight: 800;
        letter-spacing: -2px;
        margin-bottom: 5px;
    }

    .hero-subtitle {
        font-size: 19px;
        color: #94a3b8;
    }

    .pipeline {
        text-align: center;
        padding: 18px;
        margin: 20px 0;
        border: 1px solid #263247;
        border-radius: 16px;
        background: rgba(15, 23, 42, 0.7);
        font-size: 18px;
        font-weight: 600;
    }

    .agent-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid #263247;
        border-radius: 16px;
        padding: 20px;
        min-height: 145px;
        margin-bottom: 15px;
    }

    .agent-icon {
        font-size: 30px;
    }

    .agent-name {
        font-size: 20px;
        font-weight: 700;
        margin-top: 8px;
    }

    .agent-desc {
        color: #94a3b8;
        font-size: 14px;
        margin-top: 6px;
    }

    .status {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        margin-top: 10px;
        background: #172033;
        color: #94a3b8;
    }

    .metric-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid #263247;
        border-radius: 14px;
        padding: 18px;
        text-align: center;
    }

    .metric-number {
        font-size: 30px;
        font-weight: 800;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 13px;
    }

    .footer {
        text-align: center;
        color: #64748b;
        padding: 30px;
        font-size: 13px;
    }

    div[data-testid="stTextArea"] textarea {
        background-color: #0f172a;
        color: white;
        border: 1px solid #334155;
        border-radius: 12px;
    }

    .stButton button {
        width: 100%;
        border-radius: 12px;
        height: 48px;
        font-weight: 700;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- HERO ----------------
st.markdown("""
<div class="hero">
    <div class="hero-title">⚡ AGENTFORGE</div>
    <div class="hero-subtitle">
        Autonomous AI Engineering Team
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="pipeline">
    💡 Requirement &nbsp;→&nbsp;
    🧠 Plan &nbsp;→&nbsp;
    💻 Build &nbsp;→&nbsp;
    🧪 Test &nbsp;→&nbsp;
    🔧 Repair &nbsp;→&nbsp;
    🚀 Deploy
</div>
""", unsafe_allow_html=True)


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🎯 Engineering Mission")

    requirement = st.text_area(
        "Describe the application you want to build",
        value="Build a smart home automation coordinator with a dashboard for controlling devices and monitoring their status.",
        height=180
    )

    start = st.button(
        "⚡ START ENGINEERING TEAM",
        type="primary"
    )

    st.markdown("---")

    st.markdown("### 🧩 AI Team")
    st.markdown("🧠 **Planner** — Architecture & strategy")
    st.markdown("💻 **Coder** — Application generation")
    st.markdown("🧪 **Tester** — Browser testing")
    st.markdown("🔧 **Repair** — Failure recovery")
    st.markdown("🚀 **Deployment** — Final delivery")


# ---------------- AGENT CARDS ----------------
st.markdown("## 🤖 Engineering Team")

cols = st.columns(5)

agents = [
    ("🧠", "Planner", "Analyzes requirements and creates the engineering plan."),
    ("💻", "Coder", "Generates the application source code."),
    ("🧪", "Tester", "Executes AI-generated browser workflows."),
    ("🔧", "Repair", "Analyzes failures and fixes the application."),
    ("🚀", "Deployment", "Packages the completed application for delivery.")
]

for col, (icon, name, desc) in zip(cols, agents):
    with col:
        st.markdown(f"""
        <div class="agent-card">
            <div class="agent-icon">{icon}</div>
            <div class="agent-name">{name}</div>
            <div class="agent-desc">{desc}</div>
            <div class="status">● Ready</div>
        </div>
        """, unsafe_allow_html=True)


# ---------------- EXECUTION ----------------
if start:

    st.markdown("## ⚙️ Live Engineering Pipeline")

    progress = st.progress(0)

    status_box = st.empty()

    log_box = st.empty()

    logs = []

    status_box.info("🚀 Starting autonomous engineering team...")

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    process = subprocess.Popen(
        [sys.executable, "team.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        bufsize=1
    )

    try:
        process.stdin.write(requirement)
        process.stdin.close()
    except Exception:
        pass

    stage_progress = {
        "PLANNER": 20,
        "CODER": 40,
        "TESTER": 60,
        "REPAIR": 75,
        "DEPLOY": 100
    }

    while True:

        line = process.stdout.readline()

        if line:
            line = line.rstrip()
            logs.append(line)

            upper = line.upper()

            for stage, value in stage_progress.items():
                if stage in upper:
                    progress.progress(value)

                    if stage == "PLANNER":
                        status_box.info("🧠 Planner is designing the system...")
                    elif stage == "CODER":
                        status_box.info("💻 Coder is building the application...")
                    elif stage == "TESTER":
                        status_box.info("🧪 Tester is executing browser tests...")
                    elif stage == "REPAIR":
                        status_box.warning("🔧 Repair Agent is fixing detected failures...")
                    elif stage == "DEPLOY":
                        status_box.success("🚀 Deployment stage reached!")

            log_box.code(
                "\n".join(logs[-25:]),
                language="text"
            )

        elif process.poll() is not None:
            break

        time.sleep(0.05)

    progress.progress(100)

    if process.returncode == 0:
        status_box.success(
            "✅ Engineering team completed successfully!"
        )
    else:
        status_box.warning(
            "⚠️ Engineering pipeline finished with issues. "
            "Review the execution log below."
        )

    st.markdown("## 📊 Engineering Result")

    m1, m2, m3 = st.columns(3)

    with m1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-number">5</div>
            <div class="metric-label">AI Agents</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-number">∞</div>
            <div class="metric-label">Feedback Loop</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-number">AI</div>
            <div class="metric-label">Browser Testing</div>
        </div>
        """, unsafe_allow_html=True)

    # Show generated application if available
    html_path = os.path.join("generated_app", "index.html")

    if os.path.exists(html_path):

        st.markdown("## 🌐 Generated Application")

        try:
            with open(html_path, "r", encoding="utf-8") as f:
                html = f.read()

            st.components.v1.html(
                html,
                height=700,
                scrolling=True
            )

        except Exception as e:
            st.error(f"Could not preview generated application: {e}")


# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
    AGENTFORGE 2026 · Self-Organizing AI Engineering Team
    <br>
    Planner · Coder · Tester · Repair · Deployment
</div>
""", unsafe_allow_html=True)