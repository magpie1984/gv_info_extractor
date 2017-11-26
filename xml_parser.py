import xml.etree.ElementTree
import sys



try:
    input_filename = sys.argv[1]
except:
    print("ERROR: missing input file")
    print("Usage extraction.py <input>")
    sys.exit(1)

e = xml.etree.ElementTree.parse(input_filename).getroot()

#for elm in e.findall('./document/entity'):
#    for head_text in elm.findall('entity_mention/head/charseq'):
#        output = elm.attrib['TYPE'] + ", " + head_text.text
#        print(output)

for elm in e.findall('./document/event'):
    output = ""
    event_mention = elm.findall('event_mention/event_mention_argument')
    anchor = elm.findall('event_mention/anchor')
    for em in event_mention:
        output = output + em.attrib['ROLE'] + "; "
    for an in anchor:
        charseq = an.findall('charseq')
        for ch_sq in charseq:
            output = output + ch_sq.text
    print (output)


