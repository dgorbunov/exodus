import requests
from pypdf import PdfReader
import os
# Step 1: Download the PDF

def get_pdf_and_text(url, path, txtpath):

    response = requests.get(url)
    if response.status_code == 200:
        with open(path, 'wb') as f:
            f.write(response.content)
            print(f"PDF saved to {path}")
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")

    try:
        out = ""
        reader = PdfReader(path)
        for page in reader.pages:
            out = page.extract_text()
            with open(f'{txtpath}', 'a') as f:
                f.write(out)
    except Exception as e:
        print(f"Failed to read PDF: {e}")
    finally:
        os.remove(path)
if __name__ == "__main__":
    get_pdf_and_text("https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-215.pdf", "nist.pdf", 'nist.txt')

