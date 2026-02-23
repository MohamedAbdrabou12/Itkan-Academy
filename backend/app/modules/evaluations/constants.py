from datetime import timedelta

MIN_GRADE = 0
MAX_GRADE = 10
EVALUATION_EDITING_TIMEFRAME = timedelta(2)

evaluation_score_weight_mapping = {
    "حفظ": 3,
    "مراجعة": 2,
    "سلوك": 1,
    "المظهر العام": 1,
}
