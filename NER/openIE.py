from openie import StanfordOpenIE
import json
# https://stanfordnlp.github.io/CoreNLP/openie.html#api
# Default value of openie.affinity_probability_cap was 1/3.
properties = {
    'openie.affinity_probability_cap': 2 / 3,
}

# input = "corpus/CNN.txt"
input = "coref/coref_CNN.txt"

output = "results/" + input.split("/")[1].split(".")[0] + ".txt"
graph_image = 'graph/' + input.split("/")[1].split(".")[0] + ".png"

with StanfordOpenIE(properties=properties) as client:

    with open(input, encoding='utf8') as r:
        corpus = r.read().replace('\n', ' ').replace('\r', '')

    triples_corpus = client.annotate(corpus[0:5000])
    print('Found %s triples in the corpus.' % len(triples_corpus))
    with open(output, "w") as o:
        for triple in triples_corpus:
            o.write(json.dumps(triple)+"\n")
    client.generate_graphviz_graph(corpus[0:5000], graph_image)
    print('Graph generated: %s.' % graph_image)
