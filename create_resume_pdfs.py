import os
from database import RESUME_SEED_DATA

RESUMES_DIR = os.path.join(os.path.dirname(__file__), "resumes")
os.makedirs(RESUMES_DIR, exist_ok=True)

def generate_pdf_native(filename, title_str, text_content):
    """Generates a valid, native PDF 1.4 file directly in Python with zero dependencies."""
    lines = text_content.strip().split('\n')
    
    # Escape parentheses and backslashes for PDF text stream
    pdf_text_cmds = ["BT", "/F1 9 Tf", "12 TL", "36 756 Td"]
    
    for line in lines:
        clean = line.strip().replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        if not clean:
            pdf_text_cmds.append("T*")
        else:
            # Handle long lines truncation for simple page layout
            if len(clean) > 110:
                clean = clean[:107] + "..."
            pdf_text_cmds.append(f"({clean}) Tj T*")
            
    pdf_text_cmds.append("ET")
    stream_data = "\n".join(pdf_text_cmds).encode('latin1', 'replace')
    stream_len = len(stream_data)

    pdf_body = f"""%PDF-1.4
1 0 obj
<</Type /Catalog /Pages 2 0 R>>
endobj
2 0 obj
<</Type /Pages /Kids [3 0 R] /Count 1>>
endobj
3 0 obj
<</Type /Page /Parent 2 0 R /Resources <</Font <</F1 4 0 R>>>> /MediaBox [0 0 612 792] /Contents 5 0 R>>
endobj
4 0 obj
<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>
endobj
5 0 obj
<</Length {stream_len}>>
stream
""".encode('latin1') + stream_data + f"""
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000056 00000 n 
0000000111 00000 n 
0000000236 00000 n 
0000000307 00000 n 
trailer
<</Size 6 /Root 1 0 R>>
startxref
{307 + stream_len + 25}
%%EOF""".encode('latin1')

    with open(filename, 'wb') as f:
        f.write(pdf_body)
    print(f"Generated PDF Resume: {filename}")

def generate_all_resumes():
    for seed in RESUME_SEED_DATA:
        v_name = seed["vertical_name"].replace("/", "_").replace(" ", "_")
        pdf_path = os.path.join(RESUMES_DIR, f"{v_name}_Resume_Rounak_Raman.pdf")
        generate_pdf_native(pdf_path, seed["vertical_name"], seed["resume_text"])

if __name__ == "__main__":
    generate_all_resumes()
