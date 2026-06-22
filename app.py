import datetime
import streamlit as st
from utils import calculate_dday, calculate_todo_rate

st.set_page_config(page_title="나의 일상 캘린더 & 다이어리", layout="wide")
st.title("📅 나의 일상 캘린더 & 다이어리")

# --- 세션 상태(Session State) 초기화 ---
# 일정(Todos) 저장소
if "todos" not in st.session_state:
    st.session_state.todos = [
        {"날짜": datetime.date.today(), "시간": "10:00", "내용": "스트림릿 프로젝트 만들기", "카테고리": "공부", "완료": True},
        {"날짜": datetime.date.today(), "시간": "18:00", "내용": "친구와 저녁 약속", "카테고리": "약속", "완료": False},
    ]

# 다이어리(Diaries) 저장소 (날짜를 Key로 하는 딕셔너리 구조)
if "diaries" not in st.session_state:
    st.session_state.diaries = {
        datetime.date.today(): "오늘부터 스트림릿으로 나만의 다이어리 웹 앱 생성을 시작했다! 아주 뿌듯하다."
    }

# --- 사이드바: 중요한 디데이(D-Day) 설정 ---
with st.sidebar:
    st.header("🎯 중요 마감일 (D-Day)")
    dday_name = st.text_input("디데이 제목", "기말고사 발표")
    dday_date = st.date_input("디데이 날짜", datetime.date.today() + datetime.timedelta(days=5))
    
    # utils.py의 디데이 계산 함수 호출
    dday_result = calculate_dday(dday_date)
    st.metric(label=dday_name, value=dday_result)

# --- 메인 화면: 날짜 선택 (미니 달력) ---
st.markdown("---")
selected_date = st.date_input("📆 조작하고 싶은 날짜를 선택하세요", datetime.date.today())
st.subheader(f"📌 {selected_date.strftime('%Y년 %m월 %d일')}의 기록")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📋 할 일 가이드 (Todo)", "✍️ 오늘의 일기장", "📊 나의 이행률 통계"])

# --- Tab 1: 할 일 관리 ---
with tab1:
    st.write("### 오늘의 일정")
    
    # 선택한 날짜에 해당하는 일정만 필터링
    current_todos = [t for t in st.session_state.todos if t["날짜"] == selected_date]
    
    # 일정 출력 및 완료 체크박스 조작
    if current_todos:
        for todo in current_todos:
            col1, col2, col3 = st.columns([1, 4, 1])
            with col1:
                st.write(f"⏱️ {todo['시간']}")
            with col2:
                # 완료 여부에 따라 텍스트 스타일 변경
                if todo["완료"]:
                    st.write(f"~~[{todo['카테고리']}] {todo['내용']}~~ (완료!)")
                else:
                    st.write(f"**[{todo['카테고리']}]** {todo['내용']}")
            with col3:
                # 체크박스를 누르면 즉시 세션 데이터의 완료 여부가 바뀜
                todo["완료"] = st.checkbox("완료", value=todo["완료"], key=f"check_{todo['내용']}_{todo['시간']}")
    else:
        st.info("오늘 등록된 일정이 없습니다. 아래에서 추가해 보세요!")
        
    st.markdown("---")
    st.write("### 새 일정 추가")
    col1, col2, col3 = st.columns([2, 4, 2])
    with col1:
        todo_time = st.text_input("시간 (예: 14:30)", "12:00")
    with col2:
        todo_content = st.text_input("할 일 내용 입력")
    with col3:
        todo_cat = st.selectbox("카테고리", ["학교", "공부", "약속", "알바", "기타"])
        
    if st.button("일정 추가"):
        if todo_content.strip():
            st.session_state.todos.append({
                "날짜": selected_date,
                "시간": todo_time,
                "내용": todo_content,
                "카테고리": todo_cat,
                "완료": False
            })
            st.success("새 일정을 추가했습니다!")
            st.rerun()

# --- Tab 2: 다이어리 기록 ---
with tab2:
    st.write("### 오늘 하루 기록하기")
    
    # 기존에 작성한 일기가 있다면 불러오기, 없으면 빈칸
    existing_diary = st.session_state.diaries.get(selected_date, "")
    
    diary_text = st.text_area("오늘 어떤 일이 있었나요? 자유롭게 적어보세요.", value=existing_diary, height=200)
    
    if st.button("일기 저장하기"):
        st.session_state.diaries[selected_date] = diary_text
        st.success("일기가 안전하게 저장되었습니다!")

# --- Tab 3: 통계 및 달성률 ---
with tab3:
    st.write("### 오늘의 계획 이행률")
    
    # 선택한 날짜의 일정들로 달성률 계산
    current_todos = [t for t in st.session_state.todos if t["날짜"] == selected_date]
    rate = calculate_todo_rate(current_todos)
    
    st.metric(label="오늘의 할 일 달성률", value=f"{rate:.1f}%")
    
    # 시각화용 가로 막대 차트 데이터 생성
    chart_data = [{"상태": "완료", "개수": len([t for t in current_todos if t["완료"]])},
                  {"상태": "미완료", "개수": len([t for t in current_todos if not t["완료"]])}]
    
    st.bar_chart(chart_data, x="상태", y="개수", horizontal=True, height=200)