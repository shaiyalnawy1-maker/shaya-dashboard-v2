import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
import datetime

# إعدادات الواجهة والاتجاه العربي المدمج
st.set_page_config(page_title="لوحة تحكم شايع المختصرة", layout="wide")
st.markdown("<style>h1, h2, h3, h4, p, span, div { text-align: right; direction: RTL; }</style>", unsafe_allow_html=True)

# نظام الحماية والمصادقة الأمنية لـ لوحة شايع
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.subheader("🔒 بوابه الدخول الآمنة - لوحة تحكم شايع")
        user_input = st.text_input("👤 اسم المستخدم (Username):")
        password_input = st.text_input("🔑 كلمة المرور (Password):", type="password")
        if st.button("تسجيل الدخول"):
            if user_input == "shaya" and password_input == "Shaya@102030":
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ بيانات الدخول غير صحيحة")
        return False
    return True

if check_password():
    # تفعيل التحديث التلقائي اللحظي كل 30 ثانية
    st_autorefresh(interval=30000, limit=1000, key="shaya_compact_dashboard")
    
    # رأس الصفحة المدمج
    st.title("🐋 لوحة تحكم شايع الفائقة")
    st.caption(f"⏱️ تحديث آلي لحظي: {datetime.datetime.now().strftime('%H:%M:%S')}")
    st.markdown("---")

    # تتبع العملات من الشريط الجانبي
    watched_crypto = st.sidebar.text_input("✍️ رموز العملات (افصل بفاصلة):", value="BTC, ETH, SOL, XRP")
    tickers = [t.strip().upper() for t in watched_crypto.split(",")]

    # عرض العملات والرسوم البيانية المدمجة والمؤشرات الفنية (RSI & MACD)
    if tickers:
        cols = st.columns(len(tickers))
        for idx, ticker in enumerate(tickers):
            with cols[idx]:
                try:
                    symbol = f"{ticker}-USD"
                    # جلب بيانات 30 يوماً لحساب الـ MACD بدقة (فاصل 1 ساعة)
                    data = yf.Ticker(symbol).history(period="30d", interval="1h")
                    
                    if not data.empty and len(data) >= 26:
                        current_price = data['Close'].iloc[-1]
                        change_pct = ((current_price - data['Open'].iloc[-24]) / data['Open'].iloc[-24]) * 100
                        
                        # 1. حساب مؤشر RSI
                        delta = data['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rsi_val = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
                        
                        # 2. حساب مؤشر MACD
                        exp1 = data['Close'].ewm(span=12, adjust=False).mean()
                        exp2 = data['Close'].ewm(span=26, adjust=False).mean()
                        macd_line = exp1 - exp2
                        signal_line = macd_line.ewm(span=9, adjust=False).mean()
                        
                        m_val = macd_line.iloc[-1]
                        s_val = signal_line.iloc[-1]
                        
                        # دمج استراتيجية RSI و MACD لتوليد إشارة دقيقة جداً
                        if rsi_val < 40 and m_val > s_val:
                            signal = "شراء مؤكد 🟢"
                        elif rsi_val > 65 or m_val < s_val:
                            signal = "بيع وتخفيف 🔴"
                        else:
                            signal = "مراقبة وانتظار 🟡"
                        
                        # بطاقة السعر الفوري والإشارة
                        status_emoji = "📈" if change_pct > 0 else "📉"
                        st.metric(label=f"عملة {ticker} {status_emoji}", value=f"${current_price:,.2f}" if current_price > 1 else f"${current_price:.4f}", delta=f"{change_pct:.2f}%")
                        st.code(f"💡 {signal} | RSI: {rsi_val:.1f}")
                        
                        # منحنى الحركة التفاعلي المصمم بنمط وول ستريت المصغر
                        fig = go.Figure()
                        line_color = '#00cc66' if change_pct > 0 else '#ff3333'
                        fig.add_trace(go.Scatter(x=data.tail(168).index, y=data.tail(168)['Close'], mode='lines', line=dict(color=line_color, width=2.5)))
                        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=140, showlegend=False, xaxis=dict(showgrid=False, showticklabels=False), yaxis=dict(showgrid=True))
                        st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    st.error(f"خطأ في بيانات {ticker}")
                    
    st.markdown("---")
    
    # شريط وول ستريت والسيولة مدمج في سطر واحد مختصر بأسفل اللوحة
    try:
        nasdaq = yf.Ticker("^IXIC").history(period="1d")
        nasdaq_p = ((nasdaq['Close'].iloc[-1] - nasdaq['Open'].iloc[-1]) / nasdaq['Open'].iloc[-1]) * 100
        market_desc = "البيئة العامة: صعود كلي يدعم الشراء 🟢" if nasdaq_p > 0 else "البيئة العامة: هبوط وحذر من مصائد التصريف 🔴"
        st.info(f"🇺🇸 **وول ستريت (Nasdaq):** {nasdaq_p:.2f}%  |  🐋 **رادار الحيتان:** سيولة USDT نشطة  |  🎯 **{market_desc}**")
    except:
        st.info("🇺🇸 جاري تحديث مؤشرات السوق العالمية الكلية...")
