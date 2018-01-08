from invindex import InvertedIndexDB
import tt
import numpy as np
import operator

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



def vectorSearch(input_doc, collection_name, limit=0., top_k=None):
	"""
	Return: Dictionary set with documents and their similarity ranking.
	"""

	index = InvertedIndexDB(collection_name)  # get a collection
	documents = index.documents  # get all the documents of the collection

	N = len(index.documents)  # the number of all the documents

	docs_with_ranks = {}  # Dictionary with key: doc_name and value: rank

	for t in input_doc:  # for every word of the input documents

		docs_with_word = index.getDocumentsByWord(t)  # get all the docs that contain this word

		nt = len(docs_with_word)  # the number of docs containing the word

		IDF_t = np.log(1 + N/nt)

		for doc in docs_with_word:  # for every document

			doc_name = doc[0]  # get the name of the document
			f_td = doc[1]  # get the frequency of the word for that document

			TF_td = 1 + np.log(f_td)
			if doc_name in docs_with_ranks:
				docs_with_ranks[doc_name] += TF_td * IDF_t
			else:
				docs_with_ranks[doc_name] = 0

	# sort the documents by frequency
	sorted_docs = sorted(docs_with_ranks.items(), key=operator.itemgetter(1), reverse=True)

	results = sorted_docs[:top_k]  # get just the top_k docs

	return results


def getDocumentSetByWord(index, word):
	docs = index.getDocumentsByWord(word)
	if len(docs) == 0:
		return set()
	return set(zip(*docs)[0])
