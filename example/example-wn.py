##
## give some examples if using wordnet
##

import wn
from wn.similarity import path

ewn=wn.Wordnet(lexicon='omw-en:1.4')
#pudding omw-en-pudding-07612632-n omw-en-pudding-07617188-n

sids = 'omw-en-storm-11462526-n omw-en-storm-13978344-n'.split()
#sids = ('omw-en-pudding-07612632-n',  'omw-en-pudding-07617188-n')
for sid in sids:
    s = ewn.sense(id=sid)
    print(s.synset().definition()) # definition
    print(s.synset().lexfile()) # topic/supersense
    print(s.synset().min_depth()) # depth
    print(s.synset().hypernym_paths()) # hypernyms
    print(s.get_related('derivation')) # derived senses

# distance    
ss1 =  ewn.sense(id=sids[0]).synset()
ss2 =  ewn.sense(id=sids[1]).synset()
print('distance:', path(ss1,ss2))
