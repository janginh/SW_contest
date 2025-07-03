import streamlit as st
import os
import google.generativeai as genai
import random
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Gemini API 키 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 세션 상태 초기화
if 'page' not in st.session_state:
    st.session_state.page = 'ranking'  # 처음은 랭킹 화면
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'story' not in st.session_state:
    st.session_state.story = ""
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'word_question' not in st.session_state:
    st.session_state.word_question = {}
if 'ranking' not in st.session_state:
    st.session_state.ranking = []

# 🌈 스타일 적용
st.markdown(""" 
<style>
.stApp {
    animation: gradientBG 15s ease infinite;
    background: linear-gradient(-45deg, #ff9a9e, #fad0c4, #ffdde1, #c3ecf5);
    background-size: 600% 600%;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    padding: 2rem;
    min-height: 100vh;
}
@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
.title {
    font-size: 50px;
    font-weight: 900;
    color: #ffffff;
    text-align: center;
    margin-bottom: 40px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}
.subtitle {
    font-size: 30px;
    font-weight: bold;
    color: #ffffff;
    margin-top: 30px;
    text-align: center;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.4);
}
.container {
    background: rgba(255,255,255,0.9);
    border-radius: 20px;
    box-shadow: 0px 0px 15px rgba(0,0,0,0.2);
    padding: 30px;
    margin-bottom: 30px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# 페이지: 랭킹 화면
# ---------------------------
if st.session_state.page == 'ranking':
    st.markdown('<div class="title">🏅 랭킹 테이블</div>', unsafe_allow_html=True)

    if st.session_state.ranking:
        st.dataframe({
            "이름": [r[0] for r in st.session_state.ranking],
            "점수": [r[1] for r in st.session_state.ranking]
        })
    else:
        st.write("등록된 랭킹이 없습니다.")

    if st.button("📖 글 보러 가기"):
        st.session_state.page = 'select_topic'

# ---------------------------
# 페이지: 주제 선택 화면
# ---------------------------
elif st.session_state.page == 'select_topic':
    st.markdown('<div class="title">🎇 좋아하는 걸 선택해봐! 🎇</div>', unsafe_allow_html=True)

    options = ["애니메이션", "드라마", "축구", "영화"]
    selected = st.radio("카테고리를 선택하거나 직접 입력해:", options + ["직접 입력"])

    if selected == "직접 입력":
        keyword = st.text_input("주제를 입력해줘!")
    else:
        keyword = selected
    # 주제 선택 화면 (select_topic 페이지) 수정 부분

    if keyword and st.button("✍️ 글과 문제 생성하기"):
        with st.spinner('✨ 글과 문제를 생성 중입니다...'):
            prompt = f"""
'{keyword}'를 주제로 초등학생이 이해할 수 있도록 쉬운 단어로 200자 이상 300자 이내 짧은 이야기를 써줘.
중간중간에 초등학생들이 모를법한 단어를 포함해서 만들어줘.
그 이야기 내용을 바탕으로 문제 2개를 만들고,
추가로 등장했던 어려운 단어 중 하나를 골라 단어 퀴즈 문제도 만들어줘.
형식은 아래처럼 출력해. 설명하지 말고 양식만 지켜:

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

단어 문제:
(단어 문제 질문)
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

            # 파싱
            story_part = raw_text.split("문제 1:")[0].replace("이야기:", "").strip()
            q1_block = raw_text.split("문제 1:")[1].split("문제 2:")[0].strip()
            q2_block = raw_text.split("문제 2:")[1].split("단어 문제:")[0].strip()
            word_block = raw_text.split("단어 문제:")[1].strip()

            # 문제1
            q1_lines = q1_block.splitlines()
            q1_question = q1_lines[0].strip()
            q1_options = [line[3:].strip() for line in q1_lines[2:6]]
            q1_answer = int(q1_lines[7].replace("정답:", "").strip())

            # 문제2
            q2_lines = q2_block.splitlines()
            q2_question = q2_lines[0].strip()
            q2_options = [line[3:].strip() for line in q2_lines[2:6]]
            q2_answer = int(q2_lines[7].replace("정답:", "").strip())

            # 단어 문제
            w_lines = word_block.splitlines()
            w_question = w_lines[0].strip()
            w_options = [line[3:].strip() for line in w_lines[2:6]]
            w_answer = int(w_lines[7].replace("정답:", "").strip())

            # 세션에 저장
            st.session_state.story = story_part
            st.session_state.questions = [
                {"question": q1_question, "options": q1_options, "answer": q1_answer},
                {"question": q2_question, "options": q2_options, "answer": q2_answer},
            ]
            st.session_state.word_question = {
                "question": w_question,
                "options": w_options,
                "answer": w_answer
            }
            st.session_state.score = 0
            st.session_state.page = 'story'
            st.balloons()

        except Exception as e:
            st.error(f"오류 발생: {e}")

    '''if keyword and st.button(✍️ 글과 문제 생성하기"):
        with st.spinner('✨ 글과 문제를 생성 중입니다...'):
            prompt = f"""
            '{keyword}'를 주제로 초등학생이 이해할 수 있도록 쉬운 단어로 200자 이상 300자 이내 짧은 이야기를 써줘.
            중간중간에 초등학생들이 모를법한 단어를 포함해서 만들어줘.
            그리고 그 이야기 내용을 바탕으로 문제 2개를 만들어줘.
            
            아래처럼 출력해:

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

                story_part = raw_text.split("문제 1:")[0].replace("이야기:", "").strip()
                q1_block = raw_text.split("문제 1:")[1].split("문제 2:")[0].strip()
                q2_block = raw_text.split("문제 2:")[1].strip()

                q1_lines = q1_block.splitlines()
                q1_question = q1_lines[0].strip()
                q1_options = [line[3:].strip() for line in q1_lines[2:6]]
                q1_answer = int(q1_lines[7].replace("정답:", "").strip())

                q2_lines = q2_block.splitlines()
                q2_question = q2_lines[0].strip()
                q2_options = [line[3:].strip() for line in q2_lines[2:6]]
                q2_answer = int(q2_lines[7].replace("정답:", "").strip())

                st.session_state.story = story_part
                st.session_state.questions = [
                    {"question": q1_question, "options": q1_options, "answer": q1_answer},
                    {"question": q2_question, "options": q2_options, "answer": q2_answer},
                ]
                st.session_state.score = 0

                # 단어 문제
                words = [w.strip(",. ") for w in story_part.split() if len(w) > 1]
                selected_word = random.choice(words)
                word_defs = random.sample([
                    "행복한 상태", "슬픈 감정", "빠르게 움직이는 것", "만드는 행위", 
                    "빛나는 물체", "물에 관련된 것", "음식 요리", "휴식 취함"
                ], 3)
                correct_def = "문맥상 올바른 뜻"

                st.session_state.word_question = {
                    "word": selected_word,
                    "options": [correct_def] + word_defs,
                    "answer": correct_def
                }
                random.shuffle(st.session_state.word_question['options'])

                st.session_state.page = 'story'

            except Exception as e:
                st.error(f"오류 발생: {e}")'''

# ---------------------------
# 페이지: 이야기 & 문제 화면
# ---------------------------
elif st.session_state.page == 'story':
    st.markdown('<div class="subtitle">📖 생성된 이야기</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="container">{st.session_state.story}</div>', unsafe_allow_html=True)

    st.markdown('<div class="subtitle"✏️ 문제 풀기</div>', unsafe_allow_html=True)

    for idx, q in enumerate(st.session_state.questions):
        st.markdown(f"**문제 {idx+1} (30점)**: {q['question']}")
        user_answer = st.radio(
            "선택지를 골라주세요:",
            [f"{i+1}. {opt}" for i, opt in enumerate(q['options'])],
            key=f"radio_{idx}"
        )

        if f"wrong_attempts_{idx}" not in st.session_state:
            st.session_state[f"wrong_attempts_{idx}"] = 0

        if st.button(f"✅ 정답 제출 (문제 {idx+1})", key=f"submit_{idx}"):
            if user_answer:
                selected_num = int(user_answer.split(".")[0])
                if selected_num == q['answer']:
                    st.success("🎉 정답입니다! +30점 추가!")
                    st.session_state.score += 30
                    st.balloons()
                else:
                    st.session_state[f"wrong_attempts_{idx}"] += 1
                    st.session_state.score -= 1
                    st.error(f"❌ 틀렸어요! (-1점) 시도 {st.session_state[f'wrong_attempts_{idx}']}회차")

                    if st.session_state[f"wrong_attempts_{idx}"] >= 3:
                        correct_option = q['options'][q['answer']-1]
                        st.warning(f"정답: {correct_option}")

    st.markdown('<div class="subtitle">📚 단어 문제</div>', unsafe_allow_html=True)
    word = st.session_state.word_question["word"]
    options = st.session_state.word_question["options"]
    answer = st.session_state.word_question["answer"]

    user_word_answer = st.radio(f"'{word}'의 뜻을 골라주세요: (10점)", options, key="word_quiz")
    if st.button("✅ 정답 제출 (단어 문제)"):
        if user_word_answer == answer:
            st.success("🎉 정답입니다! +10점 추가!")
            st.session_state.score += 10
            st.balloons()
        else:
            st.session_state.score -= 1
            st.error("❌ 틀렸어요! (-1점 감점)")


#랭킹 등록
    st.markdown(f'<div class="final-score">🌟 현재 점수: {st.session_state.score} 점 🌟</div>', unsafe_allow_html=True)

    name = st.text_input("이름을 입력하세요:", key="name_input")
    if st.button("📋 랭킹 등록하기"):
        if name:
            st.session_state.ranking.append((name, st.session_state.score))
            st.session_state.ranking = sorted(st.session_state.ranking, key=lambda x: x[1], reverse=True)
            st.session_state.page = 'ranking'
        else:
            st.warning("이름을 입력해주세요!")

    # ✅ 여기 추가! 처음으로 돌아가기 버튼
    if st.button("🏠 처음으로 돌아가기 (랭킹 화면)"):
        st.session_state.page = 'ranking'
