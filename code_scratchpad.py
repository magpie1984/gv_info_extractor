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



query = """
        PREFIX dbo: <http://www.semanticweb.org/michael/ontologies/crime_ontology#>
        PREFIX w3: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT * WHERE {
            ?s w3:label """ + "\"" + str(subject_label) + "\"" + """ .
            ?p w3:label """ + "\"" + str(predicate_label) + "\"" + """ .
            ?p w3:domain dbo:Assailant .
            ?p w3:range dbo:Victim .
            ?o w3:label """ + "\"" + str(object_label) + "\"" + """
        }
        """



        test_query = """
        PREFIX dbo: <http://www.semanticweb.org/michael/ontologies/crime_ontology#>
        PREFIX w3: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT * WHERE {
            ?s w3:label "PERSON" .
            ?p w3:domain ?s .
            ?p w3:range ?o .
            ?o w3:label ?label
        }
        """

        is_victim_query = """
        PREFIX dbo: <http://www.semanticweb.org/michael/ontologies/crime_ontology#>
        PREFIX w3: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT * WHERE {
            ?s w3:label """ + str("\"PERSON\"") + """ .
            ?p w3:label """ + str("\"shoots\"") + """ .
            ?p w3:domain dbo:Assailant .
            ?p w3:range dbo:Victim .
            ?o w3:label """ + str("\"PERSON\"") + """
        }
        """
  #print(auth)
  #print(victims)

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


auth=[]
a = g.query(query_authorities)
for row in a:
    for item in row:
        if isinstance(item, rdflib.term.Literal):
            auth.append(item)

victims=[]
a = g.query(query_victims)
for row in a:
    for item in row:
        if isinstance(item, rdflib.term.Literal):
            victims.append(item)



        """
        print("")
        print("------------------------------------")
        print("query test:")
        a = self.g.query(is_victim_query)
        if a:
          for d in a:
            print (d)
            #for m in d:
            #    if "#" in m:
            #        print(m)
            #        #print(m.split("#")[1])
            #    else:
            #        print(m)
            #    #print("\n")
          #print("Yup")
        else:
          pass
          #print("nope")
        print("------------------------------------")

       """ 