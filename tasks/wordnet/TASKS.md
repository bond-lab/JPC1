# Wordnet integration
 * import chainnet to (English) wordnet
 * project to other languages
 * visualize
   * I have some rough code (chainnet-viz) that I will share
 * compare to corpus
 * look at sentiment
 * Look for errors
   * find exceptions to patterns
   * evaluate and fix
   * mainly direction, but can be type

## Next Tasks 

 * read: [ChainNet: Structured Metaphor and Metonymy in WordNet](https://aclanthology.org/2024.lrec-main.266/) (Maudslay et al., LREC-COLING 2024)
 * download the data https://github.com/rowanhm/ChainNet
 * read the annotation guidelines: https://maudslay.eu/ChainNet/documentation/ChainNet_Annotation_Guidelines.pdf
 * try to say something about the distribution, ...
 
THEN  
 * see if you can add the metaphor and metonymy links to the XML
OR
 * try and get wordnet editor working (I can help)
   * https://github.com/Hypercookie/wn-editor/

it should be something like:
```
import wn
from wn_editor.editor import SenseEditor, RelationType

# Download a WordNet if you haven't already
# wn.download('ewn:2020')

# Find senses you want to link
sense1 = wn.senses('hot')[0]  # Example: first sense of "hot"
sense2 = wn.senses('cold')[0]  # Example: first sense of "cold"

# Create editor and add antonym relation
editor = SenseEditor(sense1)
editor.set_relation_to_sense(sense2, RelationType.antonym)

# To delete a relation later:
# editor.delete_relation_to_sense(sense2, RelationType.antonym)from wn_editor.editor import SenseEditor, RelationType
import wn

# Get your source and target senses
source_sense = wn.sense('example-sense-id-1')
```

But currently it does not have metaphor!

Need to use a different branch:  https://github.com/goodmami/wn/tree/gh-260-wn-lmf-1.4

And adjust wordnet editor, ...   So I think I would need to help
