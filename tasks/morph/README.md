# Describe and document your code
import os
import sys
import json
import nltk

sys.path.append(os.getcwd())

def find_file_recursive(base_path, target_snippet):
    for root, dirs, files in os.walk(base_path):
        for f in files:
            if target_snippet in f:
                return os.path.join(root, f)
    return None

def load_corelex_json():
    print("--- 1. Loading CoreLex (Synset -> Type) ---")
    target_file = "synset_to_type.json"
    path = find_file_recursive("data", target_file) or find_file_recursive(".", target_file)
    
    if not path:
        print(f" Error: Could not find {target_file}")
        return {}

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # DEBUG: Print first 5 keys to confirm format
    keys = list(data.keys())[:5]
    print(f" Loaded {len(data)} types.")
    print(f"   Sample Keys: {keys} (Expecting 'word.n.01')")
    return data

def load_chainnet_data():
    print("--- 2. Loading ChainNet Data ---")
    files = ["data/chainnet.json", "chainnet.json"]
    for f in files:
        if os.path.exists(f):
            with open(f, 'r', encoding='utf-8') as jf:
                data = json.load(jf)
                return data.get('content', data)
    return []

def main():
    print("---  Semantic Shift Analysis (Direct Method) ---")
    
    # 1. Load Data
    corelex = load_corelex_json()
    chainnet_data = load_chainnet_data()
    
    if not corelex or not chainnet_data:
        print(" Missing data files.")
        return

    # 2. Setup NLTK
    try:
        from nltk.corpus import wordnet as wn
        # Ensure data is present
        try:
            wn.synsets('dog')
        except LookupError:
            nltk.download('wordnet')
            nltk.download('omw-1.4')
    except ImportError:
        print(" NLTK not installed.")
        return

    print("\n" + "="*85)
    print(f"{'WORD':<15} {'SOURCE (Prototype)':<25} {'->':<4} {'TARGET (Metaphor)':<20}")
    print("="*85)

    count = 0
    match_count = 0
    
    for entry in chainnet_data:
        if 'senses' not in entry: continue
        
        sense_types = {}
        
        # --- PHASE A: MAP SENSES TO TYPES ---
        for sense in entry['senses']:
            wn30_key = sense.get('wordnet_sense_id') # e.g. "almanac%1:10:01::"
            if not wn30_key: continue
            
            try:
                # Convert Lemma Key -> Synset Name (e.g. "almanac.n.01")
                lemma = wn.lemma_from_key(wn30_key)
                synset_name = lemma.synset().name()
                
                # Direct Lookup in your JSON
                ctype = corelex.get(synset_name)
                
                if ctype:
                    sense_types[sense['sense_id']] = ctype
                    match_count += 1
            except Exception:
                continue

        # --- PHASE B: DETECT SHIFTS ---
        for sense in entry['senses']:
            if sense['label'] == 'metaphor':
                parent_id = sense.get('child_of')
                
                # Do we have types for both Source and Target?
                if parent_id in sense_types and sense['sense_id'] in sense_types:
                    src = sense_types[parent_id]
                    tgt = sense_types[sense['sense_id']]
                    
                    if src != tgt:
                        print(f"{entry['wordform']:<15} {src:<25} ->  {tgt:<20}")
                        count += 1
                        
        if count >= 30: break
            
    print("="*85)
    print(f"Analysis Complete.")
    print(f"Total Senses Mapped to CoreLex: {match_count}")
    print(f"Total Shifts Found: {count}")

    if count == 0 and match_count == 0:
        print("\n Zero matches. This means 'synset_to_type.json' uses WN 1.5 names")
        print("   and NLTK is providing WN 3.0 names, and they don't overlap.")
    elif count == 0:
        print("\n  Matches found, but no shifts detected. (Metaphors stay within same class?)")

if __name__ == "__main__":
    main()

>> ---  Semantic Shift Analysis (Direct Method) ---
--- 1. Loading CoreLex (Synset -> Type) ---
 Loaded 82115 types.
   Sample Keys: ['entity.n.01', 'physical_entity.n.01', 'abstraction.n.06', 'thing.n.12', 'object.n.01'] (Expecting 'word.n.01')
--- 2. Loading ChainNet Data ---

>=====================================================================================
WORD            SOURCE (Prototype)        ->   TARGET (Metaphor)
=====================================================================================
can             ARTIFACT                  ->  COMMUNICATION       
diary           ARTIFACT                  ->  COMMUNICATION
ghetto          GEOGRAPHICAL_LOCATION     ->  STATE
individual      HUMAN                     ->  ANIMAL
insult          COMMUNICATION             ->  ACT
patient         HUMAN                     ->  GROUPING
range           LOCATION                  ->  PSYCHOLOGICAL_FEATURE
congestion      PSYCHOLOGICAL_FEATURE     ->  STATE
leaf            NATURAL_BODY              ->  CHEMICAL
leaf            NATURAL_BODY              ->  PHYSICAL_OBJECT
mosaic          ARTIFACT                  ->  STATE
mosaic          ARTIFACT                  ->  PSYCHOLOGICAL_FEATURE
peacemaker      HUMAN                     ->  ARTIFACT
chestnut        NATURAL_BODY              ->  PSYCHOLOGICAL_FEATURE
neighborhood    SOCIAL_GROUP              ->  INDEFINITE_QUANTITY
person          HUMAN                     ->  GROUPING
situation       STATE                     ->  LOCATION
situation       STATE                     ->  ACT
superior        HUMAN                     ->  COMMUNICATION
compression     EVENT                     ->  ACT
pawn            ARTIFACT                  ->  HUMAN
phosphorus      CHEMICAL                  ->  NATURAL_BODY
process         ACT                       ->  PSYCHOLOGICAL_FEATURE
process         ACT                       ->  PROCESS
agonist         PSYCHOLOGICAL_FEATURE     ->  HUMAN
agonist         PSYCHOLOGICAL_FEATURE     ->  PART
agonist         PSYCHOLOGICAL_FEATURE     ->  AGENT
bag             ARTIFACT                  ->  HUMAN
bag             ARTIFACT                  ->  PART
bag             INDEFINITE_QUANTITY       ->  ACT
=====================================================================================
Analysis Complete.
Total Senses Mapped to CoreLex: 147
Total Shifts Found: 30
