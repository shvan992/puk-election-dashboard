
import streamlit as st
import pandas as pd
import fitz  # PyMuPDF
from PIL import Image
from textblob import TextBlob
import matplotlib.pyplot as plt

st.set_page_config(page_title="PUK AI Dashboard", layout="centered")

# ----------- Style -----------
st.markdown("""
    <style>
    .main {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 12px;
    }
    .block-container {
        padding: 1rem 2rem;
    }
    .title-style {
        font-size: 2.3rem;
        text-align: center;
        color: #1a4d2e;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #555;
    }
    .footer {
        text-align: right;
        font-size: 13px;
        color: gray;
        margin-top: 50px;
    }
    </style>
""", unsafe_allow_html=True)

# ----------- Language Labels -----------
langs = {
    "English": {
        "login": "Login",
        "username": "Username",
        "password": "Password",
        "dashboard_title": "PUK Election AI Dashboard",
        "section_title": "📥 Analyze Comments",
        "facebook_section": "📘 Facebook Post Analyzer",
        "paste_post": "Paste Facebook post content below:",
        "analyze": "Analyze",
        "upload_file": "Upload CSV, Excel, or PDF",
        "summary": "📊 Summary Charts",
        "sentiment_chart": "Sentiment",
        "topic_chart": "Top 5 Topics"
    }
}

# ----------- Login Screen -----------
def login_screen(language):
    st.image("puk_logo.png", width=110)
    st.markdown(f"<h1 class='title-style'>PUK AI Dashboard</h1>", unsafe_allow_html=True)
    with st.form("login_form"):
        username = st.text_input(langs[language]["username"])
        password = st.text_input(langs[language]["password"], type="password")
        submit = st.form_submit_button(langs[language]["login"])
        return username == "shvan" and password == "shvan1234" and submit

# ----------- Analysis Functions -----------
def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity

def label_sentiment(score):
    return "Positive" if score > 0 else "Negative" if score < 0 else "Neutral"

def detect_topic(text):
    topics = {
        "Corruption": ["bribe", "corruption", "steal", "corrupt"],
        "Education": ["school", "university", "student", "education"],
        "Security": ["attack", "police", "terror", "safety"],
        "Economy": ["money", "job", "price", "economy", "dollar"],
        "Leadership": ["bafel", "pavel", "talabani", "leader", "president"]
    }
    text_lower = text.lower()
    for topic, keywords in topics.items():
        if any(k in text_lower for k in keywords):
            return topic
    return "Other"

def score_support(text):
    keywords = ["puk", "patriotic", "talabani", "bafel", "pavel", "mam jala", "یەکێتی"]
    text_lower = text.lower()
    if any(k in text_lower for k in keywords):
        polarity = analyze_sentiment(text)
        return "Supports PUK" if polarity > 0 else "Criticizes PUK" if polarity < 0 else "Mentions PUK"
    return "No Mention"

def show_charts(df, lang):
    st.subheader(langs[lang]["summary"])
    col1, col2 = st.columns(2)

    with col1:
        sentiment_counts = df["Sentiment"].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(sentiment_counts, labels=sentiment_counts.index, autopct="%1.1f%%", startangle=90)
        ax1.axis("equal")
        st.markdown(f"**{langs[lang]['sentiment_chart']}**")
        st.pyplot(fig1)

    with col2:
        topic_counts = df["Topic"].value_counts().head(5)
        fig2, ax2 = plt.subplots()
        ax2.bar(topic_counts.index, topic_counts.values, width=0.4)
        plt.xticks(rotation=15)
        st.markdown(f"**{langs[lang]['topic_chart']}**")
        st.pyplot(fig2)

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in doc])

# ----------- Main App -----------
def main_app(lang):
    st.markdown("<div class='main'>", unsafe_allow_html=True)
    st.markdown(f"<h2 class='subtitle'>{langs[lang]['dashboard_title']}</h2>", unsafe_allow_html=True)

    st.subheader(langs[lang]["facebook_section"])
    post_text = st.text_area(langs[lang]["paste_post"])
    if st.button(langs[lang]["analyze"] + " Post"):
        if post_text.strip():
            df = pd.DataFrame([post_text], columns=["Comment"])
            df["Sentiment Score"] = df["Comment"].apply(analyze_sentiment)
            df["Sentiment"] = df["Sentiment Score"].apply(label_sentiment)
            df["Topic"] = df["Comment"].apply(detect_topic)
            df["PUK Support"] = df["Comment"].apply(score_support)
            st.dataframe(df)

    st.subheader(langs[lang]["section_title"])
    text_input = st.text_area("Enter comments (one per line)", height=150)
    uploaded = st.file_uploader(langs[lang]["upload_file"], type=["csv", "xlsx", "pdf"])

    if st.button(langs[lang]["analyze"]) or uploaded:
        if text_input.strip():
            comments = [c.strip() for c in text_input.split("\n") if c.strip()]
            df = pd.DataFrame(comments, columns=["Comment"])
        elif uploaded:
            try:
                if uploaded.name.endswith(".xlsx"):
                    df = pd.read_excel(uploaded)
                elif uploaded.name.endswith(".csv"):
                    df = pd.read_csv(uploaded)
                elif uploaded.name.endswith(".pdf"):
                    text = extract_text_from_pdf(uploaded)
                    comments = [c.strip() for c in text.split("\n") if c.strip()]
                    df = pd.DataFrame(comments, columns=["Comment"])
                else:
                    st.error("Unsupported file format.")
                    return
                if "Comment" not in df.columns and "comment" in df.columns:
                    df.rename(columns={"comment": "Comment"}, inplace=True)
            except Exception as e:
                st.error(f"File error: {e}")
                return
        else:
            return

        df["Sentiment Score"] = df["Comment"].apply(analyze_sentiment)
        df["Sentiment"] = df["Sentiment Score"].apply(label_sentiment)
        df["Topic"] = df["Comment"].apply(detect_topic)
        df["PUK Support"] = df["Comment"].apply(score_support)
        st.dataframe(df)
        show_charts(df, lang)

    st.markdown(f"<div class='footer'>Prepared by <strong>Shvan Qaraman</strong></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------- Run App -----------
lang = "English"
if login_screen(lang):
    st.empty()
    main_app(lang)
