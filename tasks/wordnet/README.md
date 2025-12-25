# Describe and document your code

Code is in `analyze-tropes.py`

The report is in `report_wordnet.tex`

You need to process with `luatex` or `xetex`.

## ToDo

Both the code and the report need more work ---

* make sure the diagrams are all there
* calculate specificity
* add discussion



### Wordnet with metaphor and metonymy

I made a script to add metaphor and metonym links to an English wordnet <https://github.com/fcbond/ChainNet>.

The resulting wordnets are here: `omw-en:1.4_cn.xml.gz`, `oewn:2024_cn.xml.gz`.  The former has all the relations from ChainNet, the latter is missing 66, but has various new changes from the Open English Wordnet.



You can load them with  `wn` version 0.14, which requires python 3.10 or above.

```
>>> import wn
>>> wn.add('omw-en:1.4_cn.xml.gz')
Read [##############################] (1213253/1213253) 
Added omw-en:1.4.cn (OMW English Wordnet based on WordNet 3.0 with tropes from ChainNet)

>>>
>>> ewn=wn.Wordnet(lexicon='omw-en:1.4.cn')
>>> 
>>> for s in ewn.senses('chestnut'):
...   print(s, s.relations())
... 
Sense('omw-en-chestnut-00373209-s') {'derivation': [Sense('omw-en-chestnut-04972350-n')]}
Sense('omw-en-chestnut-12262905-n') {'has_metonym': [Sense('omw-en-chestnut-12262553-n')]}
Sense('omw-en-chestnut-12262553-n') {'metonym': [Sense('omw-en-chestnut-12262905-n')], 'has_metonym': [Sense('omw-en-chestnut-07772274-n')]}
Sense('omw-en-chestnut-07772274-n') {'metaphor': [Sense('omw-en-chestnut-02468504-n')], 'metonym': [Sense('omw-en-chestnut-12262553-n'), Sense('omw-en-chestnut-04972350-n')]}
Sense('omw-en-chestnut-04972350-n') {'derivation': [Sense('omw-en-chestnut-00373209-s')], 'has_metonym': [Sense('omw-en-chestnut-07772274-n')], 'metonym': [Sense('omw-en-chestnut-02388735-n')]}
Sense('omw-en-chestnut-02468504-n') {'has_metaphor': [Sense('omw-en-chestnut-07772274-n')]}
Sense('omw-en-chestnut-02388735-n') {'has_metonym': [Sense('omw-en-chestnut-04972350-n')]}
>>> 
```
