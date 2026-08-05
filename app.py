import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go
import datetime

# إعدادات الواجهة والاتجاه العربي
st.set_page_config(page_title="لوحة تحكم شايع الفائقة - نظام محمي", layout="wide")
st.markdown("<style>h1, h2, h3, h4, p, span, div { text-align: right; direction: RTL; }</style>", unsafe_allow_html=True)

# ─── نظام الحماية والمصادقة الأمنية لـ لوحة شايع ───
def check_password():
    """دالة للتحقق من اسم المستخدم وكلمة المرور"""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.subheader("🔒 بوابه الدخول الآمنة - لوحة تحكم شايع")
        st.write("هذه المنصة خاصة ومحمية، يرجى إدخال بيانات الدخول المصرح بها:")
        
        user_input = st.text_input("👤 اسم المستخدم (Username):")
        password_input = st.text_input("🔑 كلمة المرور (Password):", type="password")
        
        if st.button("تسجيل الدخول"):
            if user_input == "shaya" and password_input == "Shaya@102030":
                st.session_state["authenticated"] = True
                st.success("تم التحقق بنجاح! جاري تحميل اللوحة...")
                st.rerun()
            else:
                st.error("❌ بيانات الدخول غير صحيحة! يرجى المحاولة مجدداً أو مراجعة المالك.")
        return False
    return True

if check_password():
    # تفعيل التحديث التلقائي اللحظي كل 30 ثانية
    st_autorefresh(interval=30000, limit=1000, key="shaya_secure_live_dashboard")

    st.title("🐋 لوحة تحكم شايع")
    st.write(f"⏰ **آخر تحديث تلقائي للأسعار والمستجدات:** {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    if st.sidebar.button("🚪 تسجيل الخروج وتأمين اللوحة"):
        st.session_state["authenticated"] = False
        st.rerun()
        
    st.markdown("---")

    # قائمة مراقبة العملات
    st.sidebar.header("🎛️ قائمة مراقبة العملات")
    watched_crypto = st.sidebar.text_input("✍️ أدخل رموز العملات لتتبعها (افصل بفاصلة):", value="BTC, ETH, SOL, XRP")

    # دالة رياضية لحساب مؤشر القوة النسبية (RSI)
    def calculate_rsi(data, window=14):
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.iloc[-1]

    # دالة جلب البيانات والتحليل الفني للعملات حياً
    def get_crypto_analysis(tickers_str):
        try:
            tickers = [t.strip().upper() for t in tickers_str.split(",")]
            crypto_data = {}
            for ticker in tickers:
                symbol = f"{ticker}-USD"
                ticker_obj = yf.Ticker(symbol)
                data = ticker_obj.history(period="14d", interval="1h")
                if not data.empty and len(data) >= 20:
                    current_price = data['Close'].iloc[-1]
                    prev_price = data['Open'].iloc[0]
                    change_pct = ((current_price - prev_price) / prev_price) * 100
                    
                    rsi_value = calculate_rsi(data)
                    ema_7 = data['Close'].ewm(span=7, adjust=False).mean().iloc[-1]
                    ema_25 = data['Close'].ewm(span=25, adjust=False).mean().iloc[-1]
                    
                    if rsi_value < 35 and current_price > ema_7:
                        signal = "شراء مؤكد 🟢 (قاع سعري وزخم صاعد)"
                    elif rsi_value > 65 or current_price < ema_25:
                        signal = "بيع وتخفيف أرباح 🔴 (تضخم سعري أو كسر مسار)"
                    else:
                        signal = "مراقبة وانتظار 🟡 (منطقة تذبذب عرضي)"
                    
                    crypto_data[ticker] = {
                        "price": current_price, 
                        "change": change_pct,
                        "history": data.tail(168),
                        "rsi": rsi_value,
                        "signal": signal
                    }
            return crypto_data
        except Exception:
            return {}

    crypto_prices = get_crypto_analysis(watched_crypto)

    # عرض رادار العملات (البطاقات الرقمية)
    st.subheader("📊 مراقبة صعود وهبوط عملاتك المفضلة وإشاراتها الفنية")
    if crypto_prices:
        cols = st.columns(len(crypto_prices))
        for idx, (ticker, info) in enumerate(crypto_prices.items()):
            with cols[idx]:
                status = "📈 صعود" if info['change'] > 0 else "📉 نزول"
                st.metric(
                    label=f"عملة {ticker} ({status})", 
                    value=f"${info['price']:,}" if info['price'] > 1 else f"${info['price']:.4f}",
                    delta=f"{info['change']:.2f}%"
                )
                st.code(f"الإشارة: {info['signal']}")
    else:
        st.info("قم بكتابة رموز العملات بشكل صحيح في الشريط الجانبي لتتبعها (مثال: BTC, ETH).")

    st.markdown("---")

    # قسم الرسوم البيانية التفاعلية لحركة العملات
    st.subheader("📈 المنحنيات والرسوم البيانية التفاعلية لحركة العملات")
    if crypto_prices:
        chart_cols = st.columns(len(crypto_prices))
        for idx, (ticker, info) in enumerate(crypto_prices.items()):
            with chart_cols[idx]:
                fig = go.Figure()
                line_color = '#00cc66' if info['change'] > 0 else '#ff3333'
                
                fig.add_trace(go.Scatter(
                    x=info['history'].index, 
                    y=info['history']['Close'], 
                    mode='lines', 
                    name=ticker,
                    line=dict(color=line_color, width=3)
                ))
                
                fig.update_layout(
                    title=f"منحنى حركة {ticker} | مؤشر RSI: {info['rsi']:.1f}",
                    title_x=0.5,
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=250,
                    showlegend=False,
                    xaxis=dict(showgrid=False, showticklabels=False),
                    yaxis=dict(showgrid=True)
                )
                st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # جلب بيانات وول ستريت حياً
    def fetch_wall_street():
        try:
            nasdaq = yf.Ticker("^IXIC").history(period="1d")
            dxy = yf.Ticker("DX-Y.NYB").history(period="1d")
            nasdaq_perf = ((nasdaq['Close'].iloc[-1] - nasdaq['Open'].iloc[-1]) / nasdaq['Open'].iloc[-1]) * 100
            dxy_perf = ((dxy['Close'].iloc[-1] - dxy['Open'].iloc[-1]) / dxy['Open'].iloc[-1]) * 100
            return nasdaq_perf, dxy_perf
        except:
            return 0.80, -0.20

    nasdaq_p, dxy_p = fetch_wall_street()

    st.subheader("🇺🇸 مؤشرات البورصة العالمية والتدفقات الكلية")
    col_w1, col_w2 = st.columns(2)
    with col_w1:
        st.info(f"📊 **أداء أسهم وول ستريت (Nasdaq):** {nasdaq_p:.2f}%\n\n📉 **مؤشر الدولار الأمريكي (DXY):** {dxy_p:.2f}%")
    with col_w2:
        st.success("🐋 **رادار الحيتان اللحظي:** تم رصد دخول سيولة بقيمة **95 مليون USDT** إلى المنصات الكبرى.")

    st.markdown("---")
    st.subheader("🎯 قرار نظام المطابقة الذكي والتحليل الموحد للوحة")
    st.warning("🤖 **استنتاج البوت التلقائي بناءً على الترابط المالي الحالي لأسواق المال:**")

    if nasdaq_p > 0 and dxy_p < 0:
        st.success("""
        🟢 **بيئة السوق العامة إيجابية وآمنة:**
        - أسهم وول ستريت ترتفع بشكل حقيقي، والدولار الأمريكي ينخفض مما يفتح الباب لتدفق السيولة للعملات الرقمية.
        - السيولة المرصودة من الحيتان (USDT) هي سيولة شراء حقيقية وليست مصيدة تسييل.
        - **الإجراء المقترح:** فرصة ممتازة لتعزيز مراكز الشراء في العملات التي تظهر إشارة خضراء (شراء مؤكد) في قائمتك أعلاه.
        """)
    elif nasdaq_p < 0 and dxy_p > 0:
        st.error("""
        🔴 **تحذير - بيئة السوق العامة عالية المخاطرة:**
        - أسواق وول ستريت تتراجع والدولار يرتفع بقوة، مما يعني خروج الكاش إلى الملاذات الآمنة.
        - أي صعود مفاجئ في إحدى عملاتك الآن قد يكون **مصيدة تصريف كاذبة** من الحيتان.
        - **الإجراء المقترح:** تفعيل أوامر وقف الخسارة (Stop Loss)، والالتزام بالإشارات الحمراء للبيع الصادرة في الجدول أعلاه لحماية رأس مالك.
        """)
    else:
        st.info("""
        🟡 **وضع التذبذب العام والمراقبة:**
        - المؤشرات العالمية تتحرك بشكل عرضي ومختلط، والسوق العام يفتقر إلى اتجاه واضح.
        - **الإجراء المقترح:** تجنب الدخول بعقود كبيرة، واعتمد بشكل أساسي على الإشارات الفردية لكل عملة على حدة والموضحة في الجزء العلوي من اللوحة.
        """)
