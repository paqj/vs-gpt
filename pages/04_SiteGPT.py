import streamlit as st
from langchain.document_loaders import SitemapLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# GPT가 특정 Site를 크롤링하고 그 정보로 알려줌.
# 1. playwright, chromimum
# 2. site loader

st.set_page_config(
    page_title="SiteGPT",
    page_icon="🖥️",
)

def parse_page(soup):
    # soup에서 header, footer 제거
    header = soup.find("header")
    footer = soup.find("footer")
    if header:
        header.decompose()
    if footer:
        footer.decompose()
    # 공백, 줄바꿈, 반복문구 삭제
    return (
        str(soup.get_text())
        .replace("\n", " ")
        .replace("\xa0", " ")
        .replace("CloseSearch Submit Blog", "")
    )

@st.cache_data(show_spinner="Loading website...")
def load_website(url):
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=1000,
        chunk_overlap=200,
    )
    # html -> text 까지
    loader = SitemapLoader(
        url,
        filter_urls=[
            r"^(.*\/blog\/).*",
        ],
        parsing_function=parse_page,
    )
    # 2초 딜레이
    loader.requests_per_second = 2
    docs = loader.load_and_split(text_splitter=splitter)
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
        