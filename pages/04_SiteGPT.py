import streamlit as st
from langchain.document_loaders import AsyncChromiumLoader
from langchain.document_transformers import Html2TextTransformer

# GPT가 특정 Site를 크롤링하고 그 정보로 알려줌.
# 1. playwright, chromimum
# 2. site loader

st.set_page_config(
    page_title="SiteGPT",
    page_icon="🖥️",
)

# HTML을 Text로 변경
html2text_transformer = Html2TextTransformer()

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
    # Crawling
    loader = AsyncChromiumLoader([url])
    docs = loader.load()
    # HTML 태그 없이 content만
    transformed = html2text_transformer.transform_documents(docs)
    st.write(docs)