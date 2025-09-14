import PyPDF2
import os


def extract_metadata(pdf_path):
    metadata = {
        "num_pages": 0,
        "title": "Unknown",
        "author": "Unknown",
        "creator": "Unknown",
        "producer": "Unknown"
    }
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file, strict=False)

            if pdf_reader.is_encrypted:
                try:
                    pdf_reader.decrypt("")
                except Exception as e:
                    print(f"Skipping encrypted PDF: {pdf_path} ({e})")
                    return metadata

            metadata['num_pages'] = len(pdf_reader.pages)

            if pdf_reader.metadata:
                metadata['title'] = pdf_reader.metadata.get(
                    '/Title', 'Unknown')
                metadata['author'] = pdf_reader.metadata.get(
                    '/Author', 'Unknown')
                metadata['creator'] = pdf_reader.metadata.get(
                    '/Creator', 'Unknown')
                metadata['producer'] = pdf_reader.metadata.get(
                    '/Producer', 'Unknown')

    except Exception as e:
        print(f"Failed to extract metadata from {pdf_path}: {e}")

    return metadata


PDF_FILE = os.path.join(os.path.dirname(__file__), "Files",
                        "Prompt Engineering by Google.pdf")

metadata = extract_metadata(PDF_FILE)

print("=== PDF METADATA ===")
for key, value in metadata.items():
    print(f"{key.replace('_', ' ').title()}: {value}")
