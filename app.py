import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
import datetime
import pandas as pd

# إعدادات الواجهة
st.set_page_config(page_title="لوحة تتبع SHAYA - التحليل التفاعلي", layout="wide")
st.markdown("<style>h1, h2, h3 { text-align: right; direction: RTL; font-family: 'Cairo', sans-serif; }</style>", unsafe_allow_html=True)

# نظام الحماية (Shaya@102030)
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

# --- شريط جانبي للتحكم ---
st.sidebar.header("📊 مدخلات الرادار")
watched = st.sidebar.text_input("🎯 رموز العملات (مثلاً: BTC, ETH):", value="BTC, ETH, SOL")
# تصحيح السطر المسبب للخطأ (إضافة النقاط الفاصلة بدقة)
tickers = [t.strip().upper() for t in watched.split(",") if t.strip()]

st.title("🧠 عقل SHAYA - رادار التحليل التفاعلي")
st.caption(f"🚀 نظام دراسة البيانات والرسوم التفاعلية: {datetime.datetime.now().strftime('%H:%M:%S')}")
st.markdown("---")

# ─── محرك التحليل والرسوم التفاعلية ───
try:
    if tickers:
        # مكان عرض "خلاصة العقل المركزي" في الأعلى
        verdict_placeholder = st.empty()
        
        # توزيع الرسوم البيانية في أعمدة
        cols = st.columns(len(tickers))
        
        for idx, ticker in enumerate(tickers):
            with cols[idx]:
                # جلب البيانات (سحب بيانات الساعة لآخر 60 يوم)
                symbol = f"{ticker}-USD" if "^" not in ticker else ticker
                data = yf.Ticker(symbol).history(period="60d", interval="1h")
                
                if not data.empty:
                    curr_p = data['Close'].iloc[-1]
                    change = ((curr_p - data['Open'].iloc[-24]) / data['Open'].iloc[-24]) * 100
                    
                    # حساب RSI للتحليل الجانبي
                    delta = data['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]

                    # عرض الأرقام والبيانات الجانبية
                    st.metric(label=f"سعر {ticker}", value=f"${curr_p:,.2f}", delta=f"{change:.2f}%")
                    st.write(f"📈 مؤشر RSI: **{rsi:.1f}**")
                    
                    # الرسم البياني التفاعلي المتطور
                    fig = go.Figure()
                    v_color = "#00ff66" if change > 0 else "#ff3333"
                    
                    fig.add_trace(go.Scatter(
                        x=data.index, 
                        y=data['Close'], 
                        name=ticker, 
                        line=dict(color=v_color, width=2.5)
                    ))
                    
                    # إعدادات التفاعل (Zoom, Pan, Drawing Tools)
                    fig.update_layout(
                        margin=dict(l=0, r=0, t=30, b=0),
                        height=400,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        hovermode="x unified",
                        dragmode="drawline", # تفعيل أداة الرسم فورياً عند الضغط
                        newshape_line_color="#00ccff",
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor="#333")
                    )
                    
                    # تفعيل أدوات الرسم (الخطوط، الدوائر، التكبير)
                    st.plotly_chart(fig, use_container_width=True, config={
                        'scrollZoom': True,
                        'displaylogo': False,
                        'modeBarButtonsToAdd': [
                            'drawline', 'drawcircle', 'drawrect', 'eraseshape'
                        ]
                    })

        # تحديث نص "خلاصة العقل المركزي"
        verdict_placeholder.markdown(f"""
            <div style="background-color: #0d0d0d; border-right: 10px solid #00ff66; padding: 25px; border-radius: 10px; color: #00ff66; text-align: right; direction: rtl; margin-bottom: 20px;">
                <span style="font-size: 24px; font-weight: bold;">[خلاصة العقل المركزي]</span><br>
                تم تفعيل الأدوات التفاعلية بنجاح. يمكنك الآن <b>التكبير</b>، أو استخدام <b>أيقونة القلم</b> في أعلى الرسم لوضع نقاط وخطوط دراستك الخاصة على الشارت.
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"تنبيه: {e}")
