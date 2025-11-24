import wn
import json
import os
from collections import defaultdict as dd
from pathlib import Path

data_dir = '.' #Chainnet directory
outdir = 'build'
os.makedirs(outdir, exist_ok=True)

log = open('related.log', 'w')

### store local copy of wordnets
os.makedirs('wn_data', exist_ok=True)
wn.config.data_directory = 'wn_data'
   


def read_data(data_dir, wn):
    """
    store all the tropes as a set
    (trope, word, source_sense_id, target_sense_id)
    """
    ### make mapping
    skey = dict()
    for s in ewn.senses(pos='n'):
        #print (s.id, s.metadata()['identifier'])
        skey[s.metadata()['identifier']] = s.id

    tropes =set()    
    # Read in metaphors
    with open(f"{data_dir}/chainnet_metaphor.json", "r") as fp:
        metaphor = json.load(fp)

    print('Read Metaphors')

    meta = dd(lambda: dd(list))

    for e in metaphor['content']:
        w = e['wordform']
        fr_s = e['from_sense']
        to_s = e['to_sense']
        tropes.add(('metaphor', w, skey[fr_s], skey[to_s]))

    # Read in metonymy
    with open(f"{data_dir}/chainnet_metonymy.json", "r") as fp:
        metonymy = json.load(fp)

    print('Read Metonymy')

    for e in metonymy['content']:
        w = e['wordform']
        fr_s = e['from_sense']
        to_s = e['to_sense']
        tropes.add(('metonym', w, skey[fr_s], skey[to_s]))
    return tropes   


if __name__ == "__main__":
##
## Calculate derivational links between other senses
##
    print('Downloading OMW 1.4')
    wn.download('omw:1.4')
    ewn=wn.Wordnet(lexicon='omw-en:1.4')
    
    tropes = read_data(data_dir, ewn)


    def sid2ili (key):
        """ give an ili from a sense id """
        return ewn.sense(id=key).synset().ili.id
 
    ### list them 
    for  (trope, word, src_id, tgt_id) in tropes:
        print(trope, word, src_id, tgt_id)
    
    drvdir = Path(outdir) / 'deriv-links.tsv'
    drv = open(drvdir, 'w')

    print("rel", "src", "tgt", "wn", "link",
          "src-lem", "tgt=lem",
          sep = '\t', file=drv)

    print('Finding affixes and suffixes')
    for (trope, word, src_id, tgt_id) in tropes:
        for wnet in  wn.lexicons():
            if wnet.version !='1.4':
                continue
            wnlabel = f'{wnet.id}:1.4'

            twn = wn.Wordnet(lexicon=wnlabel)    
            labels = dd(list)
            i1 = sid2ili(src_id)
            i2 = sid2ili(tgt_id)
            if twn.synsets(ili=i1):
                ll1 = twn.synsets(ili=i1)[0].lemmas()
            else:
                ll1 = []
            if twn.synsets(ili=i2):
                ll2 = twn.synsets(ili=i2)[0].lemmas()
            else:
                ll2 = []
            for l1 in ll1:
                for l2 in ll2:
                    label = ''
                    if l1==l2: ### ignore identical ones
                            continue
                    if l1.startswith(l2):
                        label = wnet.id + '+' +  l1[len(l2):]
                        labels[label].append((i1, l1, i2, l2))
                    elif  l2.startswith(l1):
                        label = wnet.id + '-' + l2[len(l1):]
                        labels[label].append((i1, l1, i2, l2))

                    if label:
                        print(trope, i1, i2, wnet.id,
                              label, l1, l2,
                              sep = '\t', file=drv)


    


        
