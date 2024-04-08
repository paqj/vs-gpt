import streamlit as st
from langchain.retrievers import WikipediaRetriever
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.callbacks import StreamingStdOutCallbackHandler

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
    # Model의 실시간 답변을 보면서, 퀴즈를 어떻게 생성하는지 볼 수 있음
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
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


def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)

if not docs:
    st.markdown(
        """
    Welcome to QuizGPT.
                
    I will make a quiz from Wikipedia articles or files you upload to test your knowledge and help you study.
                
    Get started by uploading a file or searching on Wikipedia in the sidebar.
    """
    )
else:
    prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
        You are a helpful assistant that is role playing as a teacher.
            
        Based ONLY on the following context make 10 questions to test the user's knowledge about the text.
        
        Each question should have 4 answers, three of them must be incorrect and one should be correct.
            
        Use (o) to signal the correct answer.
            
        Question examples:
            
        Question: What is the color of the ocean?
        Answers: Red|Yellow|Green|Blue(o)
            
        Question: What is the capital or Georgia?
        Answers: Baku|Tbilisi(o)|Manila|Beirut
            
        Question: When was Avatar released?
        Answers: 2007|2001|2009(o)|1998
            
        Question: Who was Julius Caesar?
        Answers: A Roman Emperor(o)|Painter|Actor|Model
            
        Your turn!
            
        Context: {context}
    """,
                )
            ]
        )

    chain = {"context": format_docs} | prompt | llm

    # 버튼 생성   
    start = st.button("Generate Quiz")

    if start:
        chain.invoke(docs)
