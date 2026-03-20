from nltk.corpus import wordnet as wn
from collections import deque


def sense_key_distance(sense_key1, sense_key2):
    """
    Computes the distance between two WordNet sense keys in the synset hierarchy.
    Searches both upwards (hypernyms) and downwards (hyponyms) using BFS.
    
    Returns:
        int: number of steps between synsets
        None: if no path exists
    """
    # convert sense keys to synsets
    synset1 = wn.lemma_from_key(sense_key1).synset()
    synset2 = wn.lemma_from_key(sense_key2).synset()

    # if they are the same synset, distance is 0
    if synset1 == synset2:
        return 0

    visited = {synset1}  # keep track of visited synsets
    queue = deque([(synset1, 0)])  # BFS queue: (synset, distance)

    while queue:
        current, distance = queue.popleft()

        # neighbors: hypernyms (up) and hyponyms (down)
        neighbors = current.hypernyms() + current.hyponyms()
        for neighbor in neighbors:
            if neighbor == synset2:
                return distance + 1  # found target, return distance
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, distance + 1))

    # no path found
    return None

metaphor_pairs = [
('clarity%1:07:01::', 'understand%2:31:00::'),
('clearness%1:07:01::', 'understand%2:31:00::'),
('illumination%1:10:00::', 'interpret%2:32:00::'),
('illumination%1:10:00::', 'understanding%1:09:03::'),
('illumination%1:10:00::', 'understand%2:31:02::'),
('light%1:09:00::', 'understanding%1:10:00::'),
('light%1:09:01::', 'understand%2:31:03::'),
('lighting%1:04:01::', 'understand%2:31:00::'),
('night%1:28:01::', 'ignorance%1:09:00::'),
('obscure%2:31:00::', 'confused%5:00:00:unoriented:00'),
('ardor%1:12:00::', 'love%1:12:01::'),
('ardor%1:12:02::', 'warmth%1:07:00::'),
('ardour%1:12:00::', 'love%1:12:01::'),
('ardour%1:12:02::', 'warmth%1:07:00::'),
('burn%2:37:00::', 'passion%1:12:00::'),
('fervency%1:12:00::', 'warmth%1:07:00::'),
('fervent%5:00:00:passionate:00', 'love%1:12:00::'),
('fervent%5:00:00:passionate:00', 'love%2:37:01::'),
('fervent%5:00:00:passionate:00', 'passion%1:16:00::'),
('fervent%5:00:00:passionate:00', 'love%2:37:01::'),
('fervid%5:00:00:passionate:00', 'love%1:12:00::'),
('fervid%5:00:00:passionate:00', 'love%2:37:01::'),
('fervid%5:00:00:passionate:00', 'passion%1:16:00::'),
('fervid%5:00:00:passionate:00', 'love%2:37:01::'),
('fervidness%1:12:00::', 'warmth%1:07:00::'),
('fervor%1:12:00::', 'warmth%1:07:00::'),
('fervour%1:12:00::', 'warmth%1:07:00::'),
('fiery%5:00:00:hot:02', 'passion%1:12:00::'),
('fiery%5:00:00:passionate:00', 'love%1:12:00::'),
('fiery%5:00:00:passionate:00', 'love%2:37:01::'),
('fiery%5:00:00:passionate:00', 'passion%1:16:00::'),
('fiery%5:00:00:passionate:00', 'love%2:37:01::'),
('fire%1:12:00::', 'warmth%1:07:00::'),
('flaming%5:00:00:hot:02', 'passion%1:12:00::'),
('burn%2:37:00::', 'anger%1:12:00::'),
('burn%2:37:00::', 'anger%1:12:00::'),
('time%1:28:05::', 'resource%1:21:00::'),
('life%1:09:00::', 'course%1:14:00::'),
('life%1:26:02::', 'course%1:14:00::'),
('living%1:09:00::', 'course%1:14:00::'),
('cold%3:00:02::', 'unfriendly%3:00:02::'),
('frigid%5:00:00:cold:02', 'unfriendliness%1:12:00::'),
('warm%3:00:02::', 'friendly%1:14:00::'),
('warm_up%2:30:01::', 'friendly%1:14:00::'),
('hot%5:00:00:sexy:00', 'sex%1:14:00::'),
('hotness%1:26:00::', 'sex%1:14:00::'),
('red-hot%5:00:00:sexy:00', 'sex%2:31:00::'),
('spicy%5:00:00:sexy:00', 'sex%1:14:00::'),
('move%2:37:00::', 'emotional%3:00:02::'),
('death%1:19:00::', 'end%2:42:01::'),
('death%1:28:00::', 'end%1:28:00::'),
('death%1:28:01::', 'end%1:28:00::'),
('death%1:26:01::', 'end%1:09:02::'),
('death%1:26:01::', 'end%2:30:01::'),
('death%1:28:01::', 'last%1:24:00::'),
('demise%1:28:00::', 'end%1:28:00::'),
('destruction%1:04:00::', 'termination%1:10:00::'),
('destruction%1:26:00::', 'end%1:09:02::'),
('destruction%1:26:00::', 'end%2:30:01::'),
('die%2:30:01::', 'end%2:30:01::'),
('die%2:30:04::', 'stop%1:10:01::'),
('die%2:33:00::', 'end%1:09:02::'),
('dying%1:28:00::', 'end%1:28:00::'),
('expiry%1:28:00::', 'end%1:09:02::'),
('last%1:28:01::', 'death%1:28:01::'),
('last%5:00:00:dying:00', 'death%1:28:01::')
    ]


# verification that all data is correctly entered
""""
for key1, key2 in metaphor_pairs:
    synset1 = wn.synset_from_sense_key(key1)
    synset2 = wn.synset_from_sense_key(key2)

    print("PAIR:")
    print(key1, "->", synset1.definition())
    print(key2, "->", synset2.definition())
    print()"""


for metaphor, source in metaphor_pairs:
    dist = sense_key_distance(metaphor, source)

    # finds POS
    pos_m = wn.lemma_from_key(metaphor).synset().pos()
    pos_s = wn.lemma_from_key(source).synset().pos()

    print(f"{metaphor} ({pos_m}) & {source} ({pos_s}) / distance: {dist}")