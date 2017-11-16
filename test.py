# This code uses the crime_ontology.owl to find relationships within a text
import rdflib
from rdflib import Graph


example_text = "police found PERSON"

g = Graph()
g.parse('crime_news.owl')

query_basic = """
PREFIX dbo: <http://www.semanticweb.org/michael/ontologies/crime_ontology#>
PREFIX w3: <http://www.w3.org/2000/01/rdf-schema#>
SELECT * WHERE {
    ?s ?p ?o .
}
"""

query_authorities = """
PREFIX dbo: <http://www.semanticweb.org/michael/ontologies/crime_ontology#>
PREFIX w3: <http://www.w3.org/2000/01/rdf-schema#>
SELECT * WHERE {
    ?s dbo:apprehends ?o .
    ?s w3:label ?authorities .
    #?o w3:label ?victim
}
"""

query_victims = """
PREFIX dbo: <http://www.semanticweb.org/michael/ontologies/crime_ontology#>
PREFIX w3: <http://www.w3.org/2000/01/rdf-schema#>
SELECT * WHERE {
    ?s dbo:apprehends ?o .
    #?s w3:label ?authorities .
    ?o w3:label ?victim
}
"""

query_ask = """
PREFIX dbo: <http://www.semanticweb.org/michael/ontologies/crime_ontology#>
PREFIX w3: <http://www.w3.org/2000/01/rdf-schema#>
SELECT * WHERE {
    ?s w3:label "dude" .
    ?o w3:label "PERSON" .
    ?s dbo:apprehends ?o
}
"""



query_ask_2 = """
PREFIX dbo: <http://www.semanticweb.org/michael/ontologies/crime_ontology#>
PREFIX w3: <http://www.w3.org/2000/01/rdf-schema#>
SELECT * WHERE {
    ?s w3:label "PERSON" .
    ?p w3:domain ?s .
    ?p w3:range ?o .
    ?o w3:label ?label
}
"""


auth=[]
a = g.query(query_authorities)
for row in a:
    #print(row)
    for item in row:
        if isinstance(item, rdflib.term.Literal):
            auth.append(item)

victims=[]
a = g.query(query_victims)
for row in a:
    #print(row)
    for item in row:
        if isinstance(item, rdflib.term.Literal):
            victims.append(item)
"""
a = g.query(query_ask)
if a:
  print("Yup")
else:
  print("Nope")
for row in a:
    if row:
      print("Yup")
    #print(row)
    #for item in row:
    #    if isinstance(item, rdflib.term.Literal):
    #        victims.append(item)
"""


print("query test")
a = g.query(query_ask_2)
if a:
  #print(auth)
  #print(victims)
  for d in a:
    print(d)
  print("Yup")
else:
  print("nope")
#for row in a:
#    for item in row:
#        print(item)
    #print(row)
    #for item in row:
    #    if isinstance(item, rdflib.term.Literal):
    #        victims.append(item)

"""
print("complete db")
a = g.query(query_basic)
for row in a:
    print (row)


"""
