import streamlit as st
from langchain.prompts import PromptTemplate

st.title("Hello world!")
st.subheader("Welcom to Streamlit!")
st.markdown("""
    ### I love it!
""")

# write : string 뿐만 아니라 어떤 데이터 타입이던 보여줌
# st.write("hello")
# st.write([1,2,3])
# st.write({"X": 1, "Y": 2})
# st.write(PromptTemplate)

# p = PromptTemplate.from_template("xxx")
# st.write(p)

# 7.1 Magic
# # magic : write를 사용하지 않고, 변수만 쓰면 자동으로 write
# p


a = [1,2,3]

d = {"x": 1}

a
d

st.selectbox("Choose your Model", ("GPT 3.5", "GPT 4.0"))