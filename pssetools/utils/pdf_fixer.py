import os
import sys
import argparse
import tempfile
import shutil

def ajusta_pdf(pdf_path):
    """
    Retira el uno en la parte inferior del PDF
    Recorta el PDF quitando los bordes que queden por un mal paginado
    """
    import fitz  # PyMuPDF
    # Remueve el unito al final del documento
    doc = fitz.open(pdf_path)
    for page_number, page in enumerate(doc, start=1):
        text_blocks = page.get_text("blocks")
        page_height = page.rect.height
        for block in text_blocks:
            x0, y0, x1, y1, text, _, _ = block
            if abs(y1 - page_height) < 10 and text.strip() == "1":
                print(text)
                page.add_redact_annot((x0, y0, x1, y1), "")
                page.apply_redactions()
    # Recorta todos los bordes sobrantes
    for page_number, page in enumerate(doc, start=1):
        content_rect = page.rect
        x0, y0, x1, y1 = page.cropbox
        paths = page.get_drawings()   
        x0 = None
        y0 = None
        x1 = None
        y1 = None
        for path in paths:
            u0, v0, u1, v1 = path["rect"]
            x0 = min(x0, u0) if x0 else u0
            y0 = min(y0, v0) if y0 else v0
            x1 = max(x1, u1) if x1 else u1
            y1 = max(y1, v1) if y1 else v1

        if x0 is not None and y0 is not None:
            page.set_cropbox(fitz.Rect(x0, y0, x1, y1))

    # Guardar temporalmente
    temp_fd, temp_path = tempfile.mkstemp(suffix=".pdf")
    os.close(temp_fd)
    
    doc.save(temp_path)
    doc.close()
    
    # Reemplaza el original con el arreglado
    shutil.move(temp_path, pdf_path)    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ajustador y Recortador de PDFs de PSS/E")
    parser.add_argument("--pdfs", nargs='+', required=True, help="Lista de archivos PDF a procesar")
    
    args = parser.parse_args()
    
    for pdf_file in args.pdfs:
        if os.path.exists(pdf_file):
            try:
                ajusta_pdf(pdf_file)
            except Exception as e:
                print("Error al ajustar el PDF '{}': {}".format(pdf_file, e))
        else:
            print("El archivo PDF no existe: {}".format(pdf_file))
