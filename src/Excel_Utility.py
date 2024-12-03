import re
import io

# import xlsxwriter


def apply_worksheet_with_basic_format(worksheet, format):
    worksheet.set_column(0, 52, None, format)
    worksheet.hide_gridlines(2)
    worksheet.freeze_panes(32, 20)
    # worksheet.protect()
    return worksheet


def add_horizontal_border(worksheet, row, colRange, format):
    start_col = colRange.split(":")[0]
    end_col = colRange.split(":")[-1]
    col_name = {
        i - 102: chr(i).upper() for i in range(ord(start_col), ord(end_col) + 1)
    }
    for i in col_name.keys():
        # print(f'{col_name[i]}18')
        worksheet.write(f"{col_name[i]}{row}", "", format)
    return worksheet


def add_vertical_border(worksheet, rowRange, col, format):
    # col = ord(col)-65
    start_row = int(rowRange.split(":")[0])
    end_row = int(rowRange.split(":")[-1])
    # Apply border to the specified column across the specified row range
    for row in range(start_row, end_row + 1):
        worksheet.write(f"{col}{row}", "", format)  # Use the desired border format
    return worksheet


def cell_format(worksheet, refCell, format):
    worksheet.write(refCell, "", format)
    return worksheet


def getCellsRef(cellRef="D3:P28"):
    start_row = int(re.search(r"\d+", cellRef.split(":")[0]).group())
    end_row = int(re.search(r"\d+", cellRef.split(":")[-1]).group())
    start_col = re.search(r"[A-Za-z]+", cellRef.split(":")[0]).group()
    end_col = re.search(r"[A-Za-z]+", cellRef.split(":")[-1]).group()
    colRange = f"{start_col}:{end_col}"
    rowRange = f"{start_row}:{end_row}"
    top_left_corner = f"{start_col}{start_row}"
    bottom_left_corner = f"{start_col}{end_row}"
    top_right_corner = f"{end_col}{start_row}"
    bottom_right_corner = f"{end_col}{end_row}"
    return (
        start_row,
        end_row,
        start_col,
        end_col,
        colRange,
        rowRange,
        top_left_corner,
        bottom_left_corner,
        top_right_corner,
        bottom_right_corner,
    )


def add_title(worksheet, range, text, format, multiple_cell=True):
    if multiple_cell:
        worksheet.merge_range(range, text, format)
        return worksheet
    worksheet.write(range, text, format)
    return worksheet


def add_creteria(worksheet, criteria, row, title_col, value_col, format):
    # row = int(re.search(r'\d+', ref_cell).group())
    # col = re.search(r'[A-Za-z]+', ref_cell).group()
    for k, v in criteria.items():
        worksheet.write(f"{title_col}{row}", k.replace("_", " ").upper(), format)
        worksheet.write(f"{value_col}{row}", v, format)
        row += 1
    return worksheet


def write_text(worksheet, text, ref_cell, format):
    # Use regex to extract the integer from start_cel
    row = int(re.search(r"\d+", ref_cell).group())
    col = re.search(r"[A-Za-z]+", ref_cell).group()
    # text = self.disclaimer
    if isinstance(text, io.TextIOWrapper):
        text = text.read()  # Read the file content into a string

    for line in text.split("\n"):
        line = line.strip()
        worksheet.write(f"{col}{row}", line, format)
        row += 1
    return worksheet


def build_metrics_text(header="Prix d'Adjudication"):
    text = """Décote
    Cout de l'Opération
    Probabilité D'Obtention
    Plus Value
    Rentabilité Potentielle"""
    return f"{header}\n{ text}"
