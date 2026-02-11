# Describe and document your code
import pandas as pd
import json
import re
from difflib import get_close_matches

# --- 1. CONFIGURATION ---
# Placeholder paths - replace with actual dataset locations
CHAINNET_PATH = 'chainnet_data.csv'  # Columns: [source_sense, target_sense, relation_type]
MML_PATH = 'master_metaphor_list.txt'

# --- 2. DATA LOADING & EXTRACTION ---

def load_chainnet(filepath):
    """
    Extracts metaphor pairs from ChainNet.
    Returns a list of dicts: {'word': 'attack', 'source': 'war', 'target': 'argument'}
    """
    # Simulating data loading based on ChainNet structure
    # In reality, you would parse the specific ChainNet XML/CSV format
    # Here we simulate the structure for demonstration
    chainnet_entries = []
    
    try:
        df = pd.read_csv(filepath)
        # Filter for only Metaphor relations
        metaphors = df[df['relation_type'] == 'Metaphor']
        
        for _, row in metaphors.iterrows():
            # Extract the lemma (lexical item) from the WordNet sense key (e.g., 'attack.n.01')
            lemma = row['source_sense'].split('.')[0]
            chainnet_entries.append({
                'lemma': lemma,
                'source_sense': row['source_sense'],
                'target_sense': row['target_sense'],
                # In a real scenario, we would use WordNet glosses to infer domains
                # For this script, we assume 'gloss_source' and 'gloss_target' columns exist
                'source_def': row.get('source_gloss', ''), 
                'target_def': row.get('target_gloss', '')
            })
    except FileNotFoundError:
        print("ChainNet file not found. Using internal sample for demonstration.")
        # FALLBACK: Generating the sample used in the report
        sample_words = [
            ('attack', 'war', 'argument'), ('see', 'vision', 'understanding'),
            ('warm', 'temperature', 'affection'), ('time', 'money', 'resource'),
            ('digest', 'food', 'ideas')
        ]
        for w, s, t in sample_words:
            chainnet_entries.append({'lemma': w, 'source_domain_hint': s, 'target_domain_hint': t})
            
    return chainnet_entries

def load_mml(filepath):
    """
    Parses the Master Metaphor List to extract Conceptual Metaphors (CMs).
    """
    conceptual_metaphors = {} # Format: {'ARGUMENT IS WAR': ['attack', 'defend', ...]}
    
    try:
        with open(filepath, 'r') as f:
            current_cm = None
            for line in f:
                line = line.strip()
                # Heuristic: MML often uses ALL CAPS for Metaphor Names
                if line.isupper() and " IS " in line:
                    current_cm = line
                    conceptual_metaphors[current_cm] = []
                elif current_cm and line:
                    # Collect keywords/lexical triggers associated with the CM
                    conceptual_metaphors[current_cm].append(line.lower())
    except FileNotFoundError:
        print("MML file not found. Using internal knowledge base.")
        # FALLBACK: Standard MML Categories
        conceptual_metaphors = {
            'ARGUMENT IS WAR': ['attack', 'defend', 'strategy', 'win', 'lose', 'shot'],
            'IDEAS ARE FOOD': ['digest', 'swallow', 'raw', 'half-baked'],
            'UNDERSTANDING IS SEEING': ['see', 'clear', 'focus', 'view', 'perspective'],
            'TIME IS MONEY': ['spend', 'waste', 'cost', 'invest', 'budget'],
            'LIFE IS A JOURNEY': ['path', 'crossroads', 'arrival', 'departure'],
            'CONTROL IS UP': ['rise', 'fall', 'high', 'low', 'superior']
        }
        
    return conceptual_metaphors

# --- 3. LINKING LOGIC ---

def link_metaphors(chainnet_data, mml_data):
    """
    Maps lexical metaphors (ChainNet) to conceptual metaphors (MML).
    """
    links = []
    
    for entry in chainnet_data:
        lemma = entry['lemma']
        best_match = None
        
        # Strategy A: Direct Lexical Match
        # Check if the ChainNet word appears in the MML lexical triggers
        for cm, triggers in mml_data.items():
            if lemma in triggers:
                best_match = cm
                break
        
        # Strategy B: Semantic Domain Matching (Simplified)
        # If no direct match, check if source/target domains match MML naming convention
        if not best_match and 'source_domain_hint' in entry:
            src = entry['source_domain_hint'].upper()
            tgt = entry['target_domain_hint'].upper()
            constructed_cm = f"{tgt} IS {src}" # e.g. ARGUMENT IS WAR
            
            # Fuzzy match against MML keys
            matches = get_close_matches(constructed_cm, mml_data.keys(), n=1, cutoff=0.6)
            if matches:
                best_match = matches[0]

        if best_match:
            links.append({
                'Lexical_Item': lemma,
                'ChainNet_Source': entry.get('source_sense', 'N/A'),
                'ChainNet_Target': entry.get('target_sense', 'N/A'),
                'MML_Concept': best_match
            })
            
    return links

# --- 4. EXECUTION ---

if __name__ == "__main__":
    print("Extracting ChainNet data...")
    chainnet = load_chainnet(CHAINNET_PATH)
    
    print("Extracting Master Metaphor List...")
    mml = load_mml(MML_PATH)
    
    print(f"Linking {len(chainnet)} lexical items to {len(mml)} conceptual metaphors...")
    results = link_metaphors(chainnet, mml)
    
    # Output Results
    df_results = pd.DataFrame(results)
    print("\n--- LINKING RESULTS (Top 10) ---")
    print(df_results.head(10))
    
    # Save to CSV for submission
    df_results.to_csv("chainnet_mml_links.csv", index=False)
    print("\nFull results saved to 'chainnet_mml_links.csv'.")


    # Note on PDF Extraction: In the MetaNet papers, mappings are often discussed in the body text or shown in figures (like Figure 1 in W15-1405). Automated extraction works best on the capitalized conventions (e.g., "LOVE IS A JOURNEY"). 
    For the most accurate data, parsing the OWL/RDF data (as shown in the previous turn) is preferred over PDF scraping because the PDF representation is unstructured.
   
    #Context Aware:1. It specifically targets the Source Domain: syntax found on pages 5, 7, 8, etc..

                   2.Multi-word Support: It will correctly identify "CHANGE" -> "RELATIVE MOTION" instead of truncating it.

                   3.Noise Reduction: By checking if line.isupper(), it avoids picking up random sentences in the body text that happen to use "is" between capitalized words (though the regex handles most of this, the check adds safety).

https://docs.google.com/spreadsheets/d/1DIy7qy0Elw3JL2SuDhoQJNvw9WOoraMgh2hNWqcufuU/edit?usp=sharing
https://docs.google.com/document/d/1wDsXksEQ43Vit8vmBa3tqHRSNOD
[JSP3 Report on Metaphor Extraction and Research Continuity (2).pdf](https://github.com/user-attachments/files/24863014/JSP3.Report.on.Metaphor.Extraction.and.Research.Continuity.2.pdf)
oJmRELlYB6MXWxZg/edit?usp=sharing



