import rdflib
from rdflib import Graph
import sys
#from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
import re
import os
import json

reload(sys)
sys.setdefaultencoding('utf8')

class Relationship:

    def __init__(self):
        self.tagged_list = []
        #self.load_tagger()
        self.parse_args()
        self.load_input_json()
        self.load_ontology()
        self.load_tagged_list()
        self.create_lookup()

    def create_lookup(self):
        self.entity_lookup = []
        self.event_lookup = []
        self.other_lookup = []
        for item in self.tagged_list:
            if item[2] == 'entity':
                self.entity_lookup.append(item)
            if item[2] == 'event':
                self.event_lookup.append(item)
            if item[2] == 'none':
                self.other_lookup.append(item)

    def load_input_json(self):
        with open(self.input_filename, 'r') as myfile: 
            self.jsondata = json.load(myfile)

    def load_ontology(self):
        self.g = Graph()
        self.g.parse('crime_news.owl')

    def load_tagger(self):
        stan_dir = 'stanford-ner-2017-06-09/'
        stan_7_class = stan_dir+'classifiers/english.muc.7class.distsim.crf.ser.gz'
        stan_ner = stan_dir+'stanford-ner.jar'
        self.st = StanfordNERTagger(stan_7_class, stan_ner, encoding='utf-8')

    def load_tagged_list(self):
        c = 0
        t = self.jsondata['og_text']
        o = 0
        self.tagged_list = []
        events = self.jsondata['json_to_link_og_text_with_tagged_events']
        entities = self.jsondata['json_to_link_og_text_with_tagged_entities']
        evn_i=0
        ent_i=0
        json_tagged_tokenized = word_tokenize(self.jsondata['tagged_text'])
        for item in json_tagged_tokenized:
            if item == entities[ent_i]['tag']:
                e = entities[ent_i]
                to_append = (e['tag'], e['entity_tag_id'], "entity", e['entity_start_in_og_text'], e['entity_start_in_og_text'] + len(e['entity']))
                if ent_i < len(entities)-1: ent_i += 1
            elif item == events[evn_i]['tag']:
                e = events[evn_i]
                to_append = (e['tag'], e['event_tag_id'], "event", e['event_start_in_og_text'], e['event_start_in_og_text'] + len(e['event']) )
                if evn_i < len(events)-1: evn_i += 1
            else:
                to_append = (item, c, "none", t.find(item)+o, t.find(item)+o+len(item))
                o = o + t.find(item) + len(item)
                t = t[t.find(item)+len(item):len(t)]
                c += 1
            self.tagged_list.append(to_append)

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

    def scan_text(self):
        pointer_0 = 0
        pointer_1 = 0
        pointer_2 = 0
        pointer_3 = 0
        relationships = []

        while pointer_0 < len(self.tagged_list)-3:
            relationship = ["", 0, "", 0, "", 0, "", 0, 0]
            relationship_found = False
            percentage = float(pointer_0) / float(len(self.tagged_list)) * 100
            sys.stdout.write("\r%d%%" % percentage)
            sys.stdout.flush()
            for pointer_1 in range(pointer_0,len(self.tagged_list)-2):
                if relationship_found:
                    break
                if self.query_for_subject(self.tagged_list[pointer_1][0]) > 0:
                    #print("subject: " + self.tagged_list[pointer_1][0] + " [" + str(pointer_1) + "]")
                    relationship[1] = self.tagged_list[pointer_1][1]
                    relationship[2] = self.tagged_list[pointer_1][2]
                    relationship[7] = self.tagged_list[pointer_1][3]

                    for pointer_2 in range(pointer_1 + 1, pointer_1 + self.seperation_threshold):
                        if relationship_found:
                            break
                        try:
                            if self.query_for_predicate(self.tagged_list[pointer_2][0]) > 0:
                                relationship[3] = self.tagged_list[pointer_2][1]
                                relationship[4] = self.tagged_list[pointer_2][2]
                                for pointer_3 in range(pointer_2 + 1, pointer_2 + self.seperation_threshold):
                                    if relationship_found:
                                        break
                                    try:
                                        relationship[5] = self.tagged_list[pointer_3][1]
                                        relationship[6] = self.tagged_list[pointer_3][2]
                                        relationship[8] = self.tagged_list[pointer_3][4]
                                        output = self.query_ontology(self.tagged_list[pointer_1][0], self.tagged_list[pointer_2][0], self.tagged_list[pointer_3][0])
                                        relationship[0] = output
                                        if output:
                                            relationships.append(relationship)
                                            pointer_0 = pointer_3 + 1
                                            pointer_1 = pointer_3 + 1
                                            pointer_2 = pointer_3 + 1
                                            pointer_3 = pointer_3 + 1
                                            relationship_found = True
                                            break
                                    except:
                                        break
                        except:
                            break
            pointer_0 += 1
            #break
        return tuple(relationships)

rel = Relationship()
print("\n\nINFORMATION EXTRACTOR V0.0.1\n\nGoonmeet Bajaj\nMichael Partin\n\n")
print("-------ORIGINAL TEXT---------------------")
print(rel.jsondata['og_text'])
print("")
print("-------TAGGED TEXT-----------------------")
print(rel.jsondata['tagged_text'])
print("")
print("-------EVENTS----------------------------")
for event in rel.jsondata['json_to_link_og_text_with_tagged_events']:
    print(str(event['event_tag_id']) + " - " + event['tag'] + " - " + event['event'])
print("")
print("-------ENTITIES--------------------------")
for entity in rel.jsondata['json_to_link_og_text_with_tagged_entities']:
    print(str(entity['entity_tag_id']) + " - " + entity['tag'] + " - " + entity['entity'])
print("")

print("***Finding Relationships...")
result = rel.scan_text()
print("")
print("-------RELATIONSHIPS--------------------------")
i=0
for item in result:
    print(str(i) + " - " + item[0] + " - " + "\"" + rel.jsondata['og_text'][item[7]:item[8]] + "\"" )
    if item[2] == 'entity':
        g = rel.entity_lookup[item[1]]
    if item[2] == 'event':
        g = rel.event_lookup[item[1]] 
    if item[2] == 'none':
        g = rel.other_lookup[item[1]]
    print("    ["+ item[2] + "] - " + rel.jsondata['og_text'][g[3]:g[4]])

    if item[4] == 'entity':
        g = rel.entity_lookup[item[3]]
    if item[4] == 'event':
        g = rel.event_lookup[item[3]] 
    if item[4] == 'none':
        g = rel.other_lookup[item[3]]
    print("    ["+ item[4] + "] - " + rel.jsondata['og_text'][g[3]:g[4]])

    if item[6] == 'entity':
        g = rel.entity_lookup[item[5]]
    if item[6] == 'event':
        g = rel.event_lookup[item[5]] 
    if item[6] == 'none':
        g = rel.other_lookup[item[5]]
    print("    ["+ item[6] + "] - " + rel.jsondata['og_text'][g[3]:g[4]])
print("\n\n...done\n\n")

