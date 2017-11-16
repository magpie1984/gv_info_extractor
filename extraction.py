# This code uses the crome_ontology to f
import rdflib
from rdflib import Graph
import sys
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
reload(sys)
sys.setdefaultencoding('utf8')

st = StanfordNERTagger('stanford-ner-2017-06-09/classifiers/english.muc.7class.distsim.crf.ser.gz',
                                           'stanford-ner-2017-06-09/stanford-ner.jar',
                                           encoding='utf-8')

try:
    input_filename = sys.argv[1]
except:
    print("ERROR: Missing input file.")
    sys.exit(1)

with open(input_filename, 'r') as myfile:
    loaded_text=myfile.read().replace('\n', '')

tokenized_text = word_tokenize(loaded_text)
classified_text = st.tag(tokenized_text)

tokenized_display = ""

for token in classified_text:
    if token[1] == "O":
        tokenized_display = tokenized_display + str(token[0]) + " "
    else:
        tokenized_display = tokenized_display + str(token[1]) + " "

print("")
print("gun violence extractor v0.001")
print("")
print("")
print("------------------------------------")
print("loaded text:")
print(loaded_text)
print("")
print("tokenized text:")
print(tokenized_display)
print("------------------------------------")


print("")
print("comparison:")
for t, c in zip(tokenized_text, classified_text):
    print(t.encode('ascii','ignore'), c[1].encode('ascii','ignore'))

g = Graph()
g.parse('crime_news.owl')


test_query = """
PREFIX dbo: <http://www.semanticweb.org/michael/ontologies/crime_ontology#>
PREFIX w3: <http://www.w3.org/2000/01/rdf-schema#>
SELECT * WHERE {
    ?s w3:label "PERSON" .
    ?p w3:domain ?s .
    ?p w3:range ?o .
    ?o w3:label ?label
}
"""

is_victim_query = """
PREFIX dbo: <http://www.semanticweb.org/michael/ontologies/crime_ontology#>
PREFIX w3: <http://www.w3.org/2000/01/rdf-schema#>
SELECT * WHERE {
    dbo:Assailant w3:label ?assailant_label .
    dbo:Harms w3:domain dbo:Assailant .
    dbo:Harms w3:range dbo:Victim .
    dbo:Harms w3:label ?harms_label .
    dbo:Victim w3:label ?victim_label
}
"""

print("")
print("------------------------------------")
print("query test:")
a = g.query(is_victim_query)
if a:
  for d in a:
    for m in d:
        if "#" in m:
            print(m.split("#")[1])
        else:
            print(m)
        #print("\n")
  #print("Yup")
else:
  pass
  #print("nope")
print("------------------------------------")

