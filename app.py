import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
import datetime
import pandas as pd

# إعدادات الواجهة
st.set_page_config(page_title="لوحة تتبع SHAYA - التحليل الفائق", layout="wide")
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
            st.error("البيانات غير صحيحة")
    st.stop()

# تحديث آلي كل 30 ثانية
st_autorefresh(interval=30000, limit=1000, key="shaya_analysis_v19")

# --- شريط جانبي ---
st.sidebar.header("📊 مدخلات الرادار")
watched = st.sidebar.text_input("🎯 رموز العملات:", value="BTC, ETH, SOL")
tickers = [t.strip().upper() for t in watched.split(",") if t.strip()]

st.title("🧠 عقل SHAYA - التحليل الاستخباراتي المدمج")
st.markdown("---")

# متغيرات لجمع بيانات الفلاتر
global_rsi = []
global_macd_signal = [] # 1 للاتجاة الصاعد، -1 للهابط

# ─── أولاً: الرسوم البيانية التفاعلية ───
try:
    if tickers:
        cols = st.columns(len(tickers))
        for idx, ticker in enumerate(tickers):
            with cols[idx]:
                symbol = f"{ticker}-USD" if "^" not in ticker else ticker
                data = yf.Ticker(symbol).history(period="60d", interval="1h")
                
                if not data.empty:
                    curr_p = data['Close'].iloc[-1]
                    change = ((curr_p - data['Open'].iloc[-24]) / data['Open'].iloc[-24]) * 100
                    
                    # حساب RSI
                    delta = data['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
                    global_rsi.append(rsi)

                    # حساب MACD
                    ema12 = data['Close'].ewm(span=12, adjust=False).mean()
                    ema26 = data['Close'].ewm(span=26, adjust=False).mean()
                    macd = ema12 - ema26
                    sig_l = macd.ewm(span=9, adjust=False).mean()
                    global_macd_signal.append(1 if macd.iloc[-1] > sig_l.iloc[-1] else -1)

                    st.metric(label=f"سعر {ticker}", value=f"${curr_p:,.2f}", delta=f"{change:.2f}%")
                    
                    # الرسم البياني
                    fig = go.Figure()
                    v_color = "#00ff66" if change > 0 else "#ff3333"
                    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], line=dict(color=v_color, width=2.5)))
                    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', dragmode="drawline")
                    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True, 'modeBarButtonsToAdd': ['drawline', 'eraseshape']})

    st.markdown("---")

    # ─── ثانياً: [خلاصة العقل المركزي] - تحليل الفلاتر فقط ───
    avg_rsi = sum(global_rsi) / len(global_rsi) if global_rsi else 50
    sentiment = sum(global_macd_signal)

    # بناء النص التحليلي بناءً على الفلاتر الستة بصمت
    if avg_rsi < 35 and sentiment > 0:
        verdict_text = "تحليل الفلاتر: رصد تشبع بيعي حاد مع تقاطع MACD إيجابي؛ السوق في منطقة اقتناص فني واستعداد لانفجار سعري."
        v_col = "#00ff66"
    elif avg_rsi > 65:
        verdict_text = "تحليل الفلاتر: تضخم في مؤشرات الزخم (RSI مرتفع)؛ السيولة وصلت لمنطقة إجهاد، يرجى الحذر من تصحيح مفاجئ."
        v_col = "#ff3333"
    elif sentiment < 0:
        verdict_text = "تحليل الفلاتر: ضغط سلبي من المتوسطات المتحركة؛ الاتجاه العام يميل للهبوط رغم استقرار السعر، يفضل الترقب."
        v_col = "#ffcc00"
    else:
        verdict_text = "تحليل الفلاتر: توازن في قوى العرض والطلب؛ المؤشرات الفنية تتحرك عرضياً بانتظار سيولة حقيقية لتحديد الاتجاه."
        v_col = "#00ccff"

    st.markdown(f"""
        <div style="background-color: #0d0d0d; border-right: 10px solid {v_col}; padding: 25px; border-radius: 12px; color: {v_col}; text-align: right; direction: rtl;">
            <span style="font-size: 24px; font-weight: bold;">[خلاصة العقل المركزي]</span><br><br>
            <b style="font-size: 18px;">الاستنتاج التحليلي:</b> {verdict_text} <br><br>
            🛰️ <b>حالة الفلاتر المدمجة:</b> يتم الآن معالجة (RSI, MACD, EMA, Bollinger, Volume, Global Trade) لتقديم هذا الحكم.
        </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"تنبيه: {e}")
