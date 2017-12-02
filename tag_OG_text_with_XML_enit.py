import xml.etree.ElementTree
import sys, json, re
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
        for event_entity in event.findall('event_mention/anchor'):
            tup = ( event_entity.find('charseq').text,
                    event_entity.find('charseq').attrib['START'],
                    event_entity.find('charseq').attrib['END'] )
            event_entities.append(tup)
        tup = (event.attrib['SUBTYPE'], event_entities)
        events.append(tup)
    return events

def get_Text(xmldoc):
    return xml.etree.ElementTree.tostring(xmldoc.encode("utf-8"), method='text').strip().encode("utf-8")


def tag_og_text_with_entities(og_text, xml_info):
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
        temp["entity_tag_id"] = tag_num
        tag_num = tag_num + 1

        # print ("tag", tag[0])
        # print ("enity", tag[1])

        temp["entity"] = tag[1]
        # print ("search text", str(og_text[og_search_index:]))
        temp["entity_start_in_og_text"] = og_search_index + re.search(r'\b{}\b'.format(tag[1]), str(og_text[og_search_index:])).start() #og_text[og_search_index:].find(tag[1] + " ")
        temp["entity_end_in_og_text"] = temp["entity_start_in_og_text"] + len(tag[1])
        # print ("start index:",temp["entity_start_in_og_text"], "end index:", temp["entity_end_in_og_text"])
        #print temp["entity_start_in_og_text"]
        # print ("found text in og", og_text[temp["entity_start_in_og_text"]: temp["entity_end_in_og_text"]])
        # print ("found text in og with surr",og_text[temp["entity_start_in_og_text"]: temp["entity_end_in_og_text"] + 10])
        # print ("new search index:", temp["entity_end_in_og_text"])
        og_search_index = temp["entity_end_in_og_text"]

        # print  "\n\n\n\n\n\n"
        #find entity in tagged_text
        # print ("search tagged_text", str(tagged_text[tags_search_index:]))
        temp["tag_text_start_in_tagged_text"] = tags_search_index + re.search(r'\b{}\b'.format(tag[1]), str(tagged_text[tags_search_index:])).start() #og_text[og_search_index:].find(tag[1] + " ")
        replace_index = temp["tag_text_start_in_tagged_text"] + len(tag[1])
        # print ("start index:",temp["tag_text_start_in_tagged_text"], "end index:", replace_index)
        tagged_text = tagged_text[:temp["tag_text_start_in_tagged_text"]] +  tag[0] + tagged_text[replace_index:]
        temp["tag_text_end_in_tagged_text"] = temp["tag_text_start_in_tagged_text"] + len(tag[0])
        tags_search_index = temp["tag_text_end_in_tagged_text"]
        # print ("new tagged search index:", tags_search_index)
        # print ("search tagged_text", str(tagged_text[tags_search_index:]))
        # print "\n"
        # print tagged_text
        # print  "\n\n\n\n\n\n"

        tags_and_texts.append(temp)
        # print temp
        #exit()
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

def tag_og_text_with_events(doc_tagged, og_text, xml_info):
    xml_info_events = gather_events(xml_info)
    doc_tagged["xml_info_events"] = xml_info_events
    tagged_text = doc_tagged["tagged_text"]
    tags_and_texts = []
    og_search_index = 0
    tags_search_index = 0
    tag_num = 0
    for tag in xml_info_events:
        # print tag[1]
        # print og_text
        temp = {}
        temp["tag"] = tag[0].upper()
        temp["event_tag_id"] = tag_num
        tag_num = tag_num + 1

        #entity info
        temp["event"] = tag[1][0][0]
        # print temp["event"]
        temp["event_start_in_og_text"] = og_search_index + re.search(r'\b{}\b'.format(temp["event"]), str(og_text[og_search_index:])).start()
        og_search_index = temp["event_start_in_og_text"] + len(temp["event"])
        temp["event_end_in_og_text"] = og_search_index
        # print temp["event_start_in_og_text"]
        # print temp["event_end_in_og_text"]
        # print og_text[temp["event_start_in_og_text"] : temp["event_end_in_og_text"]]

        #tag start end
        # print tagged_text
        # print tags_search_index
        temp["tag_text_start_in_tagged_text"] = tags_search_index + re.search(r'\b{}\b'.format(temp["event"]), str(tagged_text[tags_search_index:])).start()
        replace_index = temp["tag_text_start_in_tagged_text"] + len(temp["event"])
        # print temp["tag_text_start_in_tagged_text"]
        tagged_text = tagged_text[:temp["tag_text_start_in_tagged_text"]] +  tag[0].upper() + tagged_text[replace_index:]
        temp["tag_text_end_in_tagged_text"] = temp["tag_text_start_in_tagged_text"] + len(temp["tag"])
        # print tags_search_index
        tags_search_index = temp["tag_text_end_in_tagged_text"]
        # print tagged_text[temp["tag_text_start_in_tagged_text"] : temp["tag_text_end_in_tagged_text"]]
        tags_and_texts.append(temp)
    doc_tagged["tagged_text"] = tagged_text
    doc_tagged["json_to_link_og_text_with_tagged_events"] = tags_and_texts
    # for x in tags_and_texts:
    #     #print x["tag"]
    #     print ("enity", og_text[int(x["event_start_in_og_text"]) : int(x["event_end_in_og_text"])])
    #     print ("tag from xml", x["tag"])
    #     print ("tag in text",tagged_text[int(x["tag_text_start_in_tagged_text"]) : int(x["tag_text_end_in_tagged_text"])])
    # print len(xml_info_events)
    # exit()
    return doc_tagged



if __name__ == '__main__':
    data_gs_file = os.listdir("DATASET_FOR_FINAL")

    for gs_file in data_gs_file:
        if gs_file.endswith(".txt"):
            #print gs_file
            text_file = open("DATASET_FOR_FINAL/" + gs_file, "r")
            #og_xml = load_xml(text_file)
            og_text = text_file.read().encode("utf-8")
            og_text = og_text.strip("\n")
            xml_file = open("DATASET_FOR_FINAL/" + gs_file.replace(".txt", ".sgm.apf.xml"), "r")
            xml_info = load_xml(xml_file)
            doc_tagged = tag_og_text_with_entities(og_text, xml_info)#tag_og_text(og_xml, xml_info)#tag_og_text(og_text, xml_info)
            doc_tagged = tag_og_text_with_events(doc_tagged, og_text, xml_info)
            doc_tagged["file"] = gs_file
            #print doc_tagged
            json.dump(doc_tagged, open("DATASET_FOR_FINAL/tagged_" + gs_file.replace(".txt",".json"), "w"), indent=2, ensure_ascii=True)
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
