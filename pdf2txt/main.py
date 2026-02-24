import PyPDF2

def simple_pdf_to_txt(pdf_path, txt_path=None):
    """Egyszerű PDF-ből TXT konvertáló"""
    if txt_path is None:
        txt_path = pdf_path.replace('.pdf', '.txt')
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            with open(txt_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)
            
            print(f"Konvertálás kész: {txt_path}")
    
    except Exception as e:
        print(f"Hiba: {e}")

# Használat
simple_pdf_to_txt("pdf2txt/sorsolas.pdf")