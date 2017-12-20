from invindex import InvertedIndexDB
import tt

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
			docset = getDocumentSetByWord(index, tok)
			if negation:
				clause_results = clause_results - docset
				negation = False
			else:
				clause_results = clause_results & docset

		# And the results of this clause to the final results
		results = results | clause_results

	return results

def getDocumentSetByWord(index, word):
	docs = index.getDocumentsByWord(word)
	if len(docs) == 0:
		return set()
	return set(zip(*docs)[0])
