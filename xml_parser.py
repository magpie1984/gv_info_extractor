import xml.etree.ElementTree
import sys
import traceback



#try:
#    input_filename = sys.argv[1]
#except:
#    print("ERROR: missing input file")
#    print("Usage extraction.py <input>")
#    sys.exit(1)

unique_set = []
unique_set_text = []
file_match = []
anchors = []


for input_filename in range(0,1000):

    try:

        e = xml.etree.ElementTree.parse("DATASET_FOR_FINAL/" + str(input_filename) + ".sgm.apf.xml").getroot()

        for elm in e.findall('./document/event'):
            count = 0
            output = ""
            text = ""
            subtype = elm.attrib['SUBTYPE']
            event_mention = elm.findall('event_mention/event_mention_argument')
            output = subtype + ";"
            text = elm.find('event_mention/anchor/charseq').text + ';'
            anchor = elm.findall('event_mention/anchor')
            for em in event_mention:
                output = output + em.attrib['ROLE'] + ";"
                text = text + em.find('extent/charseq').text + ';'
                count += 1

            for an in anchor:
                charseq = an.find('charseq')
                if elm.attrib['SUBTYPE'] == "Attack":
                        anchors.append(charseq.text)

            if count == 2:
                triple = output.split(";")
                triple_text = text.split(";")

                if triple not in unique_set:
                    unique_set.append(triple)
                    unique_set_text.append(triple_text)
                    file_match.append("xml/" + str(input_filename) + ".sgm.apf.xml")





    except:
        #traceback.print_exc()
        pass

for item, item_text, filen in zip(unique_set, unique_set_text, file_match):
    print ("From: " + filen)
    print (item[1], item[0], item[2])
    print (item_text[1], item_text[0], item_text[2])
    print ("")

print ("anchors:\n\n\n")

anchor = list(set(anchors))
for a in anchor:
    print(a)
