import streamlit as st


# # with 패턴을 쓰면 component에 내용을 바로 넣을 수 있음
# st.title("title")

# with st.sidebar:
#     st.title("sidebar title")
#     st.text_input("xxx")


# tab_one, tab_two, tab_three = st.tabs(["A", "B", "C"])

# with tab_one:
#     st.write("1")

# with tab_two:
#     st.write("2")

# with tab_three:
#     st.write("3")


st.set_page_config(
    page_title="FullstackGPT Home",
    page_icon="🤖",
)

# pages folder에 들어 있으면 sidebar에 목록이 생김.
# folder 내의 파일 순서대로 정렬됨

st.title("FullstackGPT Home")

st.markdown(
    """
# Hello!
            
Welcome to my FullstackGPT Portfolio!
            
Here are the apps I made:
            
- [X] [DocumentGPT](/DocumentGPT)
- [ ] [PrivateGPT](/PrivateGPT)
- [ ] [QuizGPT](/QuizGPT)
- [ ] [SiteGPT](/SiteGPT)
- [ ] [MeetingGPT](/MeetingGPT)
- [ ] [InvestorGPT](/InvestorGPT)
"""
)