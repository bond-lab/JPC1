import wn
import json
import os
import sys
from collections import Counter

sys.path.append(os.getcwd())

def setup_resources():
    print("Preparing components")

    candidate_files = [
        "omw-en_1.4_cn.xml",
        "data/omw-en_1.4_cn.xml",
        "omw-en_1.4_cn.xml.gz"
    ]

    custom_wn_file = None
    for f in candidate_files:
        if os.path.exists(f):
            custom_wn_file = f
            print(f"Found lexicon file: {f}")
            break

    lexicon_id = 'omw-en:1.4.cn'

    try:
        ewn = wn.Wordnet(lexicon_id)
        print(f"Lexicon '{lexicon_id}' loaded")
    except wn.Error:
        if custom_wn_file:
            print("Installing lexicon")
            wn.add(custom_wn_file)
            ewn = wn.Wordnet(lexicon_id)
            print("Lexicon installed")
        else:
            print("Lexicon missing and file not found")
            sys.exit(1)

    corelex_file = "synset_to_type.json"
    found_path = None

    for root, _, files in os.walk("."):
        if corelex_file in files:
            found_path = os.path.join(root, corelex_file)
            break

    if not found_path:
        print("Could not find 'synset_to_type.json'")
        sys.exit(1)

    with open(found_path, 'r', encoding='utf-8') as f:
        corelex = json.load(f)

    print(f"Loaded CoreLex map with {len(corelex)} entries")
    return ewn, corelex


def get_corelex_type(word, sense_id, noun_senses, corelex_map):
    try:
        index = next((i for i, s in enumerate(noun_senses) if s.id == sense_id), -1)
        if index == -1:
            return None

        key_v1 = f"{word}.n.{index+1:02d}"
        key_v2 = f"{word}.n.{index+1}"

        return corelex_map.get(key_v1) or corelex_map.get(key_v2)

    except:
        return None


def get_noun_senses(ewn, lemma):
    return [s for s in ewn.senses(lemma) if s.synset().pos == 'n']


def resolve_target_type(ewn, target_sense, corelex):
    tgt_lemma = target_sense.word().lemma()
    tgt_senses = get_noun_senses(ewn, tgt_lemma)

    return get_corelex_type(
        tgt_lemma,
        target_sense.id,
        tgt_senses,
        corelex
    )


def main():
    ewn, corelex = setup_resources()

    target_words = [
        'chestnut', 'pig', 'star', 'mouth', 'head', 'face', 'arm',
        'leg', 'foot', 'dog', 'rat', 'snake', 'lamb', 'hawk'
    ]
    print(40 * "-")
    print("WORD\tSOURCE TYPE\tTARGET TYPE")
    print(40 * "-")

    detected_shifts = []

    for word in target_words:
        noun_senses = get_noun_senses(ewn, word)

        for sense in noun_senses:
            relations = sense.relations()
            if 'metaphor' not in relations:
                continue

            src_type = get_corelex_type(word, sense.id, noun_senses, corelex)

            for target_sense in relations['metaphor']:
                tgt_type = resolve_target_type(ewn, target_sense, corelex)

                if src_type and tgt_type and src_type != tgt_type:
                    print(f"{word}\t{src_type}\t{tgt_type}")

                    try:
                        src_def = sense.synset().definition()
                    except:
                        src_def = "Definition unavailable"

                    try:
                        tgt_def = target_sense.synset().definition()
                    except:
                        tgt_def = "Definition unavailable"

                    print(f"  Source: {src_def}")
                    print(f"  Target: {tgt_def}\n")

                    detected_shifts.append((src_type, tgt_type))

    print("Analysis")

    if not detected_shifts:
        print("No semantic shifts detected")
    else:
        print(f"Total shifts: {len(detected_shifts)}")

        counts = Counter(detected_shifts)
        for (src, tgt), count in counts.most_common(5):
            print(f"{src} -> {tgt}: {count}")


if __name__ == "__main__":
    main()