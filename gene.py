#!/usr/bin/env python3


import os
import sys
import json
import xml.etree.ElementTree



import entrezpy.conduit
import entrezpy.base.result
import entrezpy.base.analyzer
from bs4 import BeautifulSoup

class GeneRecord:
	"""Simple data class to store individual Pubmed records. Individual authors will
	be stored as dict('lname':last_name, 'fname': first_name) in authors.
	Citations as string elements in the list citations. """

	def __init__(self):
		self.geneId = None
		self.seqId = None
		self.seqStart = None
		self.seqEnd = None
		self.sequence = None
		self.accver = None
		self.phenotype = None
		self.loc = None





class GeneResult(entrezpy.base.result.EutilsResult):
	"""Derive class entrezpy.base.result.EutilsResult to store Pubmed queries.
	Individual Pubmed records are implemented in :class:`PubmedRecord` and
	stored in :ivar:`pubmed_records`.

	:param response: inspected response from :class:`PubmedAnalyzer`
	:param request: the request for the current response
	:ivar dict pubmed_records: storing PubmedRecord instances"""

	def __init__(self, response, request):
		super().__init__(request.eutil, request.query_id, request.db)
		self.gene_records = {}

	def size(self):
		"""Implement virtual method :meth:`entrezpy.base.result.EutilsResult.size`
		returning the number of stored data records."""
		return len(self.gene_records)

	def isEmpty(self):
		"""Implement virtual method :meth:`entrezpy.base.result.EutilsResult.isEmpty`
		to query if any records have been stored at all."""
		if not self.gene_records:
			return True
		return False

	def get_link_parameter(self, reqnum=0):
		"""Implement virtual method :meth:`entrezpy.base.result.EutilsResult.get_link_parameter`.
		Fetching a pubmed record has no intrinsic elink capabilities and therefore
		should inform users about this."""
		print("{} has no elink capability".format(self))
		return {}

	def dump(self):
		"""Implement virtual method :meth:`entrezpy.base.result.EutilsResult.dump`.

		:return: instance attributes
		:rtype: dict
		"""
		return {self:{'dump':{'gene_records':[x for x in self.gene_records],
									'query_id': self.query_id, 'db':self.db,
									'eutil':self.function}}}

	def add_gene_record(self, gene_record):
		"""The only non-virtual and therefore PubmedResult-specific method to handle
		adding new data records"""
		self.gene_records[gene_record.geneId] = gene_record



class GeneAnalyzer(entrezpy.base.analyzer.EutilsAnalyzer):
	"""Derived class of :class:`entrezpy.base.analyzer.EutilsAnalyzer` to analyze and
	parse PubMed responses and requests."""

	def __init__(self):
		super().__init__()

	def init_result(self, response, request):
		"""Implemented virtual method :meth:`entrezpy.base.analyzer.init_result`.
		This method initiate a result instance when analyzing the first response"""
		if self.result is None:
			self.result = GeneResult(response, request)

	def analyze_error(self, response, request):
		"""Implement virtual method :meth:`entrezpy.base.analyzer.analyze_error`. Since
		we expect XML errors, just print the error to STDOUT for
		logging/debugging."""
		print(json.dumps({__name__:{'Response': {'dump' : request.dump(),
													'error' : response.getvalue()}}}))

	def analyze_result(self, response, request):
		"""Implement virtual method :meth:`entrezpy.base.analyzer.analyze_result`.
		Parse PubMed  XML line by line to extract authors and citations.
		xml.etree.ElementTree.iterparse
		(https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.iterparse)
		reads the XML file incrementally. Each  <PubmedArticle> is cleared after processing.

		..note::  Adjust this method to include more/different tags to extract.
					Remember to adjust :class:`.PubmedRecord` as well."""
		self.init_result(response, request)
		
		soup = BeautifulSoup(response, 'xml')
		geneRec = GeneRecord()
		geneRec.geneId = int(soup.find('Gene-track_geneid').string)
		if t := soup.find_all('Gene-ref_desc', limit=1):
			geneRec.phenotype = t[0].text
		if t := soup.find_all('Seq-id_gi', limit=1):
			geneRec.seqId = t[0].text
		if t := soup.find_all('Seq-interval_from', limit=1):
			geneRec.seqStart = t[0].text
		if t := soup.find_all('Seq-interval_to', limit=1):
			geneRec.seqEnd = t[0].text
		if t := soup.find_all('Gene-commentary_accession', limit=1):
			geneRec.accver = t[0].text
		if t:= soup.find_all('Gene-ref_maploc', limit=1):
			geneRec.loc = t[0].text
		
		self.result.add_gene_record(geneRec)


class SeqRecord:
	
	def __init__(self):
		self.accver = None
		self.sid = None
		self.taxid = None
		self.orgname = None
		self.defline = None
		self.seqLen = None
		self.sequence = None
	

class SeqResult(entrezpy.base.result.EutilsResult):
	"""Derive class entrezpy.base.result.EutilsResult to store Pubmed queries.
	Individual Pubmed records are implemented in :class:`PubmedRecord` and
	stored in :ivar:`pubmed_records`.

	:param response: inspected response from :class:`PubmedAnalyzer`
	:param request: the request for the current response
	:ivar dict pubmed_records: storing PubmedRecord instances"""

	def __init__(self, response, request):
		super().__init__(request.eutil, request.query_id, request.db)
		self.seq_records = {}

	def size(self):
		"""Implement virtual method :meth:`entrezpy.base.result.EutilsResult.size`
		returning the number of stored data records."""
		return len(self.seq_records)

	def isEmpty(self):
		"""Implement virtual method :meth:`entrezpy.base.result.EutilsResult.isEmpty`
		to query if any records have been stored at all."""
		if not self.seq_records:
			return True
		return False

	def get_link_parameter(self, reqnum=0):
		"""Implement virtual method :meth:`entrezpy.base.result.EutilsResult.get_link_parameter`.
		Fetching a pubmed record has no intrinsic elink capabilities and therefore
		should inform users about this."""
		print("{} has no elink capability".format(self))
		return {}

	def dump(self):
		"""Implement virtual method :meth:`entrezpy.base.result.EutilsResult.dump`.

		:return: instance attributes
		:rtype: dict
		"""
		return {}
		return {self:{'dump':{'seq_records':[x for x in self.seq_records],
									'query_id': self.query_id, 'db':self.db,
									'eutil':self.function}}}
	def add_seq_record(self, seq_record):
		"""The only non-virtual and therefore PubmedResult-specific method to handle
		adding new data records"""
		self.seq_records[seq_record.sid] = seq_record

class SeqAnalyzer(entrezpy.base.analyzer.EutilsAnalyzer):
	

	def __init__(self):
		super().__init__()

	def init_result(self, response, request):
		
		if self.result is None:
			self.result = SeqResult(response, request)

	def analyze_error(self, response, request):
		
		print(json.dumps({__name__:{'Response': {'dump' : request.dump(),
													'error' : response.getvalue()}}}))

	def analyze_result(self, response, request):
		
		self.init_result(response, request)
		
		soup = BeautifulSoup(response, 'xml')
		seqRec = SeqRecord()
		if t := soup.find('TSeq_accver'):
			seqRec.accver = t.text 
		if t := soup.find('TSeq_sid'):
			seqRec.sid = t.text
		if t := soup.find('TSeq_taxid'):
			seqRec.taxid = t.text
		if t := soup.find('TSeq_orgname'):
			seqRec.orgname = t.text
		if t := soup.find('TSeq_length'):
			seqRec.seqLen = int(t.text)
		if t := soup.find('TSeq_defline'):
			seqRec.defline = t.text
		if t := soup.find('TSeq_sequence'):
			seqRec.sequence = t.text

		self.result.add_seq_record(seqRec)

email = 'zhuzhuoerbilly@gmail.com'
api = '15035947eb5eba07c081a0c90fc48acdb609'
c = entrezpy.conduit.Conduit(email, api, threads=5)

geneList = ['APOE',
			'APP',
			'PSEN1']
geneSearch = [{'db':'gene', 'term': x + '[sym] AND human[ORGN]'} for x in geneList]

seqQurey = []
for query in geneSearch:
	fetchGene = c.new_pipeline()
	sid = fetchGene.add_search(query)
	lid = fetchGene.add_link({'cmd':'neighbor_history', 'db':'Nucleotide'}, dependency=sid)
	lid = fetchGene.add_search({'cmd':'neighbor_history'}, dependency=lid)
	# fetchProtein.add_fetch({'retmax': 1, 'retmode':'xml','rettype':'fasta'}, dependency=lid, analyzer=proteinAnalyzer())
	fid = fetchGene.add_fetch({'retmax': 1, 'retmode':'xml','rettype':'fasta'}, dependency=lid, analyzer=SeqAnalyzer())
	
	fetchG = c.new_pipeline()
	sid2 = fetchG.add_search(query)
	fid2 = fetchG.add_fetch({'retmax': 1, 'retmode':'xml','rettype':'fasta'}, dependency=sid2, analyzer=GeneAnalyzer())
	
	g_res = c.run(fetchG).get_result()

	for i in g_res.gene_records:
		print('gene seqId: {}'.format(g_res.gene_records[i].seqId))
		print('gene phenotype: {}'.format(g_res.gene_records[i].phenotype))
		print('gene loc: {}'.format(g_res.gene_records[i].loc))
	
	res = c.run(fetchGene).get_result()

	
	for i in res.seq_records:
		print('seq accver:{}'.format(res.seq_records[i].accver))
		print('seq sid:{}'.format(res.seq_records[i].sid))
		print('seq taxid:{}'.format(res.seq_records[i].taxid))
		print('seq orgname:{}'.format(res.seq_records[i].orgname))
		print('seq defline:{}'.format(res.seq_records[i].defline))
		print('seq seqLen:{}'.format(res.seq_records[i].seqLen))
		print('seq sequence:{}'.format(res.seq_records[i].sequence[:30]))
		print("##############")
