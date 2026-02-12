import pandas as pd
import json
import os 

# --- 1. CONFIGURATION ---
# Define the input files and their corresponding labels
FILES_TO_LOAD = [
    {"path": r"C:\Users\Mahdal\Desktop\Bond\chainnet_metaphor.json", "type": "Metaphor"},
    {"path": r"C:\Users\Mahdal\Desktop\Bond\chainnet_metonymy.json", "type": "Metonymy"}
]

OUTPUT_FILE = "chainnet_combined_results.csv"

# --- 2. DATA LOADING & PROCESSING ---

def load_and_combine_chainnet(files_config):
    """
    Reads multiple ChainNet JSON files and combines them into one dataset.
    """
    combined_data = []
    
    for config in files_config:
        filepath = config["path"]
        data_type = config["type"]
        
        # Robust path checking (handles .json.json errors)
        if not os.path.exists(filepath):
            if os.path.exists(filepath + ".json"):
                filepath += ".json"
            else:
                print(f"Warning: File not found: {filepath}")
                continue
                
        print(f"Processing {data_type} from {os.path.basename(filepath)}...")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = json.load(f)
                
            # Extract the list of entries from the "content" key
            items = content.get('content', [])
            
            for item in items:
                # Create a clean entry row
                entry = {
                    'Word': item.get('wordform', 'N/A'),
                    'Type': data_type,
                    'Source_Sense': item.get('from_sense', 'N/A'),
                    'Target_Sense': item.get('to_sense', 'N/A')
                }
                combined_data.append(entry)
                
            print(f"   -> Loaded {len(items)} entries.")
            
        except Exception as e:
            print(f"   -> Error reading file: {e}")
            
    return combined_data

# --- 3. EXECUTION ---

if __name__ == "__main__":
    print("--- STARTING CHAINNET INTEGRATION ---")
    
    # 1. Load and Combine
    all_data = load_and_combine_chainnet(FILES_TO_LOAD)
    
    # 2. Output Results
    if all_data:
        df = pd.DataFrame(all_data)
        
        # Display large sample to console (50 items)
        print("\n--- COMBINED DATASET SAMPLE ---")
        print(df.head(50).to_string(index=False))
        
        # Save to CSV
        output_dir = os.path.dirname(FILES_TO_LOAD[0]["path"])
        output_path = os.path.join(output_dir, OUTPUT_FILE)
        
        df.to_csv(output_path, index=False)
        print(f"\nSUCCESS: Saved {len(df)} rows to '{output_path}'")
    else:
        print("\nNo data found. Please check your JSON file locations.")