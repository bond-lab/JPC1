# Describe and document your code
import pdfplumber
import re

def extract_metaphor_mappings(pdf_path):
    mappings = []
    # Regex to capture patterns like "X is Y" or "X are Y" (common metaphor formulations)
    # This is a heuristic; MetaNet papers often list them explicitly in tables or capitalized text.
    metaphor_pattern = re.compile(r'\b([A-Z]+)\s+(?:IS|ARE)\s+([A-Z]+)\b')

    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Analyzing {pdf_path} with {len(pdf.pages)} pages...")
            
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                
                # 1. Search for Capitalized Metaphor Mappings (e.g., POVERTY IS A DISEASE)
                matches = metaphor_pattern.findall(text)
                for source, target in matches:
                    # Filter out noise (short words)
                    if len(source) > 3 and len(target) > 3:
                        mappings.append({
                            "Target": source, 
                            "Source": target, 
                            "Context": "Capitalized Pattern",
                            "Page": page_num + 1
                        })

                # 2. Look for explicit mentions of "Source Domain" and "Target Domain"
                # (Simple text scraping for proximity)
                if "Source Domain" in text and "Target Domain" in text:
                    # Extract lines that might contain the mapping
                    lines = text.split('\n')
                    for line in lines:
                        if "→" in line or "map" in line.lower():
                            mappings.append({
                                "Raw_Line": line.strip(),
                                "Context": "Explicit Mapping Description",
                                "Page": page_num + 1
                            })

    except Exception as e:
        print(f"Error processing PDF: {e}")
        return []

    return mappings

# --- Usage ---
# mappings = extract_metaphor_mappings("W15-1405.pdf")
# for m in mappings:
#     print(m)



# Note on PDF Extraction: In the MetaNet papers, mappings are often discussed in the body text or shown in figures (like Figure 1 in W15-1405). Automated extraction works best on the capitalized conventions (e.g., "LOVE IS A JOURNEY"). For the most accurate data, parsing the OWL/RDF data (as shown in the previous turn) is preferred over PDF scraping because the PDF representation is unstructured.


