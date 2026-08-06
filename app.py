import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
import datetime
import pandas as pd

# إعدادات الواجهة
st.set_page_config(page_title="عقل SHAYA - رادار التحليل التفاعلي", layout="wide")
st.markdown("<style>h1, h2, h3 { text-align: right; direction: RTL; font-family: 'Cairo', sans-serif; }</style>", unsafe_allow_html=True)

# نظام الحماية (رقمك السري Shaya@102030)
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.subheader("🔒 تفعيل الرادار المركزي - لوحة SHAYA")
    user = st.text_input("المستخدم:")
    pwd = st.text_input("كلمة المرور:", type="password")
    if st.button("بدء النظام"):
        if user == "shaya" and pwd == "Shaya@102030":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("بيانات غير مصرح بها")
    st.stop()

# تحديث آلي كل 30 ثانية
st_autorefresh(interval=30000, limit=1000, key="shaya_interactive_v17")

# --- شريط جانبي لإدخال البيانات وتحكم العقل ---
st.sidebar.header("📊 مدخلات الرادار")
# يمكنك تغيير الرموز هنا وستظهر لك جميعاً مع رسومها
watched = st.sidebar.text_input("🎯 رموز العملات/المؤشرات:", value="BTC, ETH, ^IXIC")
tickers = [tstrip()upper() for t in watchedsplit(",") if tstrip()]

st.title("🧠 عقل SHAYA - رادار التحليل التفاعلي")
st.caption(f"🚀 النظام يعمل الآن بكامل طاقته البيانية: {datetime.datetime.now().strftime('%H:%M:%S')}")
st.markdown("---")

# ─── محرك التحليل والرسوم التفاعلية ───
try:
    if tickers:
        # عرض "خلاصة العقل المركزي" في الأعلى لتكون واضحة
        verdict_placeholder = st.empty()
        
        # إنشاء الأعمدة للرسوم البيانية والأرقام
        cols = st.columns(len(tickers))
        
        for idx, ticker in enumerate(tickers):
            with cols[idx]:
                data = yf.Ticker(f"{ticker}-USD" if "^" not in ticker else ticker).history(period="60d", interval="1h")
                
                if not data.empty:
                    curr_p = data['Close'].iloc[-]
                    change = ((curr_p - data['Open'].iloc[-]) / data['Open'].iloc[-]) * 100
                    
                    # حساب RSI و MACD في الخلفية
                    delta = data['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-]

                    # عرض الأرقام الجانبية المفقودة
                    st.metric(label=f"السعر الحقيقي {ticker}", value=f"${curr_p:,.2f}", delta=f"{change:.2f}%")
                    st.write(f"📈 RSI: **{rsi:.1f}**")
                    
                    # الرسم البياني التفاعلي (قابل للتكبير وإضافة نقاط)
                    fig = go.Figure()
                    v_color = "#00ff66" if change > 0 else "#ff3333"
                    
                    fig.add_trace(go.Scatter(
                        x=data.index, 
                        y=data['Close'], 
                        name=ticker, 
                        line=dict(color=v_color, width=2)
                    ))
                    
                    # إعدادات التفاعل القصوى (Zoom, Pan, Draw)
                    fig.update_layout(
                        margin=dict(l=0, r=0, t=30, b=0),
                        height=350,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        hovermode="x unified",
                        dragmode="drawopenpath", # تفعيل وضع الرسم اليدوي لإضافة نقاط
                        newshape_line_color=v_color,
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor="#333"),
                        title=dict(text=f"تحليل {ticker}", x=0.5, font=dict(color="white"))
                    )
                    
                    # إضافة ميزة التكبير المباشر (Full Screen Mode متوفر في القائمة العلوية للرسم)
                    st.plotly_chart(fig, use_container_width=True, config={
                        'scrollZoom': True,           # التكبير عبر بكرة الفأرة
                        'displaylogo': False,
                        'modeBarButtonsToAdd': [
                            'drawline', 'drawcircle', 'eraseshape' # أدوات رسم النقاط والدوائر للدراسة
                        ]
                    })

        # تحديث "خلاصة العقل المركزي" بناءً على البيانات المسحوبة
        with verdict_placeholder:
            st.markdown(f"""
                <div style="background-color: #0d0d0d; border-right: 10px solid #00ff66; padding: 20px; border-radius: 10px; color: #00ff66; text-align: right; direction: rtl; margin-bottom: 20px;">
                    <span style="font-size: 24px; font-weight: bold;">[خلاصة العقل المركزي]</span><br>
                    تم إعادة تفعيل الأرقام الجانبية وأدوات الرسم التفاعلي. يمكنك الآن استخدام "شريط الأدوات" فوق كل رسم لتكبيره أو وضع نقاط دراسة.
                </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"جاري سحب البيانات.. {e}")
