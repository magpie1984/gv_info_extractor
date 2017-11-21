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

        self.tokenized_text = word_tokenize(loaded_text)
        self.classified_text = st.tag(self.tokenized_text)
        self.classified_list = []

        tokenized_display = ""

        for token in self.classified_text:
            if token[1] == "O":
                tokenized_display = tokenized_display + str(token[0]) + " "
                self.classified_list.append(str(token[0]))
            else:
                tokenized_display = tokenized_display + str(token[1]) + " "
                self.classified_list.append(str(token[1]))

        print("")
        print("gun violence extractor v0.002")
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
        print("")
        #for t, c in zip(tokenized_text, classified_text):
        #    print(t.encode('ascii','ignore'), c[1].encode('ascii','ignore'))

        self.g = Graph()
        self.g.parse('crime_news.owl')

    def scan_text(self, seperation_threshold):
        pointer_0 = 0
        pointer_1 = 0
        pointer_2 = 0
        pointer_3 = 0
        relationships = []

        while pointer_0 < len(self.classified_text)-3:
            relationship = ["", 0,0,0,0,0,0]
            relationship_found = False
            #print(pointer_1, pointer_2, pointer_3)
            for pointer_1 in range(pointer_0,len(self.classified_text)):
                if relationship_found:
                    break
                if self.query_for_subject(self.classified_list[pointer_1]) > 0:
                    print("subject: " + self.classified_list[pointer_1] + " [" + str(pointer_1) + "]")
                    relationship[1] = pointer_1
                    try:
                        sub_len = 1
                        for subject_length in range(pointer_1+1, pointer_1+3):
                            if self.classified_list[pointer_1] == self.classified_list[subject_length]:
                                sub_len += 1
                        relationship[4] = sub_len
                    except:
                        break
                    for pointer_2 in range(pointer_1 + 1, pointer_1 + seperation_threshold):
                        if relationship_found:
                            break
                        try:
                            if self.query_for_predicate(self.classified_list[pointer_2]) > 0:
                                print("predicate: " + self.classified_list[pointer_2] + " [" + str(pointer_2) + "]")
                                relationship[2] = pointer_2
                                for pointer_3 in range(pointer_2 + 1, pointer_2 + seperation_threshold):
                                    if relationship_found:
                                        break
                                    try:
                                        print("object: " + self.classified_list[pointer_3] + " [" + str(pointer_3) + "]")
                                        relationship[3] = pointer_3
                                        print(self.classified_list[pointer_1], self.classified_list[pointer_2], self.classified_list[pointer_3])
                                        output = self.query_ontology(self.classified_list[pointer_1], self.classified_list[pointer_2], self.classified_list[pointer_3])
                                        #print(output)
                                        relationship[0] = output
                                        if output:
                                            relationships.append(relationship)
                                            pointer_0 = pointer_3 + 1
                                            pointer_1 = pointer_3 + 1
                                            pointer_2 = pointer_3 + 1
                                            pointer_3 = pointer_3 + 1
                                            relationship_found = True
                                            print("")
                                            break
                                    except:
                                        break
                        except:
                            break
            pointer_0 += 1
        return tuple(relationships)


    def query_for_subject(self, subject_label):
        query = """
        PREFIX dbo: <http://www.semanticweb.org/michael/ontologies/crime_ontology#>
        PREFIX w3: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT * WHERE {
            ?s w3:label """ + "\"" + str(subject_label) + "\"" + """ .
            ?p w3:domain ?s .
            ?p w3:range ?o .
            ?o w3:label ?ol
        }
        """
        a = self.g.query(query)
        hits = 0
        for b in a:
            hits += 1
        return hits


    def query_for_predicate(self, predicate_label):
        query = """
        PREFIX dbo: <http://www.semanticweb.org/michael/ontologies/crime_ontology#>
        PREFIX w3: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT * WHERE {
            ?s w3:label ?sl .
            ?p w3:label """ + "\"" + str(predicate_label) + "\"" + """ .
            ?p w3:domain ?s .
            ?p w3:range ?o .
            ?o w3:label ?ol
        }
        """
        a = self.g.query(query)
        hits = 0
        for b in a:
            hits += 1
        return hits


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
data = a.scan_text(3)
print("------------------------------------")
print("")
print("results:")
print("")
print(data)
