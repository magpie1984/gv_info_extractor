import xml.etree.ElementTree
import sys
import traceback
import sys

class XML_INFO:

    def __init__(self):
        self.parse_args()
        self.load_xml()
        self.entities = []
        self.events = []


    def parse_args(self):
        try:
            self.input_filename = sys.argv[1]
        except:
            print("ERROR: missing input file")
            print("Usage extraction.py <input>")
            sys.exit(1)

    def load_xml(self):
        self.xmldoc = xml.etree.ElementTree.parse(self.input_filename).getroot()

    def gather_entites(self):
        for entity in self.xmldoc.findall('./document/entity'):
            tup = ( entity.attrib['TYPE'],
                    entity.find('entity_mention/extent/charseq').text, 
                    entity.find('entity_mention/extent/charseq').attrib['START'],
                    entity.find('entity_mention/extent/charseq').attrib['END'],
                    entity.find('entity_mention/head/charseq').text,
                    entity.find('entity_mention/head/charseq').attrib['START'],
                    entity.find('entity_mention/head/charseq').attrib['END'] )
            self.entities.append(tup)

    def gather_events(self):
        for event in self.xmldoc.findall('./document/event'):
            event_entities = []
            for event_entity in event.findall('event_mention/event_mention_argument'):
                tup = ( event_entity.attrib['ROLE'],
                        event_entity.find('extent/charseq').text,
                        event_entity.find('extent/charseq').attrib['START'],
                        event_entity.find('extent/charseq').attrib['END'] )
                event_entities.append(tup)
            tup = (event.attrib['SUBTYPE'], event_entities)
            self.events.append(tup)


xml_info = XML_INFO()
xml_info.gather_entites()
xml_info.gather_events()

print("")
print("XML info extractor")
print("----------------------")
print("\nEntities:\n----------------------")

for item in xml_info.entities:
    print(item)

print("\nEvents:\n----------------------")

for item in xml_info.events:
    print(item)
print("")
