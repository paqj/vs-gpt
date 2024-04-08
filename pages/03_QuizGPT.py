import streamlit as st
from langchain.retrievers import WikipediaRetriever
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI

st.set_page_config(
    page_title="QuizGPT",
    page_icon="📃",
)

st.title("QuizGPT")

# https://platform.openai.com/docs/models/gpt-3-5-turbo
# https://openai.com/pricing#language-models
llm = ChatOpenAI(
    temperature=0.1,
    model="gpt-3.5-turbo-1106",
)

# File을 토큰 사이즈에 따라 분류
@st.cache_data(show_spinner="Loading file...")
def split_file(file):
    file_content = file.read()
    file_path = f"./.cache/quiz_files/{file.name}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load_and_split(text_splitter=splitter)
    return docs

with st.sidebar:
    docs = None
    choice = st.selectbox(
        "Choose what you want to use.",
        (
            "File",
            "Wikipedia Article",
        ),
    )
    if choice == "File":
        file = st.file_uploader(
            "Upload a .docx , .txt or .pdf file",
            type=["pdf", "txt", "docx"],
        )
        if file:
            docs = split_file(file)
    else:
        topic = st.text_input("Search Wikipedia...")
        if topic:
            # 최상단 n개의 검색 결과
            retriever = WikipediaRetriever(top_k_results=5)
            with st.status("Seaching Wikipedia..."):
                docs = retriever.get_relevant_documents(topic)

if not docs:
    st.markdown(
        """
    Welcome to QuizGPT.
                
    I will make a quiz from Wikipedia articles or files you upload to test your knowledge and help you study.
                
    Get started by uploading a file or searching on Wikipedia in the sidebar.
    """
    )
else:
    st.write(docs)