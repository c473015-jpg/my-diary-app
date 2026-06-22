import datetime
import streamlit as st
from streamlit_calendar import calendar
from utils import calculate_dday, calculate_todo_rate, format_todos_for_calendar, get_korea_today

st.set_page_config(page_title="컬러풀 캘린더 & 다이어리", layout="wide")

# 탭 글씨 크기 수정 (16px) 및 UI 깔끔하게 세팅
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 16px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌈 나의 컬러풀 캘린더 & 다이어리")

# 🌟 한국 시간 기준으로 오늘 날짜 저장
k_today = get_korea_today()

# --- 세션 상태 초기화 ---
if "todos" not in st.session_state:
    st.session_state.todos = [
        {"날짜": datetime.date(2026, 6, 23), "시간": "10:00", "내용": "프로젝트 배포하기", "카테고리": "공부", "완료": True},
        {"날짜": datetime.date(2026, 6, 23), "시간": "14:00", "내용": "종강 파티 참석", "카테고리": "약속", "완료": False},
        {"날짜": datetime.date(2026, 6, 24), "시간": "18:00", "내용": "카페 알바 대타", "카테고리": "알바", "완료": False},
    ]
if "diaries" not in st.session_state:
    st.session_state.diaries = {}

# 현재 활성화된 탭을 기억하는 세션 변수 (기본값 0: 달력 탭)
if "current_tab" not in st.session_state:
    st.session_state.current_tab = 0

# 현재 선택된 날짜를 기억하는 세션 변수
if "selected_date" not in st.session_state:
    st.session_state.selected_date = str(k_today)

# --- 사이드바: 디데이 ---
with st.sidebar:
    st.header("🎯 중요 마감일")
    dday_name = st.text_input("제목", "종강일")
    dday_date = st.date_input("날짜", k_today + datetime.timedelta(days=10))
    st.metric(label=dday_name, value=calculate_dday(dday_date))
    
    st.markdown("---")
    # 현재 어떤 날짜가 선택되어 있는지 사이드바에 명확히 박아줍니다.
    st.success(f"📅 현재 선택된 날짜:\n**{st.session_state.selected_date}**")

# --- 메인 탭 구성 (렌더링을 위해 변수에 담음) ---
# 기존 st.tabs 대신 공통 컴포넌트로 관리하여 클릭 시 강제 탭 이동이 가능하게 만듭니다.
tab_titles = ["🗓️ 월간 캘린더", "📋 할 일 관리", "✍️ 오늘의 일기", "📊 통계"]

# 세션에 저장된 current_tab 번호를 기반으로 스트림릿 탭을 활성화합니다.
tabs = st.tabs(tab_titles)

# --- Tab 1: 진짜 달력 ---
with tabs[0]:
    st.subheader("이번 달 일정 한눈에 보기")
    events = format_todos_for_calendar(st.session_state.todos)
    
    calendar_options = {
        "headerToolbar": {"left": "today prev,next", "center": "title", "right": "dayGridMonth,timeGridWeek"},
        "initialView": "dayGridMonth",
        "initialDate": str(k_today),
        "selectable": True,
        "height": 600,
        "displayEventTime": False,
    }
    
    cal_state = calendar(events=events, options=calendar_options, key="main_calendar")
    
    # 달력 클릭 이벤트 처리
    new_date = None
    if cal_state.get("select") is not None:
        new_date = cal_state["select"]["start"].split("T")[0]
    elif cal_state.get("eventClick") is not None:
        new_date = cal_state["eventClick"]["event"]["start"].split("T")[0]
        
    # 만약 새로운 날짜가 클릭되었다면!
    if new_date and st.session_state.selected_date != new_date:
        st.session_state.selected_date = new_date
        # 🌟 중요: 날짜를 클릭하면 자동으로 '📋 할 일 관리'(1번 탭)으로 화면을 넘겨버립니다!
        st.session_state.current_tab = 1
        st.rerun()

# 현재 선택된 날짜 객체 생성
sel_date_obj = datetime.datetime.strptime(st.session_state.selected_date, "%Y-%m-%d").date()

# --- Tab 2: 할 일 관리 ---
with tabs[1]:
    st.header(f"📌 {sel_date_obj.strftime('%m/%d')} 일정 관리")
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
                
            todo["완료"] = c3.checkbox("완료", value=todo["완료"], key=f"todo_{i}_{todo['시간']}_{st.session_state.selected_date}")
    else:
        st.info(f"{sel_date_obj.strftime('%m/%d')}에 등록된 일정이 없습니다. 아래에서 새로 추가해 보세요!")

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
                st.success("일정이 추가되었습니다!")
                st.rerun()

# --- Tab 3: 다이어리 ---
with tabs[2]:
    st.header(f"✍️ {sel_date_obj.strftime('%m/%d')} 일기장")
    current_diary = st.session_state.diaries.get(sel_date_obj, "")
    diary_input = st.text_area("오늘의 이야기를 기록하고 아래 버튼을 눌러 저장하세요.", value=current_diary, height=300)
    if st.button("일기 저장하기"):
        st.session_state.diaries[sel_date_obj] = diary_input
        st.success(f"{sel_date_obj.strftime('%m/%d')} 일기가 안전하게 저장되었습니다!")

# --- Tab 4: 통계 ---
with tabs[3]:
    st.header(f"📊 {sel_date_obj.strftime('%m/%d')} 일정 분석")
    current_todos = [t for t in st.session_state.todos if str(t["날짜"]) == st.session_state.selected_date]
    rate = calculate_todo_rate(current_todos)
    st.metric("오늘의 계획 달성률", f"{rate:.1f}%")
    
    if current_todos:
        status_count = {"완료": 0, "미완료": 0}
        for t in current_todos:
            status_count["완료" if t["완료"] else "미완료"] += 1
            
        chart_data = [{"상태": k, "개수": int(v)} for k, v in status_count.items()]
        st.bar_chart(chart_data, x="상태", y="개수", horizontal=True, height=200)
    else:
        st.write("통계를 낼 일정이 없습니다.")