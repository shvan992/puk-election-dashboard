
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image
from textblob import TextBlob
import matplotlib.pyplot as plt

st.set_page_config(page_title="PUK AI Dashboard", layout="centered")

# Language labels
langs = {
    "English": {
        "login": "Login", "username": "Username", "password": "Password",
        "dashboard_title": "PUK Election AI Dashboard",
        "section_title": "📥 Analyze Comments",
        "facebook_section": "📘 Facebook Post Analyzer",
        "paste_post": "Paste Facebook post content below:",
        "analyze": "Analyze",
        "upload_file": "Upload CSV, Excel, or PDF",
        "summary": "📊 Summary Charts",
        "sentiment_chart": "Sentiment",
        "topic_chart": "Top 5 Topics"
    },
    "Arabic": {
        "login": "تسجيل الدخول", "username": "اسم المستخدم", "password": "كلمة المرور",
        "dashboard_title": "لوحة تحكم الذكاء الاصطناعي لانتخابات الاتحاد الوطني الكردستاني",
        "section_title": "📥 تحليل التعليقات",
        "facebook_section": "📘 تحليل منشور فيسبوك",
        "paste_post": "الصق محتوى منشور فيسبوك أدناه:",
        "analyze": "تحليل",
        "upload_file": "تحميل CSV أو Excel أو PDF",
        "summary": "📊 الرسوم البيانية",
        "sentiment_chart": "المشاعر",
        "topic_chart": "أهم 5 مواضيع"
    },
    "Kurdish": {
        "login": "چوونەژوورەوە", "username": "ناوی بەکارهێنەر", "password": "وشەی نهێنی",
        "dashboard_title": "داشبۆردی AI ی هەڵبژاردنی یەکێتی",
        "section_title": "📥 ڕاوێژکردنی لێدوانەکان",
        "facebook_section": "📘 ڕاوێژکردنی بابەتی فەیسبووک",
        "paste_post": "ناوەڕۆکی بابەتی فەیسبووک لێرە بچوونە ژوورەوە:",
        "analyze": "آنالیز",
        "upload_file": "بارکردنی فایل CSV، Excel یان PDF",
        "summary": "📊 شێوەکارییەکان",
        "sentiment_chart": "هەست",
        "topic_chart": "5 بابەتی سەرەکی"
    }
}

# Login page
def login_screen():
    st.image("puk_logo.png", width=100)
    st.title("PUK AI Dashboard")
    language = st.selectbox("🌐 Language / زمان / زمان", ["English", "Arabic", "Kurdish"])
    st.session_state.lang = language
    with st.form("login_form"):
        username = st.text_input(langs[language]["username"])
        password = st.text_input(langs[language]["password"], type="password")
        submit = st.form_submit_button(langs[language]["login"])
        if submit and username == "shvan" and password == "shvan1234":
            st.session_state.authenticated = True
            st.rerun()

# Analysis logic
def analyze_sentiment(text): return TextBlob(text).sentiment.polarity
def label_sentiment(score): return "Positive" if score > 0 else "Negative" if score < 0 else "Neutral"
def detect_topic(text):
    topics = {"Corruption": ["bribe", "corrupt"], "Education": ["school", "student"], "Security": ["attack", "police"],
              "Economy": ["money", "job", "price"], "Leadership": ["bafel", "pavel", "talabani"]}
    text = text.lower()
    for topic, keys in topics.items():
        if any(k in text for k in keys): return topic
    return "Other"
def score_support(text):
    keys = ["puk", "patriotic", "talabani", "bafel", "pavel", "mam jala", "یەکێتی"]
    text = text.lower()
    if any(k in text for k in keys):
        polarity = analyze_sentiment(text)
        return "Supports PUK" if polarity > 0 else "Criticizes PUK" if polarity < 0 else "Mentions PUK"
    return "No Mention"
def extract_text_from_pdf(file): return "\n".join([p.get_text() for p in fitz.open(stream=file.read(), filetype="pdf")])
def show_charts(df, lang):
    st.subheader(langs[lang]["summary"])
    col1, col2 = st.columns(2)
    with col1:
        sent = df["Sentiment"].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(sent, labels=sent.index, autopct="%1.1f%%"); ax1.axis("equal")
        st.markdown(f"**{langs[lang]['sentiment_chart']}**"); st.pyplot(fig1)
    with col2:
        topics = df["Topic"].value_counts().head(5)
        fig2, ax2 = plt.subplots(); ax2.bar(topics.index, topics.values); plt.xticks(rotation=15)
        st.markdown(f"**{langs[lang]['topic_chart']}**"); st.pyplot(fig2)

# Dashboard page
def main_app(lang):
    st.markdown(f"### {langs[lang]['dashboard_title']}")
    st.subheader(langs[lang]["facebook_section"])
    post = st.text_area(langs[lang]["paste_post"])
    if st.button(langs[lang]["analyze"] + " Post") and post:
        df = pd.DataFrame([post], columns=["Comment"])
        df["Sentiment Score"] = df["Comment"].apply(analyze_sentiment)
        df["Sentiment"] = df["Sentiment Score"].apply(label_sentiment)
        df["Topic"] = df["Comment"].apply(detect_topic)
        df["PUK Support"] = df["Comment"].apply(score_support)
        st.dataframe(df)
    st.subheader(langs[lang]["section_title"])
    input_txt = st.text_area("Enter comments (one per line)", height=120)
    uploaded = st.file_uploader(langs[lang]["upload_file"], type=["csv", "xlsx", "pdf"])
    if st.button(langs[lang]["analyze"]) or uploaded:
        if input_txt.strip():
            df = pd.DataFrame([line for line in input_txt.split("\n") if line], columns=["Comment"])
        elif uploaded:
            if uploaded.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded)
            elif uploaded.name.endswith(".csv"):
                df = pd.read_csv(uploaded)
            elif uploaded.name.endswith(".pdf"):
                df = pd.DataFrame(extract_text_from_pdf(uploaded).split("\n"), columns=["Comment"])
            else:
                st.error("Unsupported file.")
                return
        df["Sentiment Score"] = df["Comment"].apply(analyze_sentiment)
        df["Sentiment"] = df["Sentiment Score"].apply(label_sentiment)
        df["Topic"] = df["Comment"].apply(detect_topic)
        df["PUK Support"] = df["Comment"].apply(score_support)
        st.dataframe(df); show_charts(df, lang)
    st.markdown("<div style='text-align:right;font-size:13px;margin-top:40px;'>Prepared by <b>Shvan Qaraman</b></div>", unsafe_allow_html=True)

# Run
if "authenticated" not in st.session_state: st.session_state.authenticated = False
if "lang" not in st.session_state: st.session_state.lang = "English"
if st.session_state.authenticated:
    main_app(st.session_state.lang)
else:
    login_screen()
