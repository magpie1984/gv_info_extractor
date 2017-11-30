import json, sys, os
import csv,math
from time import sleep, time
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize
import urllib, cStringIO
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from nltk.tag.stanford import StanfordPOSTagger
# import nltk
# nltk.internals.config_java(options='-Xmx8g')
english_postagger = StanfordPOSTagger("postagger/models/english-bidirectional-distsim.tagger", "postagger/stanford-postagger.jar")
english_postagger.tag("this is stanford postagger in nltk for python users".split())

def create_sgm_files():
	anno_art = pd.read_csv("../gs_data_from_gun_vio_db/Articles.tsv", sep='\t', names=["id","Article url", "Article title","Full text","Json"], error_bad_lines=False, encoding='utf-8', header = 0, engine='python')
	print len(anno_art)
	# anno_art.to_csv("../gs_data_from_gun_vio_db/Articles.tsv", sep='\t',  encoding='utf-8')
	test_list = open("/home/goonmeet/Documents/joint_ere_release/examples/test.lst", "a+")
	print anno_art.isnull().values
	for index, row in anno_art.iterrows():
		print row["id"].isdigit()
		if row["id"].isdigit() == False:
			continue
		f = open("/home/goonmeet/Documents/joint_ere_release/examples/test/" + (str(row["id"]) + ".sgm"), "w+")
		print row["id"]
		print type(row["Article title"])
		if row["Article title"] ==  "nan":
			row["Article title"] = "No title"
		print row["Full text"]
		if str(row["Full text"]) == "nan":
			continue
		f.write("<DOC>\n")
		#DOCID
		f.write("<DOCID> ")
		f.write(row["id"])
		f.write(" </DOCID>\n")
		#DOCTYPE
		f.write("<DOCTYPE SOURCE=\"newswire\"> NEWS STORY </DOCTYPE>\n")
		#DATETIME
		f.write("<DATETIME> 00000000 </DATETIME>\n")
		#BODY
		f.write("<BODY>\n")
		f.write("<HEADLINE>\n")
		f.write(row["Article title"])
		f.write("\n</HEADLINE>\n")
		#TEXT
		f.write("<TEXT>\n")
		f.write(row["Full text"])
		f.write("\n</TEXT>\n")
		f.write("</BODY>\n")
		f.write("</DOC>\n")
		f.close()
		test_list.write((str(row["id"]) + ".sgm\n"))
		#exit()
	# 	anno_art.set_value(index,"Article title",str(row["Article title"]).replace("\n", " "))
	# anno_art.to_csv("../gs_data_from_gun_vio_db/Articles.tsv", sep='\t',  encoding='utf-8', index=False)

def tag_articles():
	anno_art = pd.read_csv("../gs_data_from_gun_vio_db/Articles.tsv", sep='\t', names=["id","Article url", "Article title","Full text","Json","POS_Tagged_Article", "VB_Phrases"], error_bad_lines=False, encoding='utf-8', header = 0, engine='python')
	print len(anno_art)
	anno_art = anno_art.astype('object')
# 	anno_art['POS_Tagged_Article'] = "nan"
# 	anno_art['VB_Phrases'] = "nan"
# 	anno_art['POS_Tagged_Article'] = anno_art['POS_Tagged_Article'].astype('object')
# 	anno_art['VB_Phrases'] = anno_art['VB_Phrases'].astype('object')
	#anno_art.to_csv("../gs_data_from_gun_vio_db/Articles.tsv", sep='\t',  encoding='utf-8')
	#exit()
	big_vb_pharses = {}
	#print anno_art.isnull().values
	for index, row in anno_art.iterrows():
		print row.keys()
		if "VB_Phrases" in row.keys():
			try:
				if len(row["VB_Phrases"]) < 1:
					continue
				else:
					continue
			except:
				print row["id"]
				#sleep(10)
		print str(row["id"]).isdigit()
		if str(row["id"]).isdigit() == False:
			continue
		print row["id"]
		print type(row["Article title"])
		if row["Article title"] ==  "nan":
			row["Article title"] = "No title"
		print row["Full text"]
		if str(row["Full text"]) == "nan":
			continue
		tagged = english_postagger.tag(row["Full text"].split())
		print tagged
		anno_art.set_value(index, "POS_Tagged_Article", [tagged])
		print anno_art.POS_Tagged_Article.values
		v_p_l = []
		for x in range(len(tagged)):
			v_p = ""
			print v_p
			if 'V' in tagged[x][1]:
				print tagged[x]
				v_p = v_p + " "  + tagged[x][0]
				print v_p
				x = x + 1
				print range(len(tagged) - 1)
				while (x in range(len(tagged))):
					print len(tagged)
					#print tagged
					print x
					if 'V' in tagged[x][1]:
						print  tagged[x]
						v_p = v_p + " "  + tagged[x][0]
						print v_p
						#exit()
						x = x + 1
					else:
						break
			if v_p != "":
				v_p = v_p.strip()
				v_p_l.append(v_p)
		print v_p_l
		for x in v_p_l:
			if x not in big_vb_pharses.keys():
				big_vb_pharses[x] = 1
			else:
				big_vb_pharses[x] = big_vb_pharses[x] + 1
		anno_art.set_value(index, "VB_Phrases", [v_p_l])
		anno_art.to_csv("../gs_data_from_gun_vio_db/Articles.tsv", sep='\t',  encoding='utf-8', index=False)
		print big_vb_pharses
		#exit()
		
		
tag_articles()
