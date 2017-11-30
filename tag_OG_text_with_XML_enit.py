import xml.etree.ElementTree
import sys
import traceback
import os
from time import sleep
reload(sys)
sys.setdefaultencoding('utf8')

def load_xml(input_filename):
    xmldoc = xml.etree.ElementTree.parse(input_filename).getroot()
    return xmldoc

def gather_entites(xmldoc):
    entities = []
    for entity in xmldoc.findall('./document/entity'):
        tup = ( entity.attrib['TYPE'],
                # entity.find('entity_mention/extent/charseq').text,
                # entity.find('entity_mention/extent/charseq').attrib['START'],
                # entity.find('entity_mention/extent/charseq').attrib['END'],
                entity.find('entity_mention/head/charseq').text,
                entity.find('entity_mention/head/charseq').attrib['START'],
                entity.find('entity_mention/head/charseq').attrib['END'] )
        entities.append(tup)
    return entities

def gather_events(xmldoc):
    events = []
    for event in xmldoc.findall('./document/event'):
        event_entities = []
        for event_entity in event.findall('event_mention/event_mention_argument'):
            tup = ( event_entity.attrib['ROLE'],
                    event_entity.find('extent/charseq').text,
                    event_entity.find('extent/charseq').attrib['START'],
                    event_entity.find('extent/charseq').attrib['END'] )
            event_entities.append(tup)
        tup = (event.attrib['SUBTYPE'], event_entities)
        events.append(tup)
    return events

def get_Text(xmldoc):
    return xml.etree.ElementTree.tostring(xmldoc.encode("utf-8"), method='text').strip().encode("utf-8")


def tag_og_text(og_text, xml_info):
    xml_info_entitites = gather_entites(xml_info)
    tagged_text = og_text
    tags_and_texts = []
    # print xml_info_entitites
    # print ""
    og_search_index = 0
    tags_search_index = 0
    tag_num = 0
    doc_tagged = {}
    doc_tagged["og_text"] = og_text
    doc_tagged["xml_info_entitites"] = xml_info_entitites
    for tag in xml_info_entitites:
        temp = {}
        og_text_list = list(og_text)

        #tag info
        temp["tag"] = tag[0]
        temp["tag_id"] = tag_num
        tag_num = tag_num + 1

        #entity info
        temp["entity"] = tag[1]
        temp["entity_start_in_og_text"] = og_search_index + og_text[og_search_index:].find(tag[1])
        og_search_index = og_text.find(tag[1]) + len(tag[1])
        temp["entity_end_in_og_text"] = og_search_index

        #tag start end
        tagged_text = tagged_text.replace(tag[1], tag[0], 1)
        # print tags_search_index
        temp["tag_text_start_in_tagged_text"] = tags_search_index + tagged_text[tags_search_index:].find(tag[0])
        # print temp["tag_text_start_in_tagged_text"]
        # print tagged_text[tags_search_index:]
        tags_search_index = temp["tag_text_start_in_tagged_text"] + len(tag[0])
        # print tags_search_index
        temp["tag_text_end_in_tagged_text"] = tags_search_index

        tags_and_texts.append(temp)
        # print temp
    #Wexit()
    # print og_text
    # print ""
    # print tagged_text
    # for x in tags_and_texts:
    #     #print x["tag"]
    #     print ("enity", og_text[int(x["entity_start_in_og_text"]) : int(x["entity_end_in_og_text"])])
    #     print ("tag from xml", x["tag"])
    #     print ("tag in text",tagged_text[int(x["tag_text_start_in_tagged_text"]) : int(x["tag_text_end_in_tagged_text"])])
    # print len(xml_info_entitites)
    doc_tagged["tagged_text"] = tagged_text
    doc_tagged["json_to_link_og_text_with_tagged_entities"] = tags_and_texts
    #exit()
    return doc_tagged


if __name__ == '__main__':
    data_gs_file = os.listdir("DATASET_FOR_FINAL")

    for gs_file in data_gs_file:
        if gs_file.endswith(".txt"):
            # print gs_file
            text_file = open("DATASET_FOR_FINAL/" + gs_file, "r")
            #og_xml = load_xml(text_file)
            og_text = text_file.read().encode("utf-8")
            xml_file = open("DATASET_FOR_FINAL/" + gs_file.replace(".txt", ".sgm.apf.xml"), "r")
            xml_info = load_xml(xml_file)
            doc_tagged = tag_og_text(og_text, xml_info)#tag_og_text(og_xml, xml_info)#tag_og_text(og_text, xml_info)
            doc_tagged["file"] = gs_file
            print doc_tagged
            #exit()

# input_filename = sys.argv[1]
#
# print("")
# print("XML info extractor")
# xml_info = load_xml(input_filename)
# print("----------------------")
#
# print("\nEntities:\n----------------------")
# xml_info_entitites = gather_entites(xml_info)
# for item in xml_info_entitites:
#     print(item)
#
# print("\nEvents:\n----------------------")
# xml_info_events = gather_events(xml_info)
# print len(xml_info_events)
# for item in xml_info_events:
#     print(item)
# print("")
