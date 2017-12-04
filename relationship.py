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
        #self.show_all_tagged()

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
        self.og_text = self.jsondata['og_text'].replace("\n", " ").replace("\u", "    ")
        self.tag_text = self.jsondata['tagged_text'].replace("\n", " ").replace("\u", "    ")

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
        t = self.jsondata['og_text'].replace("\n", " ")
        o = 0
        self.tagged_list = []
        events = self.jsondata['json_to_link_og_text_with_tagged_events']
        entities = self.jsondata['json_to_link_og_text_with_tagged_entities']
        evn_i=0
        ent_i=0
        json_tagged_tokenized = word_tokenize(self.tag_text)
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

    def show_all_tagged(self):
        k=0
        print("\n\n###################################")
        for item in self.tagged_list:
            print("[" + str(k) + "] " + item[0] + " - " + self.og_text[item[3]:item[4]])
            k +=1
        print("###################################\n\n")

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

    def write_percentage(self, v1, v2):
        percentage = float(v1) / float(len(v2)) * 100
        sys.stdout.write("\r%d%%" % percentage)
        sys.stdout.flush()

    def scan_text(self):
        last_ent_found_mem = 0
        last_ent_found = 0
        end_reached = False
        t_l = self.tagged_list
        s_t = self.seperation_threshold
        p_0 = 0
        p_1 = 0
        p_2 = 0
        p_3 = 0
        rs = []

        while p_0 < len(t_l)-3:
            r = ["", 0, "", 0, "", 0, "", 0, 0]
            r_found = False
            #self.write_percentage(p_0, t_l)
            for p_1 in range(p_0,len(t_l)-2):
                self.write_percentage(p_1, t_l)
                if r_found:
                    break
                if self.query_for_subject(t_l[p_1][0]) > 0:
                    last_ent_found_mem = last_ent_found
                    if last_ent_found_mem == p_1:
                        return tuple(rs)

                    last_ent_found = p_1
                    
                    r[1] = t_l[p_1][1]
                    r[2] = t_l[p_1][2]
                    r[7] = t_l[p_1][3]
                    for p_2 in range(p_1 + 1, p_1 + s_t):
                        if r_found:
                            break
                        try:
                            if self.query_for_predicate(t_l[p_2][0]) > 0:
                                r[3] = t_l[p_2][1]
                                r[4] = t_l[p_2][2]
                                for p_3 in range(p_2 + 1, p_2 + s_t):
                                    if r_found:
                                        break
                                    try:
                                        output = self.query_ontology(t_l[p_1][0], t_l[p_2][0], t_l[p_3][0])
                                        if output:
                                            r[0] = output
                                            r[5] = t_l[p_3][1]
                                            r[6] = t_l[p_3][2]
                                            r[8] = t_l[p_3][4]
                                            r_to_add = (r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8])
                                            rs.append(r_to_add)
                                            p_3 += 1
                                    except:
                                        end_reached = True
                                        break
                        except:
                            end_reached = True
                            break
                p_0 = last_ent_found
        return tuple(rs)

rel = Relationship()
print("\n\nINFORMATION EXTRACTOR V0.0.1\n\nGoonmeet Bajaj\nMichael Partin\n\n")
print("-------ORIGINAL TEXT---------------------")
print(rel.og_text)
print("")
print("-------TAGGED TEXT-----------------------")
print(rel.tag_text)
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
    print(str(i) + " - " + item[0] + " - " + "\"" + rel.og_text[item[7]:item[8]] + "\"" )
    if item[2] == 'entity':
        g = rel.entity_lookup[item[1]]
    if item[2] == 'event':
        g = rel.event_lookup[item[1]] 
    if item[2] == 'none':
        g = rel.other_lookup[item[1]]
    print("    ["+ item[2] + "] - " + rel.og_text[g[3]:g[4]])

    if item[4] == 'entity':
        g = rel.entity_lookup[item[3]]
    if item[4] == 'event':
        g = rel.event_lookup[item[3]] 
    if item[4] == 'none':
        g = rel.other_lookup[item[3]]
    print("    ["+ item[4] + "] - " + rel.og_text[g[3]:g[4]])

    if item[6] == 'entity':
        g = rel.entity_lookup[item[5]]
    if item[6] == 'event':
        g = rel.event_lookup[item[5]] 
    if item[6] == 'none':
        g = rel.other_lookup[item[5]]
    print("    ["+ item[6] + "] - " + rel.og_text[g[3]:g[4]])
    i += 1
print("\n\n...done\n\n")