import wn
import nltk
from nltk.corpus import wordnet as nltk_wn
import json
import os
import sys
import re

# Make sure local files are visible
sys.path.append(os.getcwd())


def setup_resources():
    print("--- Setting up resources ---")

    # Try to locate the custom WordNet file
    candidate_files = [
        "omw-en_1.4_cn.xml",
        "data/omw-en_1.4_cn.xml",
        "omw-en:1.4_cn.xml.gz"
    ]

    custom_wn_file = None
    for fname in candidate_files:
        if os.path.exists(fname):
            custom_wn_file = fname
            print(f"Found WordNet file: {fname}")
            break

    if custom_wn_file is None:
        print("Error: could not find 'omw-en_1.4_cn.xml'")
        print("Make sure the file is in the same directory as this script.")
        sys.exit(1)

    lexicon_id = "omw-en:1.4.cn"

    # Load or install the lexicon if needed
    try:
        wn.Wordnet(lexicon_id)
        print(f"Lexicon '{lexicon_id}' already available.")
    except wn.Error:
        print(f"Installing lexicon from '{custom_wn_file}' (may take a moment)...")
        wn.add(custom_wn_file)
        print("Lexicon installed.")

    # Load CoreLex mapping
    corelex_file = "synset_to_type.json"
    corelex_path = None

    for root, _, files in os.walk("."):
        if corelex_file in files:
            corelex_path = os.path.join(root, corelex_file)
            break

    if corelex_path is None:
        print("Error: synset_to_type.json not found.")
        sys.exit(1)

    with open(corelex_path, "r", encoding="utf-8") as f:
        corelex = json.load(f)

    print(f"Loaded CoreLex with {len(corelex)} entries.")

    # Load ChainNet words (used only as a word list)
    words = []
    for path in ("chainnet.json", "data/chainnet.json"):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                content = data.get("content", data)
                words = [item["wordform"] for item in content if "wordform" in item]
            break

    if not words:
        print("Warning: chainnet.json not found, using fallback list.")
        words = ["chestnut", "head", "pig", "mouth", "star", "hawk", "lamb"]

    return wn.Wordnet(lexicon_id), corelex, words


def get_corelex_type(wn_sense, corelex_map):
    """
    Maps a custom WordNet sense to a CoreLex type.
    """
    try:
        # Example ID: omw-en-chestnut-07772274-n
        m = re.search(r"-(\d{8})-", wn_sense.id)
        if not m:
            return "Unknown_ID_Format"

        offset = int(m.group(1))
        pos = wn_sense.id[-1]

        if pos != "n":
            return "Not_Noun"

        synset = nltk_wn.synset_from_pos_and_offset("n", offset)
        synset_name = synset.name()

        return corelex_map.get(synset_name, "No_CoreLex_Entry")

    except Exception:
        return "Map_Error"


def main():
    ewn, corelex, target_words = setup_resources()

    print("\n" + "=" * 85)
    print(f"{'WORD':<15} {'SOURCE (Prototype)':<25} {'->':<4} {'TARGET (Metaphor)':<20}")
    print("=" * 85)

    count = 0

    for word in sorted(set(target_words)):
        senses = ewn.senses(word)

        for sense in senses:
            rels = sense.relations()

            targets = []
            if "metaphor" in rels:
                targets.extend(rels["metaphor"])
            if "has_metaphor" in rels:
                targets.extend(rels["has_metaphor"])

            if not targets:
                continue

            source_type = get_corelex_type(sense, corelex)

            for target_sense in targets:
                target_type = get_corelex_type(target_sense, corelex)

                ok = (
                    source_type not in ("Not_Noun", "Map_Error", "No_CoreLex_Entry")
                    and target_type not in ("Not_Noun", "Map_Error", "No_CoreLex_Entry")
                )

                if ok and source_type != target_type:
                    print(f"{word:<15} {source_type:<25} ->  {target_type:<20}")
                    count += 1

        if count >= 50:
            break

    print("=" * 85)
    print(f"Analysis complete. Found {count} semantic shifts.")


if __name__ == "__main__":
    main()
