import os

import re
from collections import Counter

from bs4 import BeautifulSoup
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
from invindex import IndexCreator

def preprocessCollection(name, uploaded=False):
	""" Preprocesses and adds to an InvertedIndexDB all of the documents in a collections
	Parameters
	----------
	name: [String] the name of the collection
	"""
	# create a new collection
	db = IndexCreator(name)

	# path to folder with html files
	directory = 'collections/{}'.format(name)

	# check every html file inside the folder
	for filename in os.listdir(directory):

		if filename.endswith(".html") or filename.endswith(".htm"):
			if not uploaded:
				with open(directory + '/' + filename, 'r') as f:  #TODO: check if path is correct
					doc_name = f.readline().strip()
			else:
				doc_name = '/result/' + name + '/' + filename

			soup = BeautifulSoup(open(directory + '/' + filename), 'html.parser')

			# get just the text of the html
			document = soup.findAll(text=True)

			words = []
			# convert the text in list of words ignoring white spaces and special characters
			for text in document:
				list_of_words = text.split() # re.split(" ", text)  # split just by space

				for word in list_of_words:
					if (word.isalnum()):  # keep just clean text, if it contains special character ignore
						words.append(word)

			# get rid of stopwords
			words_in_low = [word.lower() for word in words]
			filtered_words = [word for word in words_in_low if word not in stopwords.words('english')]

			stemmer = SnowballStemmer("english", ignore_stopwords=True)
			stemmed_words = [stemmer.stem(word) for word in filtered_words]

			# count how many times each word appears inside document
			words_with_weights = Counter(stemmed_words)
			#words_with_weights = {x:float(words_with_weights[x])/len(stemmed_words) for x in words_with_weights}

			db.add(words_with_weights, doc_name)

			description = soup.findAll(attrs={"property":"og:description"})
			if len(description) != 0:
				description = description[0]['content']
			else:
				descirption = 'Description unavailable'
			db.setDocumentProperties(doc_name,
										soup.title.string,
										description)
	db.close()

if __name__ == '__main__':
	preprocessCollection("thomann")
