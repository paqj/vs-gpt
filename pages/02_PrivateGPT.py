from langchain.prompts import ChatPromptTemplate
from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings import CacheBackedEmbeddings, OllamaEmbeddings
from langchain.schema.runnable import RunnableLambda, RunnablePassthrough
from langchain.storage import LocalFileStore
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.chat_models import ChatOllama
from langchain.callbacks.base import BaseCallbackHandler

import streamlit as st

# LLM과 Embedding Model을 다운 받고, Offline에서 돌림
# Ollama : Local Model을 실행시키는 것

# HuggingFaceHub : 수많은 AI 모델을 선택해서 클라우드에서 돌리거나, 다운 받아서 off line에서 돌릴 수 있음
# 1. Hugging Interface - Access Token 으로 사용하는 유료 모델
# 2. 

st.set_page_config(
    page_title="PriavteGPT",
    page_icon="📃",
)

# llm의 event를 listen -> 작용
# *args, **kwargs : 많은 argument나 keyword를 받음 on_llm_start(1,2,3,4,a=1,b=2,c=3...)
# llm start -> message_box 초기화
# llm에서 token을 생성할 때 마다 message_box에 계속 추가
# llm end -> message save
class ChatCallbackHandler(BaseCallbackHandler):
    message = ""

    def on_llm_start(self, *args, **kwargs):
        self.message_box = st.empty()

    def on_llm_end(self, *args, **kwargs):
        save_message(self.message, "ai")

    def on_llm_new_token(self, token, *args, **kwargs):
        self.message += token
        self.message_box.markdown(self.message)

# llm = ChatOllama(
#     model="mistral:latest",
#     temperature=0.1,
#     streaming=True,
#     callbacks=[
#         ChatCallbackHandler(),
#     ],
# )

# 동일한 file(hashing)이면 구동되지 않고, 직전에 실행된 결과를 리턴.
@st.cache_data(show_spinner="Embdding file...")
def embed_file(file):
    file_content = file.read()
    # Caching
    file_path = f"./.cache/private_files/{file.name}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    cache_dir = LocalFileStore(f"./.cache/private_embeddings/{file.name}")

    # splitter
    splitter = CharacterTextSplitter.from_tiktoken_encoder(
        separator="\n",
        chunk_size=600,
        chunk_overlap=100,
    )
    loader = UnstructuredFileLoader(file_path)
    docs = loader.load_and_split(text_splitter=splitter)

    # embedding
    embeddings = OllamaEmbeddings(
        model="mistral:latest"
    )
    cached_embeddings = CacheBackedEmbeddings.from_bytes_store(embeddings, cache_dir)
    vectorstore = FAISS.from_documents(docs, cached_embeddings)
    retriever = vectorstore.as_retriever()
    return retriever

def save_message(message, role):
    st.session_state["messages"].append({"message": message, "role": role})

def send_message(message, role, save=True):
    with st.chat_message(role):
        st.markdown(message)
    if save:
        save_message(message, role)


def paint_history():
    for message in st.session_state["messages"]:
        send_message(message["message"], message["role"], save=False)

def format_docs(docs):
    return "\n\n".join(document.page_content for document in docs)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Answer the question using ONLY the following context. If you don't know the answer just say you don't know. DON'T make anything up.
            
            Context: {context}
            """,
        ),
        ("human", "{question}"),
    ]
)

st.title("DocumentGPT")

st.markdown(
    """
Welcome!
            
Use this chatbot to ask questions to an AI about your files!

Upload your files on the sidebar.
"""
)

# Uploader를 sidebar로 이동
with st.sidebar:
    file = st.file_uploader(
        "Upload a .txt .pdf or .docx file",
        type=["pdf", "txt", "docx"],
    )

    model = st.selectbox("Choose Your model", ("mistral","llama2"))
    if model == "mistral":
        llm = ChatOllama(
        model="mistral:latest",
        temperature=0.1,
        streaming=True,
        callbacks=[ChatCallbackHandler(),
        ],
    )
    else:
        llm = ChatOllama(
        model="llama2:latest",
        temperature=0.1,
        streaming=True,
        callbacks=[ChatCallbackHandler(),],
    )

if file:
    retriever = embed_file(file)

    send_message("I'm ready! Ask away!", "ai", save=False)
    paint_history()

    message = st.chat_input("Ask Anything about your file...")

    if message:
        send_message(message, "human")
        # User의 Input에서 retriver를 호출 -> 추출한 docs를 -> prompt에 전달(context, question) -> llm
        chain = (
            {
                "context": retriever | RunnableLambda(format_docs),
                "question": RunnablePassthrough(), # "question": message
            }
            | prompt
            | llm
        )

        # ai의 답변으로 보이게 함
        with st.chat_message("ai"):
            response = chain.invoke(message)


# file이 없으면, history 초기화
else:
    st.session_state["messages"] = []