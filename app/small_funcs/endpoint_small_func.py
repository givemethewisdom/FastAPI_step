from datetime import datetime, time, timedelta


def calculate_work_time(
    start_dt: datetime,
    end_dt: datetime,
    work_start: time = time(8, 0),  # 8:00
    work_end: time = time(17, 0),  # 17:00
    work_days: set = {0, 1, 2, 3, 4},  # пн-пт (0-пн, 6-вс)
) -> timedelta:
    """
    Рассчитывает рабочее время между двумя датами.

    Args:
        start_dt: Дата начала
        end_dt: Дата окончания
        work_start: Начало рабочего дня
        work_end: Окончание рабочего дня
        work_days: Рабочие дни недели (0-пн, 6-вс)

    Returns:
        Общее рабочее время как timedelta
    """
    if start_dt > end_dt:
        return timedelta(0)

    total_work_time = timedelta()

    # Текущий день для итерации
    current_day_start = datetime.combine(start_dt.date(), work_start)
    if current_day_start < start_dt:
        current_day_start = start_dt

    # Пока не достигнем end_dt
    while current_day_start < end_dt:
        current_date = current_day_start.date()

        # Проверяем, рабочий ли это день
        if current_date.weekday() in work_days:
            # Определяем конец рабочего дня
            day_work_end = datetime.combine(current_date, work_end)

            # Фактический конец работы в этот день
            day_end = min(day_work_end, end_dt)

            # Добавляем время работы за этот день
            if current_day_start < day_end:
                total_work_time += day_end - current_day_start

        # Переходим к следующему дню
        next_day = current_date + timedelta(days=1)
        current_day_start = datetime.combine(next_day, work_start)

    return total_work_time
