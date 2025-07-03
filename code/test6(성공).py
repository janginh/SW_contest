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
if 'ranking' not in st.session_state:
    st.session_state.ranking = []

st.markdown("""
<style>
/* Streamlit 전체 앱에만 스타일 적용 */
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

/* 제목 */
.title {
    font-size: 50px;
    font-weight: 900;
    color: #ffffff;
    text-align: center;
    margin-bottom: 40px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}

/* 부제목 */
.subtitle {
    font-size: 30px;
    font-weight: bold;
    color: #ffffff;
    margin-top: 30px;
    text-align: center;
    text-shadow: 1px 1px 3px rgba(0,0,0,0.4);
}

/* 컨테이너 */
.container {
    background: rgba(255,255,255,0.9);
    border-radius: 20px;
    box-shadow: 0px 0px 15px rgba(0,0,0,0.2);
    padding: 30px;
    margin-bottom: 30px;
    transition: 0.5s;
}
.container:hover {
    box-shadow: 0px 0px 25px rgba(0,0,0,0.3);
    transform: translateY(-5px);
}

/* 버튼 스타일 */
.stButton>button {
    background: linear-gradient(45deg, #6a11cb, #2575fc);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 15px 30px;
    font-size: 20px;
    font-weight: bold;
    transition: 0.4s;
    margin-top: 10px;
    cursor: pointer;
}
.stButton>button:hover {
    background: linear-gradient(45deg, #8e2de2, #4a00e0);
    transform: scale(1.05);
    box-shadow: 0px 0px 20px 5px rgba(255,255,255,0.8);
}

/* 최종 점수 스타일 */
.final-score {
    font-size: 40px;
    font-weight: bold;
    text-align: center;
    color: #ff4081;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)


# 타이틀
st.markdown('<div class="title">🎇 좋아하는 걸 선택해봐! 🎇</div>', unsafe_allow_html=True)

# 주제 선택
options = ["애니메이션", "드라마", "축구", "영화"]
selected = st.radio("카테고리를 선택하거나 직접 입력해:", options + ["직접 입력"])

if selected == "직접 입력":
    keyword = st.text_input("주제를 입력해줘!")
else:
    keyword = selected

# 글과 문제 생성
if keyword:
    if st.button("✍️ 글과 문제 생성하기"):
        with st.spinner('✨ 글과 문제를 생성 중입니다...'):
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

                # 파싱
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

                st.balloons()

            except Exception as e:
                st.error(f"오류 발생: {e}")
                st.text_area("응답 내용:", raw_text)

# 이야기 표시
if st.session_state.story:
    st.markdown('<div class="subtitle">📖 생성된 이야기</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="container">{st.session_state.story}</div>', unsafe_allow_html=True)

# 문제 풀기
if st.session_state.questions:
    st.markdown('<div class="subtitle">✏️ 문제 풀기</div>', unsafe_allow_html=True)

    for idx, q in enumerate(st.session_state.questions):
        st.markdown(f"**문제 {idx+1}: {q['question']}**")
        user_answer = st.radio(
            "선택지를 골라주세요:",
            [f"{i+1}. {opt}" for i, opt in enumerate(q['options'])],
            key=f"user_answer_{idx}"
        )

        if st.button(f"✅ 정답 제출 (문제 {idx+1})", key=f"submit_{idx}"):
            selected_num = int(user_answer.split(".")[0])
            if selected_num == q['answer']:
                st.success("🎉 정답입니다! +10점 추가!")
                st.session_state.score += 10
                st.balloons()
            else:
                correct_option = q['options'][q['answer']-1]
                st.error(f"❌ 틀렸어요! 정답은 '{correct_option}' 입니다.")

# 최종 점수 및 랭킹
if st.session_state.questions:
    st.markdown('<div class="subtitle">🏆 최종 점수</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="final-score">🌟 {st.session_state.score} 점 🌟</div>', unsafe_allow_html=True)

    if st.session_state.score >= 100:
        st.success("🎆 불꽃놀이 발사!")
        st.markdown("""
        <script src="https://cdn.jsdelivr.net/npm/fireworks-js@2.1.0/dist/fireworks.js"></script>
        <div id="fireworks-container" style="position:fixed; top:0; left:0; width:100%; height:100%; pointer-events:none;"></div>
        <script>
        const container = document.getElementById('fireworks-container');
        const fireworks = new Fireworks(container, { 
          rocketsPoint: {min: 0, max: 100},
          opacity: 0.5,
          acceleration: 1.05,
          friction: 0.97,
          gravity: 1.5,
          particles: 50,
          trace: 3,
          explosion: 5
        });
        fireworks.start();
        </script>
        """, unsafe_allow_html=True)

    # 랭킹 등록
    if st.button("📋 랭킹 등록하기"):
        name = st.text_input("이름을 입력하세요:", key="name_input")
        if name:
            st.session_state.ranking.append((name, st.session_state.score))
            st.session_state.ranking = sorted(st.session_state.ranking, key=lambda x: x[1], reverse=True)

    if st.session_state.ranking:
        st.markdown('<div class="subtitle">🏅 랭킹</div>', unsafe_allow_html=True)
        st.table({
            "이름": [r[0] for r in st.session_state.ranking],
            "점수": [r[1] for r in st.session_state.ranking]
        })
