import re
import string
import pg

#database = pg.connect(host=self.conn_info[0], port=int(self.conn_info[1]), user=self.conn_info[2], passwd='', dbname=self.conn_info[3])
#XNodeSomeType(str(visualization.SVG(database, 'cell_%', 9606, 'ENSP00000269305')))
#XNodeSomeType(str(visualization.SVG(database, 'overview_%', 9606, 'ENSP00000269305')))
#database.close()

class SVG:
	__svg = ""
	
	def __init__(self, database, qfigure, qtype, qid):
		self.fetch_svg(database, self.find_svg(database, qfigure, qtype, qid))
		self.apply_colors(self.fetch_colors(database, qfigure, qtype, qid))
	
	def __str__(self):
		return self.__svg
	
	""" Retrieves the figure from the database that was defined as an argument.
	"""	
	def fetch_svg(self, database, qfigure):
		q = "SELECT svg FROM figures WHERE figure = '%s';" % pg.escape_string(qfigure)
		r  = database.query(q).getresult()
		if len(r) == 0:
			raise Exception, "Error: No figure called %s has been returned" % qfigure
		self.__svg = r[0][0]
		return
	
	def find_svg(self, database, qfigure, qtype, qid):
		q = "SELECT DISTINCT figure FROM colors WHERE type = %d AND id = '%s' AND figure LIKE '%s';" % (qtype, pg.escape_string(qid), pg.escape_string(qfigure))
		r = database.query(q).getresult()
		if len(r) == 0:
			raise Exception, "No figures matched query"
		elif len(r) > 1:
			raise Exception, "More than one figure matches query"
		return r[0][0]
	
	def apply_colors(self, label_color_map):
		buf = []
		for line in self.__svg.split("\n"):
			m = re.search('<.* title="([^"]+)".*>', line)
			if m:
				label = m.group(1)
				if label in label_color_map:
						line = re.sub('(?<=fill:|ill=")#.{6}', '%s' % label_color_map[label], line)
			buf.append(line)
		
		self.__svg = string.join(buf,"\n")
		return
	
	def fetch_colors(self, database, qfigure, qtype, qid):
		label_color_map = {}
		q = "SELECT label, color FROM colors WHERE type = %d AND id = '%s' AND figure LIKE '%s';" % (qtype, pg.escape_string(qid), pg.escape_string(qfigure))
		r = database.query(q).getresult()
		for record in r:
			label_color_map[record[0]] = record[1]
		return label_color_map
