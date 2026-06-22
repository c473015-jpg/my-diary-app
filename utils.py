import datetime


def calculate_dday(target_date):
    """지정한 날짜까지 남은 디데이(D-Day)를 계산합니다."""
    today = datetime.date.today()
    delta = target_date - today

    if delta.days == 0:
        return "D-Day"
    elif delta.days > 0:
        return f"D-{delta.days}"
    else:
        return f"D+{abs(delta.days)}"


def calculate_todo_rate(todos):
    """등록된 일정(Todo)의 완료 달성률(%)을 계산합니다."""
    if not todos:
        return 0.0

    completed_count = 0
    for todo in todos:
        if todo.get("완료", False):  # 완료 체크박스가 True인 것만 개수 세기
            completed_count += 1

    return (completed_count / len(todos)) * 100