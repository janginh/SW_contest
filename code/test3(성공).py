# test2.py

import streamlit as st
import random
from dotenv import load_dotenv
import os
import google.generativeai as genai

# 1. .env 파일 로드
load_dotenv()

# 2. Gemini 클라이언트 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 3. 모델 준비
model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

# 점수 초기화
if 'score' not in st.session_state:
    st.session_state.score = 0

# 선택 주제
st.title("좋아하는 걸 선택해봐!")

options = ["애니메이션", "드라마", "축구", "영화"]
selected = st.radio("카테고리를 선택하거나 직접 입력해:", options + ["직접 입력"])

if selected == "직접 입력":
    keyword = st.text_input("주제를 입력해줘!")
else:
    keyword = selected

# 글 생성하기
if keyword:
    if st.button("글 생성하기"):
        with st.spinner('글을 생성 중입니다...'):
            prompt = f"{keyword}에 관한 흥미로운 이야기를 만들어줘. (300자 내외)"
            response = model.generate_content(prompt)
            story = response.text
            st.session_state.story = story

# 글 보여주기
if 'story' in st.session_state:
    st.subheader("생성된 글")
    st.markdown(st.session_state.story)

    # 문제 출제
    st.subheader("문제 풀어볼까?")

    # 예시 문제 1 - 단어 뜻 맞추기
    word_question = "균열"
    options = ["갈라짐", "연합", "발전", "확장"]
    answer_idx = 0  # 정답은 첫 번째

    user_answer = st.radio(f"'균열' 이 무슨 뜻일까?", options, key="q1")

    if st.button("정답 제출 (문제1)"):
        if user_answer == options[answer_idx]:
            st.success("정답이야! 🎯")
            st.session_state.score += 10
        else:
            st.error("틀렸어! 😭")

    # 예시 문제 2 - 글 흐름 이해
    flow_question = "토니 스타크가 마지막에 고민한 것은?"
    flow_options = ["과거를 바꾸는 방법", "자신의 선택", "어벤저스 승리 방법", "인피니티 스톤 강화"]
    flow_answer_idx = 1

    user_flow_answer = st.radio(flow_question, flow_options, key="q2")

    if st.button("정답 제출 (문제2)"):
        if user_flow_answer == flow_options[flow_answer_idx]:
            st.success("정답이야! 🎯")
            st.session_state.score += 30
        else:
            st.error("틀렸어!")

    # 추가 문제 - 너의 의견
    st.subheader("너라면 어떤 선택을 했을까?")
    user_opinion = st.text_area("자유롭게 써봐", key="q3")

    if st.button("의견 제출"):
        st.success("좋은 생각이야! 창의력 +50점 추가! 🌟")
        st.session_state.score += 50

    # 최종 점수
    st.header(f"🌟 최종 점수: {st.session_state.score}점 🌟")

    # 간단한 랭킹 관리
    if 'ranking' not in st.session_state:
        st.session_state.ranking = []

    if st.button("랭킹에 등록하기"):
        name = st.text_input("이름을 입력해:", key="name_input")
        if name:
            st.session_state.ranking.append((name, st.session_state.score))
            st.session_state.ranking = sorted(st.session_state.ranking, key=lambda x: x[1], reverse=True)

    if st.session_state.ranking:
        st.subheader("랭킹")
        for idx, (name, score) in enumerate(st.session_state.ranking, 1):
            st.write(f"{idx}등: {name} - {score}점")
