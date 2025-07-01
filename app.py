
import streamlit as st
from PIL import Image

st.set_page_config(page_title="PUK Election AI Dashboard", layout="wide")

# Display PUK logo
logo = Image.open("puk_logo.png")
st.image(logo, width=150)

st.title("PUK Election AI Dashboard")

st.markdown("""
This dashboard uses Artificial Intelligence to analyze election-related content for the Patriotic Union of Kurdistan (PUK).

Key features include:
- 📊 **Sentiment Analysis** of comments and posts
- 🧠 **Topic Detection** from discussions
- 🟢 **PUK Support Scoring** based on language used
- 🤖 **Bot & Influencer Detection**
""")

st.info("Note: This is a demo version. Contact the technical team for a fully integrated system.")

# Footer with credit
st.markdown("""<div style='text-align: right; color: gray; font-size: 13px; margin-top: 100px;'>
Prepared by <strong>Shvan Qaraman</strong>
</div>""", unsafe_allow_html=True)
