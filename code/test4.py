# test2.py

import streamlit as st
import random
from dotenv import load_dotenv
import os
import google.generativeai as genai
import json

# 1. .env 파일 로드
load_dotenv()

# 2. Gemini 클라이언트 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 점수 및 세션 상태 초기화
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'story' not in st.session_state:
    st.session_state.story = ""
if 'questions' not in st.session_state:
    st.session_state.questions = []

# UI - 주제 선택
st.title("좋아하는 걸 선택해봐!")

options = ["애니메이션", "드라마", "축구", "영화"]
selected = st.radio("카테고리를 선택하거나 직접 입력해:", options + ["직접 입력"])

if selected == "직접 입력":
    keyword = st.text_input("주제를 입력해줘!")
else:
    keyword = selected

# 글과 문제 생성
if keyword:
    if st.button("글과 문제 생성하기"):
        with st.spinner('글과 문제를 생성 중입니다...'):
            prompt = f"""
            '{keyword}'를 주제로 300자 이내 흥미로운 이야기를 써줘.
            그리고 그 이야기 내용을 기반으로 문제 2개를 만들어줘.
            문제마다 선택지는 4개씩 주고, 정답도 명확히 알려줘.
            아래 JSON 형태로 답변해줘:

            {{
              "story": "이야기 본문",
              "questions": [
                {{
                  "question": "문제 1",
                  "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
                  "answer": "정답"
                }},
                {{
                  "question": "문제 2",
                  "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
                  "answer": "정답"
                }}
              ]
            }}
            """

            try:
                model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
                response = model.generate_content(prompt)
                result = json.loads(response.text)

                # 세션에 저장
                st.session_state.story = result['story']
                st.session_state.questions = result['questions']
                st.session_state.score = 0  # 점수 리셋

            except Exception as e:
                st.error(f"오류 발생: {e}")

# 생성된 글과 문제 보여주기
if st.session_state.story:
    st.subheader("🌟 생성된 이야기 🌟")
    st.markdown(st.session_state.story)

if st.session_state.questions:
    st.subheader("✏️ 문제 풀어보기")

    for idx, q in enumerate(st.session_state.questions):
        st.markdown(f"**문제 {idx+1}: {q['question']}**")
        user_answer = st.radio(
            f"선택지를 골라주세요:",
            q['options'],
            key=f"user_answer_{idx}"
        )

        if st.button(f"정답 제출 (문제 {idx+1})", key=f"submit_{idx}"):
            if user_answer == q['answer']:
                st.success("정답입니다! 🎉")
                st.session_state.score += 10
            else:
                st.error(f"틀렸어요! 정답은 '{q['answer']}' 입니다.")

    st.header(f"🏆 최종 점수: {st.session_state.score}점 🏆")

