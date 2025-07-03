# test2.py

import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Gemini API 키 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 세션 상태 초기화
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
            '{keyword}'를 주제로 300자 이내 짧은 이야기를 써줘.
            그리고 그 이야기 내용을 바탕으로 문제 2개를 만들어줘.
            아래처럼 형식을 지켜서 작성해줘. 설명하지 말고, 아래 양식 그대로 출력해.

            이야기:
            (이야기 본문)

            문제 1:
            (문제1 질문)
            선택지:
            1. (선택지1)
            2. (선택지2)
            3. (선택지3)
            4. (선택지4)
            정답:
            (정답 번호)

            문제 2:
            (문제2 질문)
            선택지:
            1. (선택지1)
            2. (선택지2)
            3. (선택지3)
            4. (선택지4)
            정답:
            (정답 번호)
            """

            try:
                model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
                response = model.generate_content(prompt)
                raw_text = response.text

                # 파싱 시작
                story_part = raw_text.split("문제 1:")[0].replace("이야기:", "").strip()

                q1_block = raw_text.split("문제 1:")[1].split("문제 2:")[0].strip()
                q2_block = raw_text.split("문제 2:")[1].strip()

                # 문제 1 파싱
                q1_lines = q1_block.splitlines()
                q1_question = q1_lines[0].strip()
                q1_options = [line[3:].strip() for line in q1_lines[2:6]]
                q1_answer = int(q1_lines[7].replace("정답:", "").strip())

                # 문제 2 파싱
                q2_lines = q2_block.splitlines()
                q2_question = q2_lines[0].strip()
                q2_options = [line[3:].strip() for line in q2_lines[2:6]]
                q2_answer = int(q2_lines[7].replace("정답:", "").strip())

                # 세션에 저장
                st.session_state.story = story_part
                st.session_state.questions = [
                    {"question": q1_question, "options": q1_options, "answer": q1_answer},
                    {"question": q2_question, "options": q2_options, "answer": q2_answer},
                ]
                st.session_state.score = 0  # 점수 리셋

            except Exception as e:
                st.error(f"오류 발생: {e}")
                st.text_area("응답 내용:", raw_text)

# 생성된 이야기 및 문제 표시
if st.session_state.story:
    st.subheader("🌟 생성된 이야기 🌟")
    st.markdown(st.session_state.story)

if st.session_state.questions:
    st.subheader("✏️ 문제 풀어보기")

    for idx, q in enumerate(st.session_state.questions):
        st.markdown(f"**문제 {idx+1}: {q['question']}**")
        user_answer = st.radio(
            f"선택지를 골라주세요:",
            [f"{i+1}. {opt}" for i, opt in enumerate(q['options'])],
            key=f"user_answer_{idx}"
        )

        if st.button(f"정답 제출 (문제 {idx+1})", key=f"submit_{idx}"):
            selected_num = int(user_answer.split(".")[0])  # "1. 보기"에서 번호만 추출
            if selected_num == q['answer']:
                st.success("정답입니다! 🎉")
                st.session_state.score += 10
            else:
                correct_option = q['options'][q['answer']-1]
                st.error(f"틀렸어요! 정답은 '{correct_option}' 입니다.")

    st.header(f"🏆 최종 점수: {st.session_state.score}점 🏆")
