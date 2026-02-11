The report claims that you have linked chainnet to corenet, and this gives som useful Lexical–Conceptual Mappings.  I was unable to get any output.

When I ran the code, I got this output:
```
uv run --with-requirements requirements.txt python analyze_shifts_final.py 
--- Setting up resources ---
Found WordNet file: omw-en_1.4_cn.xml
Lexicon 'omw-en:1.4.cn' already available.
Loaded CoreLex with 82115 entries.

=====================================================================================
WORD            SOURCE (Prototype)        ->   TARGET (Metaphor)   
=====================================================================================
=====================================================================================
Analysis complete. Found 0 semantic shifts.
```

I had to fiddle a bit to get things to work, next class we will look at setting up environments.

Note, that this maping was only the first step of the assignment, you then needed to do some anlaysis of the mappings.

Hint: you can do the mapping more easily, the number in the corelex file is the sense number, so chestnut.n.4 is the fourth noun sense.  If you list the senses in order, this is the one you will get, ...

```
for s in ewn.senses('chestnut'):
...     print(s, s.metadata(), s.synset().definition())
...     
Sense('omw-en-chestnut-00373209-s') {'identifier': 'chestnut%5:00:00:chromatic:00'} (of hair or feathers) of a golden brown to reddish brown color
Sense('omw-en-chestnut-12262905-n') {'identifier': 'chestnut%1:20:02::'} wood of any of various chestnut trees of the genus Castanea
Sense('omw-en-chestnut-12262553-n') {'identifier': 'chestnut%1:20:00::'} any of several attractive deciduous trees yellow-brown in autumn; yield a hard wood and edible nuts in a prickly bur
Sense('omw-en-chestnut-07772274-n') {'identifier': 'chestnut%1:13:00::'} edible nut of any of various chestnut trees of the genus Castanea
Sense('omw-en-chestnut-04972350-n') {'identifier': 'chestnut%1:07:00::'} the brown color of chestnuts
Sense('omw-en-chestnut-02468504-n') {'identifier': 'chestnut%1:05:01::'} a small horny callus on the inner surface of a horse's leg
Sense('omw-en-chestnut-02388735-n') {'identifier': 'chestnut%1:05:00::'} a dark golden-brown or reddish-brown horse
```

Finally, you have not committed the LaTeX source of the report.
