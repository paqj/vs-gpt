import streamlit as st
from langchain.prompts import PromptTemplate
from datetime import datetime


# streamlit 은 데이터가 바뀌면 코드 전체가 Refresh 됨
today = datetime.today().strftime("%H:%M:%S")
st.title(today)


a = [1,2,3]

d = {"x": 1}

a
d

model = st.selectbox("Choose your Model", ("GPT 3.5", "GPT 4.0"))

# 전체 페이지를 Refresh 함 -> 조건문으로 요소를 숨기는 것 처럼 보이게 할 수 있음.
if model == "GPT 3.5":
    st.write("Cheap!!")
else:
    name = st.text_input("What is your name?")
    name

    value = st.slider("temperature", min_value=0.1, max_value=1.0)
    value