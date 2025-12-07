# resume_parser.py
import tempfile
import os
import re

def extract_text_from_file(file_or_path) -> str:
    """
    Robust text extractor that accepts:
      - a Flask `werkzeug.datastructures.FileStorage` uploaded file
      - a local file path string
      - a raw file-like object
    Returns extracted plain text (may be empty).
    """

    # Try to import FileStorage for type checking
    try:
        from werkzeug.datastructures import FileStorage
    except Exception:
        FileStorage = None

    # Helper to clean extracted text
    def clean_text(x: str) -> str:
        if not x:
            return ""
        x = str(x)
        x = re.sub(r"[\r\n\t]+", " ", x)
        x = re.sub(r"[^\x00-\x7F]+", " ", x)
        return x.strip()

    # Resolve input to a filesystem path (path variable)
    path = None
    tmp_dir = os.path.join(os.getcwd(), "temp_uploads")
    os.makedirs(tmp_dir, exist_ok=True)

    # Case 1: FileStorage (Flask uploaded file)
    if FileStorage is not None and isinstance(file_or_path, FileStorage):
        filename = (file_or_path.filename or "").lower()
        suffix = ".pdf" if filename.endswith(".pdf") else ".docx"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=tmp_dir) as tmp:
            file_or_path.stream.seek(0)
            tmp.write(file_or_path.read())
            tmp.flush()
            path = tmp.name

    # Case 2: path string
    elif isinstance(file_or_path, str):
        path = file_or_path

    # Case 3: raw file-like object
    else:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=tmp_dir) as tmp:
                # attempt to read from file-like object
                file_or_path.seek(0)
                tmp.write(file_or_path.read())
                tmp.flush()
                path = tmp.name
        except Exception as e:
            print("resume_parser: unsupported input type:", e)
            return ""

    text = ""

    # If PDF -> try pdfminer, PyPDF2, then OCR fallback
    if path.lower().endswith(".pdf"):
        # 1) pdfminer.six
        try:
            print("🔍 Trying pdfminer.six for text extraction...")
            from pdfminer.high_level import extract_text as pdf_extract
            text = pdf_extract(path) or ""
        except Exception as e:
            print("⚠️ PDFMiner failed:", e)

        # 2) PyPDF2 fallback
        if not text.strip():
            try:
                print("🔁 Trying PyPDF2 fallback...")
                from PyPDF2 import PdfReader
                reader = PdfReader(path)
                pages = [p.extract_text() or "" for p in reader.pages]
                text = " ".join(pages)
            except Exception as e:
                print("⚠️ PyPDF2 failed:", e)

        # 3) OCR fallback (requires pytesseract & pdf2image & pillow)
        if not text.strip():
            try:
                print("🧠 Trying OCR fallback (pytesseract)...")
                from pdf2image import convert_from_path
                import pytesseract
                from PIL import Image
                pages = convert_from_path(path)
                ocr_text = [pytesseract.image_to_string(page) for page in pages]
                text = " ".join(ocr_text)
            except Exception as e:
                print("⚠️ OCR fallback failed:", e)

    # DOCX or other text files
    else:
        try:
            print("📄 Trying docx2txt for DOCX...")
            import docx2txt
            text = docx2txt.process(path) or ""
        except Exception as e:
            print("⚠️ DOCX extraction failed:", e)
            # final fallback: plain text read
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except Exception as e2:
                print("⚠️ Plain text fallback failed:", e2)
                text = ""

    text = clean_text(text)

    # Debug preview
    print("\n========== RESUME TEXT EXTRACTED (preview) ==========\n")
    print(text[:800] or "[EMPTY TEXT! CHECK PDF TYPE OR OCR DEPENDENCIES]")
    print("\n===========================================\n")

    return text
