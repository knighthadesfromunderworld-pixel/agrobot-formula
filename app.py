import streamlit as st
import matplotlib.pyplot as plt
from gtts import gTTS
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="Agro Twin Pro", page_icon="🚜", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; border-left: 6px solid #2e7d32; margin-bottom: 20px; }
    .tamil-sub { color: #2e7d32; font-weight: bold; font-size: 1.1em; }
    </style>
    """, unsafe_allow_html=True)

# --- THE ADVANCED FORMULA ENGINE ---
def calculate_suitability(n, p, k, moisture, temp, ph, soil_type):
    # Profiles: [N, P, K, Moisture, Temp, pH, Ideal Soil Type]
    # Soil Types: 0:Sandy, 1:Loamy, 2:Clay, 3:Black
    crop_db = {
        "Teak": {"vals": [40, 20, 30, 35, 28, 7.0, 1], "ta": "தேக்கு மரம்", "cat": "Long Term"},
        "Turmeric": {"vals": [70, 45, 50, 75, 26, 6.5, 2], "ta": "மஞ்சள்", "cat": "Short Term"},
        "Banana": {"vals": [55, 35, 85, 80, 30, 6.5, 1], "ta": "வாழை", "cat": "High Profit"}
    }
    
    results = {}
    for crop, data in crop_db.items():
        ideals = data["vals"]
        
        # 1. Nutrient Score (NPK) - Weighted 40%
        n_score = 100 - (abs(ideals[0] - n) * 1.5)
        p_score = 100 - (abs(ideals[1] - p) * 1.5)
        k_score = 100 - (abs(ideals[2] - k) * 1.5)
        nutri_avg = (n_score + p_score + k_score) / 3
        
        # 2. Environment (Moisture/Temp/pH) - Weighted 40%
        m_score = 100 - (abs(ideals[3] - moisture) * 1.2)
        t_score = 100 - (abs(ideals[4] - temp) * 2.0)
        ph_score = 100 - (abs(ideals[5] - ph) * 20.0)
        env_avg = (m_score + t_score + ph_score) / 3
        
        # 3. Soil Type Compatibility - Weighted 20%
        soil_score = 100 if soil_type == ideals[6] else 40
        
        # Final Formula
        final_score = (nutri_avg * 0.4) + (env_avg * 0.4) + (soil_score * 0.2)
        results[crop] = {
            "score": max(0, min(100, round(final_score, 1))),
            "ta": data["ta"],
            "cat": data["cat"]
        }
    return results

# --- SIDEBAR: ROVER CONTROLS ---
st.sidebar.title("🎮 Rover Telemetry")
st.sidebar.markdown("---")
with st.sidebar:
    st.subheader("Nutrient Levels (mg/kg)")
    n = st.slider("Nitrogen (N)", 0, 100, 45)
    p = st.slider("Phosphorus (P)", 0, 100, 30)
    k = st.slider("Potassium (K)", 0, 100, 50)
    
    st.subheader("Environment")
    ph = st.slider("pH Level", 4.0, 9.0, 6.5)
    temp = st.slider("Temperature °C", 15, 45, 28)
    moisture = st.slider("Moisture %", 0, 100, 40)
    
    soil_map = {"Sandy": 0, "Loamy": 1, "Clay": 2, "Black": 3}
    soil_select = st.selectbox("Observed Soil Type", list(soil_map.keys()))

# --- MAIN DASHBOARD ---
st.title("🛰️ Agro Twin: Advanced Soil Intelligence")
st.write(f"Digital Twin Status: **Connected** | Location: **Kattankulathur, TN**")

scores = calculate_suitability(n, p, k, moisture, temp, ph, soil_map[soil_select])

# TOP METRICS
m1, m2, m3 = st.columns(3)
total_fertility = sum(v["score"] for v in scores.values()) / 3
m1.metric("Global Fertility Index", f"{total_fertility:.1f}%")
m2.metric("Soil Type", soil_select)
m3.metric("pH Balance", ph, delta="Optimal" if 6.0 <= ph <= 7.5 else "Correction Needed")

st.divider()

# RESULTS COLUMNS
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📊 AI Suitability Analysis")
    fig, ax = plt.subplots(figsize=(6, 4))
    # Using dynamic values from the formula for the pie chart
    labels = [f"{c} ({v['score']}%)" for c, v in scores.items()]
    sizes = [v["score"] for v in scores.values()]
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['#2e7d32', '#fbc02d', '#d32f2f'], startangle=140)
    st.pyplot(fig)

with col_right:
    st.subheader("💡 Precision Recommendations")
    
    for crop, info in scores.items():
        st.markdown(f"""
        <div class="card">
            <small>{info['cat']}</small><br>
            <b style='font-size:1.2em;'>{crop}</b> | <span class="tamil-sub">{info['ta']}</span><br>
            Confidence Score: <b>{info['score']}%</b>
        </div>
        """, unsafe_allow_html=True)
    
    # VOICE GENERATION
    if st.button("🔊 Play Voice Advisory"):
        voice_text = f"மண் வளம் {int(total_fertility)} சதவீதம். " + " ".join([f"{v['cat']} பயிர்: {v['ta']}." for v in scores.values()])
        tts = gTTS(text=voice_text, lang='ta')
        tts.save("pro_voice.mp3")
        st.audio("pro_voice.mp3")

# BAR CHART COMPARISON (Live Feedback)
st.divider()
st.subheader("📈 Nutrient Distribution Analysis")
fig2, ax2 = plt.subplots(figsize=(12, 3))
ax2.bar(["Nitrogen", "Phosphorus", "Potassium", "Moisture"], [n, p, k, moisture], color='#1976d2')
ax2.set_ylim(0, 100)
st.pyplot(fig2)
