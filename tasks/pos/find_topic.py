from collections import defaultdict as dd
from pathlib import Path
import toml
from delphin import tdl, predicate
import wn
import sys, re

import networkx as nx
import matplotlib.pyplot as plt


### erg
tml = toml.load('topics.toml')

#wn.get('oewn:2022')
en = wn.Wordnet('oewn:2024')

topic = dd(dict) # topic_by_depth['00742582'] = (2, com, communication)

def load_verbs(pos, vpath, topic):
    fh = open(vpath)
    for l in fh:
        row = l.strip().split('\t')
        topic[f"oewn-{row[1].strip()}-{pos}"] = (int(row[2].strip()), row[3].strip(), row[0].strip())
    return topic
    
topic = load_verbs('v', 'verbs.tsv', topic)
topic = load_verbs('n', 'nouns.tsv', topic)

def print_top (pos, topic, root):
    """
    show the top hierarchy
    """
    G = nx.DiGraph()
    edges = set()
    labels = dict()
    named = []
    nodes=set()
    special_nodes = dict()
    for ssid in topic:
        if not ssid.endswith(f'-{pos}'):
            continue
        named.append(ssid)
        labels[ssid] = topic[ssid][1].upper()+ "\n " + topic[ssid][2]  # TLA
        special_nodes[ssid] = 'lightgreen'
        if topic[ssid][0] == 0 and pos == 'v': # Add top for verbs
            edges.add((root, ssid))
            
    #print(labels)
    if pos == 'v':
        named.append(root)
        labels[root] = root
        special_nodes[ssid] = 'lightgreen'
    
    for ssid in named:
        if ssid == root:
            continue
        s = en.synset(ssid)
        for h in s.hypernyms():
            edges.add((h.id, s.id))
            nodes.add(h.id)
        for p in s.hypernym_paths():
            for ss in p:
                nodes.add(ss.id)
                for h in ss.hypernyms():
                    edges.add((h.id, ss.id))
                    nodes.add(h.id)
                    
    for synset in nodes:
        if synset not in labels:
            labels[synset] = en.synset(synset).lemmas()[0]

    # print ("\n".join(str(s) for s in sorted(edges)))
    G.add_edges_from(edges)

    node_colors = [special_nodes.get(node, 'lightblue') for node in G.nodes()]
    #print (G.nodes())

    # Draw the graph
    plt.figure(figsize=(20, 10))
    position= nx.nx_agraph.graphviz_layout(G, prog='dot', root=root)
    nx.draw(G, position, labels=labels, node_color=node_colors, 
            node_size=1000, arrows=True, arrowsize=20, 
            font_size=12, font_weight='bold')

    plt.title(f"Top Nodes for {pos}")
    filename = f'Top nodes for {pos}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()  # Close to free memory
    print(f"Graph saved as: '{filename}'")
                    

#quit()    

def get_topic(synset, tml=tml, topic=topic):
    """
    return the TLA of the topic of a synset
    for verb or noun, use hypernyms 
    for the rest use lexicographer files
    """
    pos = synset.pos
    top_abv = 'UNKNOWN'
    candidates = []
    if pos in 'vn':
        ancestors = synset.hypernym_paths()
        if ancestors == []: # no hypernym
            top_abv =  topic[synset.id][1]
        else:
            for a in ancestors:
                for ss in a:
                #print (ancestors[0])
                    if ss.id in topic:
                        candidates.append(ss.id)
            candidates.sort(key = lambda x: topic[x][0])
            top_abv =  topic[candidates[-1]][1]
    else:
        top = synset.lexfile()
        top_abv = tml[top.split('.')[0]][top.split('.')[1]]['abv']
    return top_abv

print(f"The topic for sense one of dog is: {get_topic(en.synsets('dog')[0])}")
print(f"The topic for sense one of illuminate is: {get_topic(en.synsets('illuminate')[0])}")

### print graphs of the supertypes for nouns and verbs
print_top('n', topic, 'oewn-0174000-n')
print_top('v', topic, 'DoBe')
#print(tbd)
