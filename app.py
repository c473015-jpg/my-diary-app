import datetime
import streamlit as st
from streamlit_calendar import calendar
from utils import calculate_dday, calculate_todo_rate, format_todos_for_calendar, get_korea_today

st.set_page_config(page_title="컬러풀 캘린더 & 다이어리", layout="wide")

# 탭 폰트 스타일 세팅
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 16px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📅 캘린더 & 다이어리")

# 🌟 한국 시간 기준으로 오늘 날짜 저장
k_today = get_korea_today()

# --- 세션 상태 초기화 ---
if "todos" not in st.session_state:
    st.session_state.todos = [
        {"날짜": datetime.date(2026, 6, 23), "시간": "14:00", "종료시간": "15:00", "내용": "과제 제출", "카테고리": "공부", "완료": True},
        # 🌟 시간은 "15:00" 그대로 두고, "종료시간": "18:00"을 새로 추가해 줍니다!
        {"날짜": datetime.date(2026, 6, 23), "시간": "15:00", "종료시간": "18:00", "내용": "비프 보강", "카테고리": "학교", "완료": False},
    ]
if "diaries" not in st.session_state:
    st.session_state.diaries = {}

# --- 사이드바: 디데이 ---
with st.sidebar:
    st.header("🎯 디데이")
    dday_name = st.text_input("제목", "종강")
    dday_date = st.date_input("날짜", datetime.date(2026, 6, 23))
    st.metric(label=dday_name, value=calculate_dday(dday_date))

# --- 핵심 해결 포인트: 상단에 고정된 날짜 조작 바 ---
st.markdown("---")
col_date1, col_date2 = st.columns([2, 5])
with col_date1:
    # 클릭 에러가 전혀 없는 스트림릿 공식 날짜 선택기
    sel_date_obj = st.date_input("📅 작업할 날짜를 선택하세요", k_today)
st.markdown("---")

# --- 메인 탭 구성 ---
tab1, tab2, tab3, tab4 = st.tabs(["🗓️ 월간 캘린더", "📋 할 일 관리", "✍️ 오늘의 일기", "📊 통계"])

# --- Tab 1: 진짜 달력 (조회용) ---
with tab1:
    # 🌟 내부에서 월간과 주간을 깔끔하게 서브 탭으로 한 번 더 나눕니다.
    sub_tab1, sub_tab2 = st.tabs(["📅 월간 보기", "⏳ 주간 보기"])
    
    events = format_todos_for_calendar(st.session_state.todos)
    
    # 1) 월간 보기 설정 (하루종일도 무조건 동그라미 점으로 표시)
    with sub_tab1:
        st.subheader("이번 달 일정 한눈에 보기")
        month_options = {
            "headerToolbar": {"left": "today prev,next", "center": "title", "right": ""},
            "initialView": "dayGridMonth",
            "initialDate": str(k_today),
            "selectable": False,
            "height": 600,
            "displayEventTime": False,
            "eventDisplay": "list-item",  # 👈 월간은 동그라미 점으로 고정!
        }
        calendar(events=events, options=month_options, key="month_calendar")
        
    # 2) 주간 보기 설정 (하루종일 일정이 상단 all-day 칸에 정상적으로 안착)
    with sub_tab2:
        st.subheader("이번 주 일정 시간표")
        week_options = {
            "headerToolbar": {"left": "today prev,next", "center": "title", "right": ""},
            "initialView": "timeGridWeek",  # 👈 주간 시간표 뷰로 고정
            "initialDate": str(k_today),
            "selectable": False,
            "height": 600,
            "displayEventTime": True,      # 주간에서는 시간을 보여주는 게 좋습니다.
            # 🌟 여기서는 eventDisplay를 빼서 라이브러리 기본 기능을 살립니다. 
            # 이렇게 해야 하루종일 일정이 맨 위 all-day 칸에 쏙 들어갑니다!
        }
        calendar(events=events, options=week_options, key="week_calendar")
        
# --- Tab 2: 할 일 관리 ---
with tab2:
    st.header(f"📌 {sel_date_obj.strftime('%m/%d')} 일정 관리")
    
    raw_todos = [t for t in st.session_state.todos if t["날짜"] == sel_date_obj]
    current_todos = sorted(raw_todos, key=lambda x: x["시간"])
    
    if current_todos:
        for i, todo in enumerate(current_todos):
            # 🌟 삭제 버튼 자리를 만들기 위해 비율을 [1.5, 3.5, 1, 1]로 쪼갭니다.
            c1, c2, c3, c4 = st.columns([1.5, 3.5, 1, 1])
            
            time_display = "all-day" if todo.get("하루종일", False) else f"{todo['시간']} ~ {todo.get('종료시간', todo['시간'])}"
            c1.write(f"🕒 {time_display}")
            
            color_codes = {"학교":"#9B59B6", "공부":"#3498DB", "약속":"#E67E22", "알바":"#E74C3C", "기타":"#95A5A6"}
            cat_color = color_codes.get(todo['카테고리'], "#000")
            c2.markdown(f"<span style='color:{cat_color}; font-weight:bold;'>[{todo['카테고리']}]</span> {todo['내용']}", unsafe_allow_html=True)
                
            todo["완료"] = c3.checkbox("완료", value=todo["완료"], key=f"todo_{i}_{todo['시간']}_{sel_date_obj}")
            
            # 🌟 4번째 칸에 삭제 버튼을 만들고, 누르면 전체 리스트에서 해당 일정을 제거합니다.
            if c4.button("🗑️ 삭제", key=f"del_{i}_{todo['시간']}_{sel_date_obj}"):
                st.session_state.todos.remove(todo)
                st.success("일정이 삭제되었습니다!")
                st.rerun()
    else:
        st.info(f"{sel_date_obj.strftime('%m/%d')}에 등록된 일정이 없습니다. 아래에서 새로 추가해 보세요!")

    st.divider()
    st.write("### ➕ 새 일정 추가")
    with st.form("add_todo_form", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns([1, 1, 2, 1]) 
        new_time = col1.text_input("시작 시간", "12:00")
        new_end_time = col2.text_input("종료 시간", "13:00") # 👈 종료 시간 입력칸 새로 추가!
        new_content = col3.text_input("내용")
        new_cat = col4.selectbox("카테고리", ["학교", "공부", "약속", "알바", "기타"])

     # 🌟 '하루 종일' 여부를 선택하는 체크박스를 폼 안에 추가합니다!
        is_allday = st.checkbox("📅 하루 종일 (체크하면 위클리 달력 맨 위 allday 칸에 들어갑니다)")
        
        if st.form_submit_button("추가하기"):
            if new_content:
                st.session_state.todos.append({
                    "날짜": sel_date_obj, 
                    "시간": new_time, 
                    "종료시간": new_end_time,
                    "내용": new_content, 
                    "카테고리": new_cat, 
                    "완료": False,
                    "하루종일": is_allday # 👈 여기에 체크 여부 저장!
                })
                st.success("일정이 추가되었습니다!")
                st.rerun()

# --- Tab 3: 다이어리 ---
with tab3:
    st.header(f"✍️ {sel_date_obj.strftime('%m/%d')} 일기장")
    current_diary = st.session_state.diaries.get(sel_date_obj, "")
    diary_input = st.text_area("오늘의 이야기를 기록하고 아래 버튼을 눌러 저장하세요.", value=current_diary, height=300)
    if st.button("일기 저장하기"):
        st.session_state.diaries[sel_date_obj] = diary_input
        st.success(f"{sel_date_obj.strftime('%m/%d')} 일기가 안전하게 저장되었습니다!")

# --- Tab 4: 통계 ---
with tab4:
    st.header(f"📊 {sel_date_obj.strftime('%m/%d')} 일정 분석")
    current_todos = [t for t in st.session_state.todos if t["날짜"] == sel_date_obj]
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