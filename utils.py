import datetime
import pytz  # 👈 시간대(Timezone) 라이브러리 추가

def get_korea_today():
    """대한민국(서울) 시간 기준으로 정확한 '오늘 날짜'를 반환합니다."""
    korea_tz = pytz.timezone("Asia/Seoul")
    # 현재 한국 시간의 날짜만 쏙 뽑아옵니다.
    return datetime.datetime.now(korea_tz).date()

def calculate_dday(target_date):
    """한국 지정한 날짜까지 남은 디데이를 계산합니다."""
    today = get_korea_today()  # 👈 기존 datetime.date.today() 대신 한국 시간 적용!
    delta = target_date - today
    if delta.days == 0: return "D-Day"
    elif delta.days > 0: return f"D-{delta.days}"
    else: return f"D+{abs(delta.days)}"

def calculate_todo_rate(todos):
    """일정 완료 달성률을 계산합니다."""
    if not todos: return 0.0
    completed_count = sum(1 for todo in todos if todo.get("완료", False))
    return (completed_count / len(todos)) * 100

def format_todos_for_calendar(todos):
    """일정 데이터를 카테고리별 색상을 입혀 달력 포맷으로 변환합니다."""
    COLOR_MAP = {
        "학교": "#9B59B6",      # 보라색
        "공부": "#3498DB",      # 파란색
        "약속": "#E67E22",      # 주황색
        "알바": "#E74C3C",      # 빨간색
        "기타": "#95A5A6"       # 회색
    }
    
    calendar_events = []
    for todo in todos:
        title_prefix = "✅ " if todo["완료"] else ""
        color = COLOR_MAP.get(todo["카테고리"], "#34495E")
        
        calendar_events.append({
            "title": f"{title_prefix}[{todo['카테고리']}] {todo['내용']}",
            "start": f"{todo['날짜']}T{todo['시간']}:00",
            "backgroundColor": color,
            "borderColor": color,
            "allDay": False
        })
    return calendar_events