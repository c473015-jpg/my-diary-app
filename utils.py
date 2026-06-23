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

def _format_time_to_pm(time_str):
    """'14:00' 형태의 문자열을 '2pm' 형태로 변환하는 함수입니다."""
    try:
        # 시간 문자열을 파이썬 시간 객체로 변환
        time_obj = datetime.datetime.strptime(time_str, "%H:%M")
        # %I(12시간 형식), %p(AM/PM)로 바꾸고 소문자화 한 뒤, 앞의 0과 분의 :00을 제거
        formatted = time_obj.strftime("%I:%M%p").lower().lstrip("0").replace(":00", "")
        return formatted
    except:
        return time_str
    
def format_todos_for_calendar(todos):
    """일정 데이터를 카테고리별 색상만 입혀 달력에 나오도록 변환합니다."""
    COLOR_MAP = {
        "학교": "#9B59B6", "공부": "#3498DB", "약속": "#E67E22", "알바": "#7E1D1D", "기타": "#95A5A6"
    }
    
    calendar_events = []
    for todo in todos:
        color = COLOR_MAP.get(todo.get("카테고리", "기타"), "#95A5A6")
        event_title = f"[{todo.get('카테고리', '기타')}] {todo.get('내용', '')}"
        
        # 🌟 핵심: 하루종일 일정이면 시간 데이터(T12:00 같은 값)를 절대 붙이지 않고 '날짜'만 보냅니다!
        # 이렇게 해야 라이브러리가 완벽하게 'all-day' 칸으로 인식합니다.
        if todo.get("하루종일", False):
            calendar_events.append({
                "title": event_title,
                "start": f"{todo['날짜']}",  # 뒤에 시간 정보를 생략합니다.
                "backgroundColor": color,
                "borderColor": color,
                "allDay": True  # 위클리 달력 상단 allday 칸 진입 보장
            })
        else:
            calendar_events.append({
                "title": event_title,
                "start": f"{todo['날짜']}T{todo['시간']}:00",
                "end": f"{todo['날짜']}T{todo.get('종료시간', todo['시간'])}:00",
                "backgroundColor": color,
                "borderColor": color,
                "allDay": False
            })
            
    return calendar_events