# Describe and document your code
import pdfplumber
import re

def extract_metaphor_mappings_v2(pdf_path):
    mappings =
    
    # 1. Improved Regex: Captures multi-word uppercase phrases
    # Example matches: "ARGUMENT IS WAR", "THE MIND IS A BODY"
    metaphor_pattern = re.compile(r'\b([A-Z]+(?:\s+[A-Z]+)*)\s+(?:IS|ARE)\s+([A-Z]+(?:\s+[A-Z]+)*)\b')

    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Analyzing {pdf_path} with {len(pdf.pages)} pages...")
            
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                
                # Buffer to store manual domain extractions
                current_source = None
                
                for line in lines:
                    line = line.strip()
                    
                    # --- Strategy A: Regex for Capitalized Metaphors ---
                    # We strictly filter for lines that look like headers (mostly uppercase)
                    # to avoid capturing random sentence fragments.
                    if line.isupper(): 
                        matches = metaphor_pattern.findall(line)
                        for target, source in matches:
                            # Filter out false positives like "THIS IS A"
                            if len(target) > 2 and len(source) > 2: 
                                mappings.append({
                                    "Target": target,
                                    "Source": source,
                                    "Type": "Capitalized Header",
                                    "Page": page_num + 1
                                })

                    # --- Strategy B: Explicit Domain Listing ---
                    # The PDF uses "Source Domain: x" and "Target Domain: y"
                    if line.startswith("Source Domain:"):
                        current_source = line.replace("Source Domain:", "").strip()
                    
                    elif line.startswith("Target Domain:") and current_source:
                        current_target = line.replace("Target Domain:", "").strip()
                        mappings.append({
                            "Target": current_target,
                            "Source": current_source,
                            "Type": "Explicit Definition",
                            "Page": page_num + 1
                        })
                        current_source = None # Reset

    except Exception as e:
        print(f"Error processing PDF: {e}")
        return

    return mappings



    # Note on PDF Extraction: In the MetaNet papers, mappings are often discussed in the body text or shown in figures (like Figure 1 in W15-1405). Automated extraction works best on the capitalized conventions (e.g., "LOVE IS A JOURNEY"). 
    For the most accurate data, parsing the OWL/RDF data (as shown in the previous turn) is preferred over PDF scraping because the PDF representation is unstructured.


https://docs.google.com/spreadsheets/d/1DIy7qy0Elw3JL2SuDhoQJNvw9WOoraMgh2hNWqcufuU/edit?usp=sharing
https://docs.google.com/document/d/1wDsXksEQ43Vit8vmBa3tqHRSNODoJmRELlYB6MXWxZg/edit?usp=sharing
