import streamlit as st
from langchain.document_loaders import SitemapLoader

# GPT가 특정 Site를 크롤링하고 그 정보로 알려줌.
# 1. playwright, chromimum
# 2. site loader

st.set_page_config(
    page_title="SiteGPT",
    page_icon="🖥️",
)

@st.cache_data(show_spinner="Loading website...")
def load_website(url):
    # html -> text 까지
    loader = SitemapLoader(url)
    loader.requests_per_second = 5
    docs = loader.load()
    return docs

st.markdown(
    """
    # SiteGPT
            
    Ask questions about the content of a website.
            
    Start by writing the URL of the website on the sidebar.
"""
)

with st.sidebar:
    url = st.text_input("Write down a URL", placeholder="https://example.com")


if url:
    if ".xml" not in url:
        with st.sidebar:
            st.error("Please write down a Sitemap URL.")
    else:
        docs = load_website(url)
        st.write(docs)
        