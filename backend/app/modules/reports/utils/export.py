from datetime import datetime
from io import BytesIO
from typing import Any, List, Literal

import openpyxl
import pandas as pd
from fastapi import Response


def export_csv_or_excel_file(
    report_data: List[Any],
    file_name: str,
    date_from: str,
    date_to: str,
    export_format: Literal["csv", "excel"],
):
    data_dicts = []

    if not report_data:
        df = pd.DataFrame()
    else:
        first_item = report_data[0]

        if hasattr(first_item, "model_dump"):
            # It's a Pydantic model
            data_dicts = [item.model_dump() for item in report_data]
        elif isinstance(first_item, dict):
            # Already dictionaries
            data_dicts = report_data
        else:
            # Try to convert to dict
            data_dicts = [dict(item) for item in report_data]
        
        df = pd.DataFrame(data_dicts)
        df = df.fillna("")

    # Create filename
    start_date = datetime.fromisoformat(date_from).strftime("%Y-%m-%d")
    end_date = datetime.fromisoformat(date_to).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")

    if export_format == "csv":
        # Export as CSV
        csv_content = df.to_csv(index=False, encoding="utf-8-sig")
        filename = (
            f"Itkan_{file_name}_{start_date}_to_{end_date}_generated_at_{today}.csv"
        )

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "text/csv; charset=utf-8-sig",
            },
        )

    elif export_format == "excel":
        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Report")

            # Formatting
            worksheet = writer.sheets["Report"]

            # Set column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    cell_value = str(cell.value) if cell.value is not None else ""
                    if len(cell_value) > max_length:
                        max_length = len(cell_value)

                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width

            # Make header row bold
            for cell in worksheet[1]:
                cell.font = openpyxl.styles.Font(bold=True)  # type: ignore

        excel_bytes = output.getvalue()
        output.close()

        filename = (
            f"Itkan_{file_name}_{start_date}_to_{end_date}_generated_at_{today}.xlsx"
        )

        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            },
        )
