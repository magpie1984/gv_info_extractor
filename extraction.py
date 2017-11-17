# This code uses the crome_ontology to f
import rdflib
from rdflib import Graph
import sys
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
reload(sys)
sys.setdefaultencoding('utf8')

class Extractor:

    def __init__(self):

        stan_7_class = 'stanford-ner-2017-06-09/classifiers/english.muc.7class.distsim.crf.ser.gz'
        stan_ner = 'stanford-ner-2017-06-09/stanford-ner.jar'
        st = StanfordNERTagger(stan_7_class, stan_ner, encoding='utf-8')

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
        #for t, c in zip(tokenized_text, classified_text):
        #    print(t.encode('ascii','ignore'), c[1].encode('ascii','ignore'))

        self.g = Graph()
        self.g.parse('crime_news.owl')


    def query_ontology(self, subject_label, predicate_label, object_label):
        query = """
        PREFIX dbo: <http://www.semanticweb.org/michael/ontologies/crime_ontology#>
        PREFIX w3: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT * WHERE {
            ?s w3:label """ + "\"" + str(subject_label) + "\"" + """ .
            ?p w3:label """ + "\"" + str(predicate_label) + "\"" + """ .
            ?p w3:domain ?s .
            ?p w3:range ?o .
            ?o w3:label """ + "\"" + str(object_label) + "\"" + """
        }
        """
        a = self.g.query(query)

        relationship = ""

        if a:
            for d in a:
                for m in d:
                    if "#" in m:
                        if len(relationship) == 0:
                            relationship = relationship + m.split("#")[1]
                        else:
                            relationship = relationship + " " + m.split("#")[1]
                    else:
                        if len(relationship) == 0:
                            relationship = relationship + m
                        else:
                            relationship = relationship + " " + m

        return relationship

a = Extractor()
print (a.query_ontology("PERSON", "shoots", "PERSON"))