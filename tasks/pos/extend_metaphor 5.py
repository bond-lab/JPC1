import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.wsd import lesk
from nltk.corpus import wordnet as wn

# Uncomment these lines to download required NLTK data on first run
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('omw-1.4')


def word_related_forms(word):
    """
    Returns a combination of synonyms and derivationally related forms from WordNet.
    """
    forms = set()
    for synset in wn.synsets(word):
        for lemma in synset.lemmas():
            forms.add(lemma.name())
            for der in lemma.derivationally_related_forms():
                forms.add(der.name())
    return forms


def highlight(text, word_list):
    """
    Highlights words from a given list in the input text.

    For each word in the text:
    - If the word exactly matches an item in word_list, it is highlighted.
    - If no exact match, it searches for the longest possible substring from word_list
      inside the word (e.g., 'understand' in 'understanding').
    - Highlights are done using << >>.
    
    The function is case-insensitive but preserves the original text casing.
    
    Parameters:
    text (str): The input text to process.
    word_list (list of str): List of words to highlight.
    
    Returns:
    str: The text with highlighted words.
    """
    import re

    # sort the word list by length descending to find the longest match first
    word_list = sorted(word_list, key=len, reverse=True)

    def replace_word(word):
        for w in word_list:
            if w.lower() in word.lower():
                # replace only the first occurrence and preserve original casing
                start = word.lower().find(w.lower())
                end = start + len(w)
                return word[:start] + f'<<{word[start:end]}>>' + word[end:]
        return word

    # tokenize text into words and punctuation
    tokens = re.findall(r'\w+|\W+', text)
    highlighted = [replace_word(token) if token.isalnum() else token for token in tokens]

    return ''.join(highlighted)


def sense_key_from_context(text, word):
    """
    Returns the WordNet sense key for a given word (lemma name) in the context of a sentence.
    """
    # get most probable synset (meaning) based on context
    synset = lesk(word_tokenize(text), word)
    if not synset:
        return None

    matched_lemma = None

    for lemma_ in synset.lemmas():
        if lemma_.name() == word:
            matched_lemma = lemma_
            break

    if matched_lemma:
        return matched_lemma.key()
    else:
        return None


def sense_key_from_marked_words(text, pattern=r'<<(.+?)>>'):
    """
    Returns a list of WordNet sense keys for each marked word in the text.

    :param text: Input sentence or text
    :param pattern: Regular expression for marked words, default '<<word>>'
    :return: List of sense keys (None if a sense is not found)
    """
    marked_words = re.findall(pattern, text)
    sense_keys = [sense_key_from_context(text, word) for word in marked_words]
    return sense_keys


def extend_metaphor(metaphor_word, source_word):
    """
    Returns matches between the lexical forms of a metaphor word and the source word
    in the definitions and examples of synsets.
    
    output:
    matches = [
        (word, pos, 'definition/example match', highlighted_text, sense_key),
        ...
    ]
    """

    metaphoric_words = word_related_forms(metaphor_word)
    source_words = word_related_forms(source_word)

    print(
        f"\nThe lexical forms of the metaphor word '{metaphor_word}': "
        f"{', '.join(sorted(metaphoric_words))}\n\n"
        f"The lexical forms of the source word '{source_word}': "
        f"{', '.join(sorted(source_words))}\n"
    )

    matches = set()

    for metaphoric_w in metaphoric_words:
        metaphor_synsets = wn.synsets(metaphoric_w) # dává všechny významy daného slova
        """
            Each synset:
            - has a unique ID
            - belongs to a part of speech (POS)
            - has one definition
            - may have zero or more examples
            - contains multiple synonyms (lemma names) = different words that share the same meaning, so they belong to the same synset / same ID.
            """

        for syn in metaphor_synsets:
            meta_pos = syn.pos()
            meta_definition = syn.definition()
            meta_examples = syn.examples()
            meta_lemmas = syn.lemmas()

            # zde získáme správné sense ID
            for meta_lem in meta_lemmas: # lemma = základní slovníková forma slova 
                if meta_lem.name() == metaphoric_w:
                    metaphor_sense_key = meta_lem.key() # sense_key = jedinečný identifikátor konkrétního významu daného lemma

                    for source_w in source_words:
                        if source_w in meta_definition:

                            highlighted_sentence = highlight(meta_definition, source_words)
                            source_sense_key = tuple(sense_key_from_marked_words(highlighted_sentence))

                            # here we want to connet metaphor_sense_key (metaphor lemma + metaphor synset) with 
                            # with estimated source_sense_key (source lemma + estimated source synset)
                            matches.add(
                                (metaphoric_w, meta_pos, "definition match", metaphor_sense_key,  highlighted_sentence, source_sense_key)
                            )

                        for ex in meta_examples:
                            if source_w in ex:

                            # here we want to connet metaphor_sense_key (metaphor lemma + metaphor synset) with 
                            # with estimated source_sense_key (source lemma + estimated source synset)
                                highlighted_sentence = highlight(ex, source_words)
                                source_sense_key = tuple(sense_key_from_marked_words(highlighted_sentence))

                                matches.add(
                                    (metaphoric_w, meta_pos, "example match", metaphor_sense_key, highlighted_sentence, source_sense_key)
                                )

    return sorted(matches)

def main():
    # List of combinations: (metaphor_word, source_word)
    word_pairs = [
        ("illuminate", "uncover"), # X
        ("light", "understand"),
        ("dark", "ignorance"),
        ("dark", "confusion"),
        ("fire", "passion"),
        ("fire", "anger"),
        ("time", "money"), # X
        ("time", "resource"),
        #("Life", "journey"),# X
        ("Life", "path"),
        ("Cold", "Unfriendly"),
        ("Warm", "Friendly"),
        ("hot", "sexy"),
        ("motion", "emotion"),
        #("Shelter", "protection"),# X
        #("Purpose", "Destination"), # X
        ("death", "end")
    ]

    for metaphor_word, source_word in word_pairs:
        print(f"\n⚫ Analysis: {metaphor_word} & {source_word}")
        extensions = extend_metaphor(metaphor_word, source_word)

        if extensions:
            for metaphoric_w, pos, match_type, metaphor_sense_key, sentence, source_sense_key in extensions:
                source_sense_key_str = ', '.join(str(s) for s in source_sense_key if s)
                print(f"{metaphoric_w} ({pos}) / {match_type} ({metaphor_sense_key}): {sentence} ({source_sense_key_str})")
        else:
            print("No matches were found")
        
if __name__ == "__main__":
    main()