import datetime
import streamlit as st
from streamlit_calendar import calendar
# 👈 utils에서 get_korea_today 함수도 함께 가져옵니다.
from utils import calculate_dday, calculate_todo_rate, format_todos_for_calendar, get_korea_today

st.set_page_config(page_title="캘린더 & 다이어리", layout="wide")

st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 16px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📅 캘린더 & 다이어리")

# 🌟 한국 시간 기준으로 오늘 날짜 저장해두기
k_today = get_korea_today()

# --- 세션 상태 초기화 ---
if "todos" not in st.session_state:
    st.session_state.todos = [
        {"날짜": datetime.date(2026, 6, 23), "시간": "14:00", "내용": "과제 제출", "카테고리": "공부", "완료": True},
        {"날짜": datetime.date(2026, 6, 23), "시간": "15:00", "내용": "비프 보강", "카테고리": "학교", "완료": False},
    ]
if "diaries" not in st.session_state:
    st.session_state.diaries = {}
if "selected_date" not in st.session_state:
    st.session_state.selected_date = str(k_today)  # 👈 여기도 한국 오늘 날짜로 초기화!

# --- 사이드바: 디데이 ---
with st.sidebar:
    st.header("🎯 중요 마감일")
    dday_name = st.text_input("제목", "종강일")
    dday_date = st.date_input("날짜", k_today + datetime.timedelta(days=10))
    st.metric(label=dday_name, value=calculate_dday(dday_date))
    st.info("💡 탭1의 달력에서 날짜를 클릭하면 해당 날짜의 일기/일정 탭으로 자동 이동합니다.")

# --- 메인 탭 구성 ---
tab1, tab2, tab3, tab4 = st.tabs(["🗓️ 월간 캘린더", "📋 일정 관리", "✍️ 오늘의 일기", "📊 통계"])

# --- Tab 1: 진짜 달력 ---
with tab1:
    st.subheader("이번 달 일정 한눈에 보기")
    events = format_todos_for_calendar(st.session_state.todos)
    
    calendar_options = {
        "headerToolbar": {"left": "today prev,next", "center": "title", "right": "dayGridMonth,timeGridWeek"},
        "initialView": "dayGridMonth",
        "initialDate": str(k_today),
        "selectable": True,
        "height": 600,
    }
    
    cal_state = calendar(events=events, options=calendar_options, key="main_calendar")
    
    if cal_state.get("select") is not None:
        st.session_state.selected_date = cal_state["select"]["start"].split("T")[0]
    elif cal_state.get("eventClick") is not None:
        st.session_state.selected_date = cal_state["eventClick"]["event"]["start"].split("T")[0]

# 현재 선택된 날짜 객체 생성
sel_date_obj = datetime.datetime.strptime(st.session_state.selected_date, "%Y-%m-%d").date()

# --- Tab 2: 할 일 관리 ---
with tab2:
    st.header(f"📌 {sel_date_obj.strftime('%m/%d')} 일정")
    current_todos = [t for t in st.session_state.todos if str(t["날짜"]) == st.session_state.selected_date]
    
    if current_todos:
        for i, todo in enumerate(current_todos):
            c1, c2, c3 = st.columns([1, 4, 1])
            c1.write(f"🕒 {todo['시간']}")
            color_codes = {"학교":"#9B59B6", "공부":"#3498DB", "약속":"#E67E22", "알바":"#E74C3C", "기타":"#95A5A6"}
            cat_color = color_codes.get(todo['카테고리'], "#000")
            
            content_display = f"<span style='color:{cat_color}; font-weight:bold;'>[{todo['카테고리']}]</span> {todo['내용']}"
            if todo["완료"]:
                c2.markdown(f"~~{content_display}~~", unsafe_allow_html=True)
            else:
                c2.markdown(content_display, unsafe_allow_html=True)
                
            todo["완료"] = c3.checkbox("완료", value=todo["완료"], key=f"todo_{i}_{todo['시간']}")
    else:
        st.info("등록된 일정이 없습니다.")

    st.divider()
    st.write("### ➕ 새 일정 추가")
    with st.form("add_todo_form", clear_on_submit=True):
        col1, col2, col3 = st.columns([1, 2, 1])
        new_time = col1.text_input("시간", "12:00")
        new_content = col2.text_input("내용")
        new_cat = col3.selectbox("카테고리", ["학교", "공부", "약속", "알바", "기타"])
        if st.form_submit_button("추가하기"):
            if new_content:
                st.session_state.todos.append({
                    "날짜": sel_date_obj, "시간": new_time, "내용": new_content, "카테고리": new_cat, "완료": False
                })
                st.success("추가되었습니다!")
                st.rerun()

# --- Tab 3: 다이어리 ---
with tab3:
    st.header(f"✍️ {sel_date_obj.strftime('%m/%d')} 일기")
    current_diary = st.session_state.diaries.get(sel_date_obj, "")
    diary_input = st.text_area("오늘의 이야기를 기록하세요", value=current_diary, height=300)
    if st.button("일기 저장"):
        st.session_state.diaries[sel_date_obj] = diary_input
        st.success("저장 완료!")

# --- Tab 4: 통계 ---
with tab4:
    st.header(f"📊 {sel_date_obj.strftime('%m/%d')} 분석")
    current_todos = [t for t in st.session_state.todos if str(t["날짜"]) == st.session_state.selected_date]
    rate = calculate_todo_rate(current_todos)
    st.metric("오늘의 계획 달성률", f"{rate:.1f}%")
    
    if current_todos:
        status_count = {"완료": 0, "미완료": 0}
        for t in current_todos:
            status_count["완료" if t["완료"] else "미완료"] += 1
        st.bar_chart([{"상태": k, "개수": v} for k, v in status_count.items()], x="상태", y="개수")
    else:
        st.write("통계를 낼 일정이 없습니다.")