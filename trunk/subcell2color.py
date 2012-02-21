#!/usr/bin/env python

import sys
import pg

db_knowledge   = ['localhost','5432','ljj','knowledge']
db_predictions = ['localhost','5432','ljj','predictions']
db_textmining  = ['localhost','5432','ljj','textmining']

goloc2label = {'GO:0005576':'ex',
			   'GO:0005634':'nu',
			   'GO:0005739':'mi',
			   'GO:0005764':'ly',
			   'GO:0005768':'en',
			   'GO:0005773':'va',
			   'GO:0005777':'pe',
			   'GO:0005783':'er',
			   'GO:0005794':'go',
			   'GO:0005829':'cy',
			   'GO:0005856':'cs',
			   'GO:0005886':'pm',
			   'GO:0009507':'ch'}

	

tax_animals =  "6085 6182 6238 6239 6945 7070 7159 7165 7176 7217 7222 7227 "
tax_animals += "7237 7244 7245 7260 7425 7460 7668 7719 7739 7955 8090 8364 "
tax_animals += "9031 9258 9361 9544 9598 9600 9606 9615 9685 9796 9823 9913 "
tax_animals += "9986 10090 10116 10141 10228 13616 28377 31033 31234 45351 "
tax_animals += "51511 59729 69293 99883 121224 135651 281687"

tax_fungi   =  "4896 4924 4929 4932 4952 4959 5057 5059 5061 5062 5085 5141 "
tax_fungi   += "5270 5306 5476 5518 6035 28985 29883 33169 33178 36630 36914 "
tax_fungi   += "51453 104341 148305 162425 214684 222929 332648 436907 500485 "
tax_fungi   += "559295 559307 573826 644223 665079"

tax_plants  =  "3055 3218 3694 3702 4558 15368 29760 39946 39947 59689 70448 436017"



def color(w):
	return "#%02x%02x%02x" % (255*(1-w), 255*(1-0.5*w), 255*(1-w))


def get_connection(conn_info):
	return pg.connect(host=conn_info[0], port=int(conn_info[1]), user=conn_info[2], passwd='', dbname=conn_info[3])


def protein_hash(result):
	myhash = {}
	for id1, id2, score in result:
		if id1 not in myhash:
			myhash[id1] = {}
		myhash[id1][id2] = score
	return myhash


def filter_compartments(result):
	global goloc2label
	filtered = []
	for row in result:
		if row[1] in goloc2label:
			filtered.append(row)
	return filtered

	
def get_result(database, table, taxid):
	entire = database.query("SELECT id1, id2, score FROM %s WHERE type1=%i AND type2=-22;" % (table, taxid)).getresult()
	twelve = filter_compartments(entire)
	return protein_hash(twelve)
		

def max_compartment_score(protein, know, pred, text):
	subcell = {}
	if protein in know:
		for loc in know[protein]:
			score = know[protein][loc]
			if loc not in subcell or subcell[loc] < score:
				subcell[loc] = score
	if protein in pred:
		for loc in pred[protein]:
			score = pred[protein][loc]
			if loc not in subcell or subcell[loc] < score:
				subcell[loc] = score
	#
	# TODO: How do we convert text-mining scores into 5 stars??
	#
	return subcell


def color_labels(type1, id1, subcell):
	kingdom = ""
	if type1 in animals:
		kingdom = "animals"
	elif type1 in fungi:
		kingdom = "fungi"
	elif type1 in plants:
		kingdom = "plants"
	else:
		raise Exception, "Organism/taxid %i neither animal, fungi nor plant." % type1
	
	for loc in subcell:
		print "%i\t%s\tcell_%s\t%s\t%s" % (type1, id1, kingdom, goloc2label[loc], color(subcell[loc]/5.0))


if __name__ == "__main__":
	
	# ==========================================================================
	#
	# We made a list of relevant animal, fungi and plant tax ids from the
	# YLoc predictions made from STRING v9 in connection with the sub-cellular
	# localization database.
	#
	# There (in Lars's directory: /home/red1/ljj/YLoc_STRING_v9/) he had used
	# dictionary files (all_entities.tsv and all_groups.tsv) to find all proteins
	# which came from organisms are from the animal, fingi or plant linneage.
	#
	# That gave us a list of 102 tax ids denoting organisms that are either
	# considered an animal, fungi or a plant.
	#
	# This is the command to take out all relevant tax ids:
	# cat anima.fasta fungi.fasta plants.fasta | perl -ne 'print $1."\n" if m/^>([0-9]+)\.([^ ]+) .*$/' | sort -n | uniq > taxids.tsv
	#
	# ==========================================================================

	animals = set()
	fungi   = set()
	plants  = set()
	
	for taxid in tax_animals.split():
		animals.add(int(taxid))
	
	for taxid in tax_fungi.split():
		fungi.add(int(taxid))
	
	for taxid in tax_plants.split():
		plants.add(int(taxid))

	
	knowledge   = get_connection(db_knowledge)
	predictions = get_connection(db_predictions)
	textmining  = get_connection(db_textmining)
	
	for taxid in animals:# + fungi + plants:
		
		know = get_result(knowledge, "knowledge", taxid)
		pred = get_result(predictions, "predictions", taxid)
		#text = get_result(textmining, "pairs", taxid)
		text = {} ## DEBUG!!
		
		proteins = {}
		for source in (know, pred, text):
			for id1 in source:
				if id not in proteins:
					proteins[id1] = {}
		
		for id1 in proteins:
			subcell = max_compartment_score(id1, know, pred, text)
			color_labels(taxid, id1, subcell)
			
		break
		
		
		
	
