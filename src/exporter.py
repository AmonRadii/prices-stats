import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side

class ExcelExporter:
    """Отвечает исключительно за формирование и стилизацию XLSX файлов."""
    
    @staticmethod
    def export(filepath: str, items: list, stats: dict) -> bool:
        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Prices Analysis"

            # 1. Формирование данных
            ws.append(["Product", "Price"])
            
            for name, price in items:
                ws.append([name, price])

            ws.append([]) # Пустая строка-разделитель

            summary_rows = [
                ("Minimum Price", stats.get("min")),
                ("Maximum Price", stats.get("max")),
                ("Median Price", stats.get("median"))
            ]
            for label, val in summary_rows:
                if val is not None:
                    ws.append([label, val])

            # 2. Стилизация
            ExcelExporter._apply_styles(ws, items)

            wb.save(filepath)
            return True
            
        except Exception as e:
            print(f"Ошибка при сохранении Excel: {e}")
            return False

    @staticmethod
    def _apply_styles(ws, items: list):
        header_fill = PatternFill(start_color="FFFF99", end_color="FFFF99", fill_type="solid")
        summary_fill = PatternFill(start_color="D9D9D9", end_color="D9D9D9", fill_type="solid")
        bold_font = Font(bold=True)
        thin_border = Border(
            left=Side(style='thin', color='000000'), right=Side(style='thin', color='000000'),
            top=Side(style='thin', color='000000'), bottom=Side(style='thin', color='000000')
        )

        # Стили шапки
        for col in ['A1', 'B1']:
            ws[col].fill = header_fill
            ws[col].font = bold_font
            ws[col].border = thin_border

        # Стили итогов (последние 3 строки)
        max_row = ws.max_row
        for r in range(max_row - 2, max_row + 1):
            for col_letter in ['A', 'B']:
                cell = ws[f"{col_letter}{r}"]
                cell.fill = summary_fill
                cell.font = bold_font
                cell.border = thin_border

        # Ширина колонок
        max_product_length = max([len(name) for name, _ in items] + [15]) # 15 как минимум для заголовков
        ws.column_dimensions['A'].width = max_product_length + 3
        ws.column_dimensions['B'].width = 15