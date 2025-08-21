import tkinter as tk
from tkinter import filedialog, messagebox
import PyPDF2
from openai import OpenAI

# Initialize OpenAI client (set your API key here or use environment variable)
client = OpenAI(api_key="your_openai_api_key_here")

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def summarize_and_explain(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # lighter & cheaper model, can switch to "gpt-4.1"
            messages=[
                {"role": "system", "content": "You are a legal assistant. Summarize the document and explain important legal terms in simple, easy-to-understand language."},
                {"role": "user", "content": text}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if file_path:
        extracted_text = extract_text_from_pdf(file_path)

        # Show extracted text in popup
        messagebox.showinfo("Extracted Text", extracted_text[:1000] + "\n...(truncated)")

        # Send to OpenAI for summary & explanation
        summary = summarize_and_explain(extracted_text)

        # Show summary in popup
        summary_window = tk.Toplevel(root)
        summary_window.title("Summary & Explanation")
        text_widget = tk.Text(summary_window, wrap="word", width=80, height=30)
        text_widget.insert("1.0", summary)
        text_widget.pack(expand=True, fill="both")

# Tkinter UI
root = tk.Tk()
root.title("PDF Scanner & Legal Summarizer")

btn = tk.Button(root, text="Choose PDF & Summarize", command=open_file, padx=20, pady=10)
btn.pack(pady=50)

root.mainloop()
