
import streamlit as st
import pandas as pd
from PIL import Image
from textblob import TextBlob
import matplotlib.pyplot as plt

# ------------------ LOGIN ------------------
def login():
    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if username == "shvan" and password == "shvan1234":
        return True
    elif username or password:
        st.sidebar.error("❌ Incorrect username or password")
    return False

# ------------------ ANALYSIS FUNCTIONS ------------------
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

# ------------------ CHARTS ------------------
def show_charts(df):
    st.subheader("📊 Summary Charts")
    col1, col2 = st.columns(2)

    with col1:
        sentiment_counts = df["Sentiment"].value_counts()
        st.markdown("**Sentiment Distribution**")
        fig1, ax1 = plt.subplots()
        ax1.pie(sentiment_counts, labels=sentiment_counts.index, autopct="%1.1f%%")
        ax1.axis("equal")
        st.pyplot(fig1)

    with col2:
        topic_counts = df["Topic"].value_counts().head(5)
        st.markdown("**Top 5 Topics**")
        fig2, ax2 = plt.subplots()
        ax2.bar(topic_counts.index, topic_counts.values)
        plt.xticks(rotation=15)
        st.pyplot(fig2)

# ------------------ MAIN APP ------------------
def main_app():
    st.image("puk_logo.png", width=150)
    st.title("PUK Election AI Dashboard")

    st.markdown("""
Analyze Facebook comments or posts to detect:
- Sentiment
- Topic
- PUK Support
- Visual summaries
""")

    st.subheader("📥 Paste or Upload Comments")
    text_input = st.text_area("Paste comments/posts (one per line)", height=200)
    uploaded = st.file_uploader("Or upload CSV with 'comment' column")

    if st.button("Analyze") or uploaded:
        if text_input.strip():
            comments = [c.strip() for c in text_input.split("\n") if c.strip()]
            df = pd.DataFrame(comments, columns=["Comment"])
        elif uploaded:
            df = pd.read_csv(uploaded)
            if "comment" not in df.columns:
                st.error("CSV must include a column named 'comment'")
                return
            df.rename(columns={"comment": "Comment"}, inplace=True)
        else:
            st.warning("Please paste text or upload a file.")
            return

        df["Sentiment Score"] = df["Comment"].apply(analyze_sentiment)
        df["Sentiment"] = df["Sentiment Score"].apply(label_sentiment)
        df["Topic"] = df["Comment"].apply(detect_topic)
        df["PUK Support"] = df["Comment"].apply(score_support)
        st.dataframe(df)
        show_charts(df)

    st.markdown("""<div style='text-align: right; color: gray; font-size: 13px; margin-top: 100px;'>
    Prepared by <strong>Shvan Qaraman</strong>
    </div>""", unsafe_allow_html=True)

# ------------------ RUN ------------------
if login():
    main_app()
else:
    st.stop()
