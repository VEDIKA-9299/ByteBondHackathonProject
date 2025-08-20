import tkinter as tk
from tkinter import filedialog
import PyPDF2

def extract_text_from_pdf():
    # Open file dialog for PDF selection
    file_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not file_path:
        print("No file selected.")
        return

    # Open and read PDF
    try:
        with open(file_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""  # extract text from each page
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return

    # Display extracted text
    text_window = tk.Toplevel(root)
    text_window.title("Extracted Text")
    text_box = tk.Text(text_window, wrap="word", width=100, height=40)
    text_box.insert("1.0", text)
    text_box.pack(expand=True, fill="both")

# GUI setup
root = tk.Tk()
root.title("PDF Text Extractor")

open_button = tk.Button(root, text="Choose PDF & Extract Text", command=extract_text_from_pdf)
open_button.pack(pady=20)

root.mainloop()
