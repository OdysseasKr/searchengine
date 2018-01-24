from invindex import InvertedIndexDB
import tt
import numpy as np
import operator
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
from collections import Counter

def booleanSearch(exp_string, collection_name):
	""" Searches for documents that match the given boolean expression
	Parameters
	----------
	exp_string: String representing the boolean expression. It should contain
				words and the operators and, or, not

	Returns: A set of document names that match the given expression
	"""
	results = set()
	index = InvertedIndexDB(collection_name)

	# Convert expression to DNF format if needed
	expression = tt.BooleanExpression(exp_string)
	while not expression.is_dnf:
		expression = tt.distribute_ands(expression)

	# Get the result set for every AND clause
	stemmer = SnowballStemmer("english", ignore_stopwords=True)
	for clause in expression.iter_dnf_clauses():
		clause_results = index.documents

		# Find the set of documents for every word
		negation = False
		for tok in clause.tokens:
			if tok == "AND":
				continue
			if tok == "NOT":
				negation = True;
				continue

			tok = tok.lower()
			tok = stemmer.stem(tok)
			docset = getDocumentSetByWord(index, tok)
			if negation:
				clause_results = clause_results - docset
				negation = False
			else:
				clause_results = clause_results & docset

		# And the results of this clause to the final results
		results = results | clause_results

	return results



def vectorSearch(input_doc, collection_name, rank_algo='alt_dot', limit=0., top_k=None):
	"""
	input_doc: the query
	collection_name: which collection to search
	rank_algo: the algorithm to calculate the similarity
		'alt_dot': alternative dot
		'dot': simple dot (supports feedback)
	limit: show results that have a rank higher from the limit
	top_k: how many of the top results to return
	Return: Sorted list with documents.
	"""

	index = InvertedIndexDB(collection_name)  # get a collection
	documents = index.documents  # get all the documents of the collection
	N = len(index.documents)  # the number of all the documents

	docs_with_ranks = {}  # Dictionary with key: doc_name and value: rank

	input_doc = preprocess_query(input_doc)

	for t in input_doc:  # for every word of the input documents

		docs_with_word = index.getDocumentsByWord(t)  # get all the docs that contain this word
		nt = len(docs_with_word)  # the number of docs containing the word

		#TODO: N = 8 but nt = 120...
		# nt must always be less or equal with N

		if nt != 0:  # if no document contain the word, continue
			IDF_t = np.log(1 + N/nt)
			for doc in docs_with_word:  # for every document

				doc_name = doc[0]  # get the name of the document
				f_td = doc[1]  # get the frequency of the word for that document
				TF_td = 1 + np.log(f_td)
				w_td = TF_td * IDF_t

				if (rank_algo=='dot'):
					t_num = input_doc.count(t)  # count how many times t shows in query
					f_tq = t_num / len(input_doc)  # get the frequency of the word in the query
					TF_tq = 1 + np.log(f_tq)
					w_tq = TF_tq * IDF_t
					rank = w_td * w_tq
				# elif (rank_algo=='alt_dot'):
				else:
					rank = w_td

				if doc_name in docs_with_ranks:
					docs_with_ranks[doc_name] += rank
				else:
					docs_with_ranks[doc_name] = rank

	# sort the documents by frequency
	sorted_docs = sorted(docs_with_ranks.items(), key=operator.itemgetter(1), reverse=True)

	results = sorted_docs[:top_k]  # get just the top_k docs

	if len(results) == 0:
		return []
	return list(zip(*results)[0])


def feedbackSearch(input_doc, R, NR, collection_name, limit=0., top_k=None):
	"""
	input_doc: the query vector
	collection_name: which collection to search
	limit: show results that have a rank higher from the limit
	top_k: how many of the top results to return
	Return: Sorted list with documents.
	"""

	index = InvertedIndexDB(collection_name)  # get a collection
	documents = index.documents  # get all the documents of the collection
	N = len(index.documents)  # the number of all the documents

	input_doc = preprocess_query(input_doc)
	q0 = Counter(input_doc)
	qm = getNewQuery(q0, R, NR, index)

	docs_with_ranks = {}
	for t in qm.keys():  # for every word of the input documents

		docs_with_word = index.getDocumentsByWord(t)  # get all the docs that contain this word
		nt = len(docs_with_word)  # the number of docs containing the word

		if nt != 0:  # if no document contain the word, continue
			IDF_t = np.log(1 + N/nt)
			for doc in docs_with_word:  # for every document

				doc_name = doc[0]  # get the name of the document
				f_td = doc[1]  # get the frequency of the word for that document
				TF_td = 1 + np.log(f_td)
				w_td = TF_td * IDF_t

				t_num = qm[t]  # count how many times t shows in query
				f_tq = t_num / len(input_doc)  # get the frequency of the word in the query
				TF_tq = 1 + np.log(f_tq)
				w_tq = TF_tq * IDF_t
				rank = w_td * w_tq

				if doc_name in docs_with_ranks:
					docs_with_ranks[doc_name] += rank
				else:
					docs_with_ranks[doc_name] = rank

	# sort the documents by frequency
	sorted_docs = sorted(docs_with_ranks.items(), key=operator.itemgetter(1), reverse=True)

	results = sorted_docs[:top_k]  # get just the top_k docs

	if len(results) == 0:
		return []
	return list(zip(*results)[0])

def getNewQuery(q0, R, NR, index):
	a = 1; b = 1; c = 1
	qm = {}
	for w in q0:
		qm[w] = a * q0[w]

	for doc in R:
		words = index.getWordsByDocument(doc)
		for w in words:
			if w not in qm:
				qm[w] = 0
			qm[w] += b * words[w] / float(len(R))
	for doc in NR:
		print(doc)
		words = index.getWordsByDocument(doc)
		print(words)
		for w in words:
			if w not in qm:
				qm[w] = 0
			qm[w] -= c * words[w] / float(len(NR))
	return {x : y for x,y in qm.items() if y!=0}

def preprocess_query(query):
	words_in_low = [word.lower() for word in query.split()]
	filtered_words = [word for word in words_in_low if word not in stopwords.words('english')]

	stemmer = SnowballStemmer("english", ignore_stopwords=True)
	stemmed_words = [stemmer.stem(word) for word in filtered_words]

	return stemmed_words


def getDocumentSetByWord(index, word):
	docs = index.getDocumentsByWord(word)
	if len(docs) == 0:
		return set()
	return set(zip(*docs)[0])
