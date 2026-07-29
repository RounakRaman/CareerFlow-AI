import os
from database import RESUME_SEED_DATA

RESUMES_DIR = os.path.join(os.path.dirname(__file__), "resumes")
os.makedirs(RESUMES_DIR, exist_ok=True)

def generate_clean_pdf(filename, title_str, text_content):
    """Generates a clean PDF file with proper bullet points and NO line truncation."""
    # Replace unicode bullet points with standard bullet dash so it doesn't render as '?'
    clean_text = text_content.replace('•', '-').replace('\u2022', '-')
    lines = clean_text.strip().split('\n')
    
    pdf_text_cmds = [
        "BT",
        "/F1 9 Tf",
        "12 TL",
        "36 756 Td"
    ]
    
    for line in lines:
        l_str = line.strip().replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        if not l_str:
            pdf_text_cmds.append("T*")
        else:
            # Wrap long lines across multiple PDF lines without truncating with '...'
            max_len = 100
            while len(l_str) > max_len:
                # Find space near max_len
                space_idx = l_str.rfind(' ', 0, max_len)
                if space_idx == -1:
                    space_idx = max_len
                chunk = l_str[:space_idx]
                pdf_text_cmds.append(f"({chunk}) Tj T*")
                l_str = l_str[space_idx:].strip()
            if l_str:
                pdf_text_cmds.append(f"({l_str}) Tj T*")
            
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
        # ONLY create if file does NOT already exist, so user's uploaded real PDFs are NEVER overwritten!
        if not os.path.exists(pdf_path):
            generate_clean_pdf(pdf_path, seed["vertical_name"], seed["resume_text"])

if __name__ == "__main__":
    generate_all_resumes()
