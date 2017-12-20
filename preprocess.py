import os

import re
from collections import Counter

from bs4 import BeautifulSoup
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
from invindex import InvertedIndexDB

def preprocessCollection(name):
	# create a new collection
	db = InvertedIndexDB(name)

	# path to folder with html files
	directory = 'collections/{}'.format(name)

	# check every html file inside the folder
	for filename in os.listdir(directory):

		if filename.endswith(".html") or filename.endswith(".htm"):

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
			filtered_words = [word for word in words if word not in stopwords.words('english')]

			stemmer = SnowballStemmer("english", ignore_stopwords=True)
			stemmed_words = [stemmer.stem(word) for word in filtered_words]

			# count how many times each word appears inside document
			words_with_weights = Counter(stemmed_words)

			db.add(words_with_weights, filename)

if __name__ == '__main__':
	preprocessCollection("thomann")
