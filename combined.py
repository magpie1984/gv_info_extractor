from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from SPARQLWrapper import SPARQLWrapper, JSON
import yaml

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

ontology_words = ["Plant","Beverage","Food","Company","Person"]

doc = []

with open('content.yml', 'r') as f:
    doc = yaml.load(f)

st = StanfordNERTagger('stanford-ner-2017-06-09/classifiers/english.muc.7class.distsim.crf.ser.gz',
                                           'stanford-ner-2017-06-09/stanford-ner.jar',
                                           encoding='utf-8')
# use NER on all the reviews
itemsFound = []
itemsFound_2 = []
for item in doc:

    text = item["Review"]
    print("***********************************************")
    print("Current Review Being Analysed: ")
    print()
    print(text)
    tokenized_text = word_tokenize(text)
    classified_text = st.tag(tokenized_text)

    last_tup = None
    for tup in classified_text:
        if tup[1] is not 'O':
            itemsFound.append(tup)

    tokenized_text = word_tokenize(text)
    for word in tokenized_text:
        query = """
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbp: <http://dbpedia.org/resource/>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?type where { dbp:""" + word.title() + """ rdf:type ?type .
            }
            """
        try:
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            for result in results["results"]["bindings"]:
                if "http://dbpedia.org/ontology" in result["type"]["value"]:
                    found = (word, result["type"]["value"].rsplit('/', 1)[1])
                    if found[1] in ontology_words:
                        itemsFound_2.append(found)
        except:
            pass

    print("\nResults From NER:\n")
    for item in itemsFound:
        print (item[0] + ": " + item[1])

    print("\nResults From KG:\n")
    for item in itemsFound_2:
        print (item[0] + ": " + item[1])
    print("                              ....Done")
    print()