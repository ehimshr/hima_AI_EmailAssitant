
import sys
import subprocess

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import PyPDF2
except ImportError:
    print("PyPDF2 not found, installing...")
    try:
        install("PyPDF2")
        import PyPDF2
    except Exception as e:
        print(f"Failed to install PyPDF2: {e}")
        sys.exit(1)

def read_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    pdf_path = r"C:\Users\Himanshu Shrivastava\Desktop\ik\git\hima_AI_EmailAssitant\AI-PoweredEmailAssistant.pdf"
    print(read_pdf(pdf_path))
