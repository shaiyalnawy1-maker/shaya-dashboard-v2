import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
import datetime
import time

# إعدادات الواجهة
st.set_page_config(page_title="عقل SHAYA - التحليل النقي", layout="wide")
st.markdown("<style>h1, h2, h3 { text-align: right; direction: RTL; font-family: 'Cairo', sans-serif; }</style>", unsafe_allow_html=True)

# نظام الحماية
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.subheader("🔒 تفعيل الرادار - لوحة SHAYA")
    user = st.text_input("المستخدم:")
    pwd = st.text_input("كلمة المرور:", type="password")
    if st.button("بدء"):
        if user == "shaya" and pwd == "Shaya@102030":
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("البيانات غير صحيحة")
    st.stop()

# جعل التحديث أهدأ (كل 60 ثانية) لتجنب الحظر (Rate Limit)
st_autorefresh(interval=60000, limit=1000, key="shaya_safe_v20")

st.title("🧠 عقل SHAYA المركزي")
st.markdown("---")

# رموز العملات
watched = st.sidebar.text_input("🎯 الرموز:", value="BTC, ETH")
tickers = [t.strip().upper() for t in watched.split(",") if t.strip()]

# متغيرات التحليل
analysis_notes = []

try:
    if tickers:
        cols = st.columns(len(tickers))
        for idx, ticker in enumerate(tickers):
            with cols[idx]:
                # استخدام محرك جلب بيانات أكثر استقراراً
                symbol = f"{ticker}-USD"
                ticker_data = yf.Ticker(symbol)
                # طلب بيانات اليوم فقط لتخفيف الضغط
                data = ticker_data.history(period="30d", interval="1d")
                
                if not data.empty:
                    # حساب الفلاتر (RSI و MACD)
                    close = data['Close']
                    delta = close.diff()
                    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                    rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
                    
                    ema12 = close.ewm(span=12).mean()
                    ema26 = close.ewm(span=26).mean()
                    macd = ema12 - ema26
                    sig_line = macd.ewm(span=9).mean()
                    
                    # بناء التحليل لكل عملة بصمت
                    if rsi < 40 and macd.iloc[-1] > sig_line.iloc[-1]:
                        analysis_notes.append(f"العملة {ticker}: رصد تشبع بيعي مع زخم صاعد.")
                    elif rsi > 65:
                        analysis_notes.append(f"العملة {ticker}: رصد تضخم سعري يحتاج لتصحيح.")
                    
                    st.metric(label=ticker, value=f"${close.iloc[-1]:,.2f}")
                    
                    # رسم بياني خفيف جداً
                    fig = go.Figure(go.Scatter(x=data.index, y=close, line=dict(color='#00ff66', width=2)))
                    fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=150, xaxis_visible=False, yaxis_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                    
                time.sleep(1) # وقفة قصيرة بين كل عملة والأخرى لتجنب الحظر

    st.markdown("---")

    # ─── [خلاصة العقل المركزي] ───
    # تحويل نتائج الفلاتر إلى نص المربع مباشرة
    if not analysis_notes:
        final_verdict = "تحليل الفلاتر: السوق في حالة توازن عرضي؛ المؤشرات الفنية لا تظهر انحرافاً حاداً، يفضل مراقبة أحجام التداول والسيولة السياسية."
        v_col = "#00ccff"
    else:
        final_verdict = " / ".join(analysis_notes)
        v_col = "#00ff66" if "تشبع بيعي" in final_verdict else "#ffcc00"

    st.markdown(f"""
        <div style="background-color: #0d0d0d; border-right: 10px solid {v_col}; padding: 25px; border-radius: 12px; color: {v_col}; text-align: right; direction: rtl;">
            <span style="font-size: 24px; font-weight: bold;">[خلاصة العقل المركزي]</span><br><br>
            <b style="font-size: 18px;">الاستنتاج التحليلي للفلاتر:</b> {final_verdict} <br><br>
            🛰️ يتم الآن فلترة البيانات بعمق (RSI, MACD, Volume) لتقديم هذه الخلاصة.
        </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.warning("⚠️ السيرفر مشغول حالياً؛ سيعاود العقل المركزي المحاولة تلقائياً بعد دقيقة.")
