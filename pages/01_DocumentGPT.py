import time
import streamlit as st

st.set_page_config(
    page_title="DocumentGPT",
    page_icon="📃",
)

st.title("DocumentGPT")

# st.session_state : data가 캐싱되는 곳.
# data가 변경될 떄 마다 전체 page가 refresh되기 떄문에 
# 전역 리스트 변수가 아닌 별도의 공간을 줘야 함.
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# 신규 메세지는 저장을 하고
# 캐싱된 메세지를 보여주는 용도로 쓸 때는 Write
def send_message(message, role, save=True):
    with st.chat_message(role):
        st.write(message)
    if save:
        st.session_state["messages"].append({"message": message, "role": role})

# 캐싱된 메시지를 보여줌
for message in st.session_state["messages"]:
    send_message(
        message["message"],
        message["role"],
        save=False,
    )

message = st.chat_input("Send a message to the ai")

if message:
    send_message(message, "human")
    time.sleep(2)
    send_message(f"You said: {message}", "ai")

    with st.sidebar:
        st.write(st.session_state)