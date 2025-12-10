from typing import List, Dict, Any


def flatten_evaluation_data_for_export(
    report_data: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    grouped_data = {}

    for item in report_data:
        key = f"{item['student_id']}_{item['date']}"

        if key not in grouped_data:
            # Initialize base data for this student-date
            grouped_data[key] = {
                "branch_id": item["branch_id"],
                "branch_name": item["branch_name"],
                "class_id": item["class_id"],
                "class_name": item["class_name"],
                "student_id": item["student_id"],
                "student_name": item["student_name"],
                "date": item["date"],
            }

        eval_name = item.get("evaluation_name", "")
        grade = item.get("grade", "")

        if eval_name:
            clean_eval_name = eval_name.strip()
            grouped_data[key][clean_eval_name] = grade

    return list(grouped_data.values())
