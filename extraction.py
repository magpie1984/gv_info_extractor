# This code uses the crome_ontology to f
import rdflib
from rdflib import Graph
import sys
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
import re
reload(sys)
sys.setdefaultencoding('utf8')

class Extractor:

    def load_tagger(self):
        stan_7_class = 'stanford-ner-2017-06-09/classifiers/english.muc.7class.distsim.crf.ser.gz'
        stan_ner = 'stanford-ner-2017-06-09/stanford-ner.jar'
        self.st = StanfordNERTagger(stan_7_class, stan_ner, encoding='utf-8')

    def parse_args(self):
        try:
            self.input_filename = sys.argv[1]
        except:
            print("ERROR: missing input file")
            print("Usage extraction.py <input> <seperation_threshold>")
            sys.exit(1)

        try:
            self.seperation_threshold = int(sys.argv[2])
        except:
            print("ERROR: missing seperation_threshold")
            print("Usage extraction.py <input> <seperation_threshold>")
            sys.exit(1)

    def load_input(self):
        with open(self.input_filename, 'r') as myfile:
            self.loaded_text=myfile.read().replace('\n\n', ' ')

    def tokenize_and_tag(self):
        self.tokenized_text = word_tokenize(self.loaded_text)
        self.tagged_text = self.st.tag(self.tokenized_text)
        self.tagged_list = []

        self.tokenized_display = ""

        for token in self.tagged_text:
            if token[1] == "O":
                self.tokenized_display = self.tokenized_display + str(token[0]) + " "
                self.tagged_list.append(str(token[0]))
            else:
                self.tokenized_display = self.tokenized_display + str(token[1]) + " "
                self.tagged_list.append(str(token[1]))

    def display(self):
        print("")
        print("gun violence extractor v0.002")
        print("")
        print("")
        print("------------------------------------")
        print("loaded text:")
        print(self.loaded_text)
        print("")
        print("tokenized text:")
        print(self.tokenized_display)
        print("------------------------------------")

    def load_ontology(self):
        self.g = Graph()
        self.g.parse('crime_news.owl')

    def __init__(self):
        self.load_tagger()
        self.parse_args()
        self.load_input()
        self.tokenize_and_tag()
        self.display()
        self.load_ontology()

    def build_tokenized_expanded(self):
        text = self.loaded_text
        tagged_offset = 0
        offset = 0
        pos = int(0)
        self.tokenized_expanded = []
        for item in self.tokenized_text:
            output = (item, self.tagged_list[tagged_offset], text.find(item) + offset, text.find(item)+len(item) - 1 + offset)
            offset = offset + text.find(item)+len(item)
            text = text[text.find(item)+len(item):len(text)]
            self.tokenized_expanded.append(output)
            tagged_offset += 1

    def build_final_tagged(self):
        #TODO: With the tokenized_expanded list:
        # (1) combine PERSONs LOCATIONs, ORGANIZATIONs, DATEs that are close
        # (2) search for other multiword tokens that can be combined into a single tag
        self.final_tagged=[]
        self.tokens_to_check = []
        cur_item = 0
        for item in self.tokenized_expanded:
            if item[1] == "PERSON" or item[1] == "LOCATION" or item[1] == "ORGANIZATION" or item[1] =="DATE":
                self.tokens_to_check.append(cur_item)
            cur_item += 1
        tokens_used=[]
        for item in self.tokens_to_check:
            tag_start = self.tokenized_expanded[item][2]
            tag_end = self.tokenized_expanded[item][3]
            for x in range(item+1, item + self.seperation_threshold):
                if self.tokenized_expanded[item][1] == self.tokenized_expanded[x][1] and x not in tokens_used and item not in tokens_used:
                    tokens_used.append(x)
                    tag_end = self.tokenized_expanded[x][3]
            if item not in tokens_used:    
                new_tag = (self.loaded_text[tag_start:tag_end+1], self.tokenized_expanded[item][1], tag_start, tag_end)
                self.final_tagged.append(new_tag)



    def check_tokenized_expanded(self):
        for item in self.tokenized_expanded:
            print(self.loaded_text[item[1]:item[2]+1])


    def scan_text(self, seperation_threshold):
        pointer_0 = 0
        pointer_1 = 0
        pointer_2 = 0
        pointer_3 = 0
        relationships = []

        print("maximum length: " + str(len(self.tagged_text)))

        while pointer_0 < len(self.tagged_text)-3:
            relationship = ["", 0,0,0,0,0,0]
            relationship_found = False
            #print(pointer_1, pointer_2, pointer_3)
            for pointer_1 in range(pointer_0,len(self.tagged_text)):
                if relationship_found:
                    break
                if self.query_for_subject(self.tagged_list[pointer_1]) > 0:
                    print("subject: " + self.tagged_list[pointer_1] + " [" + str(pointer_1) + "]")
                    relationship[1] = pointer_1
                    try:
                        sub_len = 1
                        for subject_length in range(pointer_1+1, pointer_1+3):
                            if self.tagged_list[pointer_1] == self.tagged_list[subject_length]:
                                sub_len += 1
                        relationship[4] = sub_len
                    except:
                        break
                    for pointer_2 in range(pointer_1 + 1, pointer_1 + seperation_threshold):
                        if relationship_found:
                            break
                        try:
                            if self.query_for_predicate(self.tagged_list[pointer_2]) > 0:
                                print("predicate: " + self.tagged_list[pointer_2] + " [" + str(pointer_2) + "]")
                                relationship[2] = pointer_2
                                for pointer_3 in range(pointer_2 + 1, pointer_2 + seperation_threshold):
                                    if relationship_found:
                                        break
                                    try:
                                        print("object: " + self.tagged_list[pointer_3] + " [" + str(pointer_3) + "]")
                                        relationship[3] = pointer_3
                                        print(self.tagged_list[pointer_1], self.tagged_list[pointer_2], self.tagged_list[pointer_3])
                                        output = self.query_ontology(self.tagged_list[pointer_1], self.tagged_list[pointer_2], self.tagged_list[pointer_3])
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
            break
            #print("got here")
            #pointer_0 += 1
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
a.build_tokenized_expanded()
for item in a.tokenized_expanded:
    print(item)

print("")

a.build_final_tagged()
for item in a.final_tagged:
    print(item)
#a.check_tokenized_expanded()
"""
data = a.scan_text(a.seperation_threshold)
print("------------------------------------")
print("")
print("results:")
print("")
print(data)
"""