import io
import csv
import base64
from PyPDF2 import PdfReader
from docx import Document
import openpyxl


def process_pdf(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n\n"
    if not text.strip():
        return "Could not extract text from PDF."
    return text.strip()


def process_excel(file_bytes):
    workbook = openpyxl.load_workbook(io.BytesIO(file_bytes))
    text = ""
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        text += f"\nSheet: {sheet_name}\n\n"
        for row in sheet.iter_rows(values_only=True):
            row_data = [str(cell) if cell is not None else "" for cell in row]
            text += " | ".join(row_data) + "\n"
    return text.strip()


def process_word(file_bytes):
    doc = Document(io.BytesIO(file_bytes))
    text = ""
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text += paragraph.text + "\n\n"
    for table in doc.tables:
        text += "\n[TABLE]\n"
        for row in table.rows:
            row_data = [cell.text.strip() for cell in row.cells]
            text += " | ".join(row_data) + "\n"
    return text.strip()


def process_csv_file(file_bytes):
    content = file_bytes.decode("utf-8")
    reader = csv.reader(io.StringIO(content))
    text = ""
    for row in reader:
        text += " | ".join(row) + "\n"
    return text.strip()


def process_text(file_bytes):
    return file_bytes.decode("utf-8").strip()


def process_file(file_bytes, filename):
    extension = filename.lower().split(".")[-1]
    try:
        if extension == "pdf":
            return process_pdf(file_bytes), "pdf"
        elif extension in ["xlsx", "xls"]:
            return process_excel(file_bytes), "excel"
        elif extension in ["docx", "doc"]:
            return process_word(file_bytes), "word"
        elif extension == "csv":
            return process_csv_file(file_bytes), "csv"
        elif extension in ["txt", "md"]:
            return process_text(file_bytes), "text"
        elif extension in ["png", "jpg", "jpeg", "gif", "webp"]:
            return base64.b64encode(file_bytes).decode("utf-8"), "image"
        else:
            return f"Unsupported file: .{extension}", "error"
    except Exception as e:
        return f"Error: {str(e)}", "error"
