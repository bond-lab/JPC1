# Describe and document your code


I added some code to find supertypes, this is useful for this task and lcmap (and probably more).

* `find_topic.py` the code --- there is some set up, then the function you need is `get_topic`.  It reads three files, and loads a wordnet.
  * `verbs.tsv` gives the verb top hierarchy
  * `nouns.tsv` gives the noun top hierarchy
  * `topics.toml` give a longer name and definitions for the topics
* `run_topic.sh` sets up a virtual environment and loads the requirements from `requirements.txt`

* note that  `find_topic.py` also has code to show the top hierarchy graphically, you can not call it if you don't need it.  It makes two diagrams for verbs and nouns
  * `Top nodes for v.png` and `Top nodes for n.png`

There is some documentation for topics: https://omwn.org/doc/topics.html
