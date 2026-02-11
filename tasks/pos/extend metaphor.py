import nltk
from nltk.corpus import wordnet as wn

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


def highlight(text, match):
    """Returns the text with matches highlighted as <<match>>."""
    return text.replace(match, f"<<{match}>>")


def extend_metaphor(base_word, metaphor_word):
    """
    Returns matches between the lexical forms of a base word and the metaphor word in the definitions
    and examples of synsets. Also prints the word forms.

    output:
    matches = [ (word, pos, 'definition/example match', highlight(definition, m_word)  ), (...), ... ]
    """

    related_words = word_related_forms(base_word)
    metaphoric_words = word_related_forms(metaphor_word)

    print(
    f"\nThe lexical forms of the base word '{base_word}': {', '.join(sorted(related_words))}\n\n"
    f"The forms of the metaphor '{metaphor_word}': {', '.join(sorted(metaphoric_words))}\n"
    )

    matches = []

    for word in related_words:
        for synset in wn.synsets(word):
            pos = synset.pos()  # n, v, a, r
            definition = synset.definition()
            examples = synset.examples()

            for m_word in metaphoric_words:
                # Searching in definitions
                if m_word in definition:
                    matches.append(
                        (word, pos, "definition match",
                         highlight(definition, m_word))
                    )

                # Searching in examples
                for ex in examples:
                    if m_word in ex:
                        matches.append(
                            (word, pos, "example match",
                             highlight(ex, m_word))
                        )

    return matches


def main():
    # List of combinations: (base_word, metaphor_word)
    word_pairs = [
        ("illuminate", "uncover"),
        ("light", "understand"),
        ("dark", "ignorance"),
        ("dark", "confusion")
    ]

    for base_word, metaphor_word in word_pairs:
        print(f"\n⚫ Analysis: {base_word} & {metaphor_word}")
        extensions = extend_metaphor(base_word, metaphor_word)

        if extensions:
            for base_derivation, pos, match_type, sentence in extensions:
                print(f"{base_derivation} ({pos}) / {match_type}: {sentence}")
        else:
            print("No matches were found.")


if __name__ == "__main__":
    main()


