
# Load your usual SpaCy model (one of SpaCy English models)
import neuralcoref
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
# nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
print(stop_words)

# input = "corpus/CNN.txt"
# output = "coref/coref_" + input.split("/")[1].split(".")[0] + ".txt"
# nlp = spacy.load('en_core_web_sm')

# # Add neural coref to SpaCy's pipe
# neuralcoref.add_to_pipe(nlp)

# # # You're done. You can now use NeuralCoref as you usually manipulate a SpaCy document annotations.
# with open(input, encoding='utf8') as r:
#     corpus = r.read().replace('\n', ' ').replace('\r', '')
#     doc = nlp(corpus[:5000])
#     if doc._.has_coref:
#       print(doc._.coref_clusters)
#       with open(output, "w") as f2:
#         f2.write(doc._.coref_resolved)
