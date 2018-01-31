import os
import re
import nltk
import zipfile
from flask import Flask, render_template, request, url_for, jsonify, make_response
from werkzeug.utils import secure_filename
from preprocess import preprocessCollection
from collectionindexer import CollectionIndexer
from searchalgorithms import booleanSearch, vectorSearch, feedbackSearch
from invindex import InvertedIndexDB

app = Flask(__name__)

UPLOAD_FOLDER = 'collections'
ALLOWED_EXTENSIONS = set(['txt', 'html', 'csv'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

""" Homepage route """
@app.route("/")
@app.route("/index")
@app.route("/home")
def homepage():
	colindex = CollectionIndexer(app.config['UPLOAD_FOLDER'])
	return render_template("index.html", collections=colindex.list)

""" Results route """
@app.route("/results")
def results():
	# Get search parameters
	query = str(request.args.get('q'))
	collection_name = str(request.args.get('collection'))

	# Get results from algorithm
	if request.args.get('type') == "boolean":
		result_filenames = booleanSearch(query, collection_name)
	else:
		k = int(request.args.get('topk'))
		result_filenames = vectorSearch(query, collection_name, top_k=k)

	# Get documents for results
	search_results = []
	index = InvertedIndexDB(collection_name)
	for filename in result_filenames:
		properties = index.getDocumentProperties(filename)
		obj = {
			"title": properties['title'],
			"url": filename,
			"excerpt": properties['desc'],
			"id": filename
		}
		search_results.append(obj)

	return render_template("results.html", results=search_results, type=request.args.get('type'))

""" Feedback search endpoint route """
@app.route("/feedbacksearch", methods=['POST'])
def feedbackresults():
	# Get search parameters
	if request.get_json()['query'] != False:
		query = request.get_json()['query']
	else:
		query = str(request.args.get('q'))
	collection_name = str(request.args.get('collection'))
	goodRes = request.get_json()['good']
	badRes = request.get_json()['bad']
	k = int(request.args.get('topk'))

	# Find results from the algorithm
	result_filenames, new_query = feedbackSearch(query, goodRes, badRes, collection_name, top_k=k)

	# Get documents for results
	result = {
		"search_results": [],
		"query": new_query
	}
	index = InvertedIndexDB(collection_name)
	for filename in result_filenames:
		properties = index.getDocumentProperties(filename)
		obj = {
			"title": properties['title'],
			"url": "/result/"+collection_name+"/"+filename,
			"excerpt": properties['desc'],
			"id": filename
		}
		result["search_results"].append(obj)

	return jsonify(result)

""" Route for a document in a local collection """
@app.route("/result/<collection>/<filename>")
def result(collection, filename):
    with open('collections/'+collection+'/'+filename, 'r') as f:
        body = f.read()
    return make_response((body, {}))

""" Upload collection page route """
@app.route("/new-collection")
def newCollection():
	return render_template("upload.html")

""" Endpoint for uploading files for a new collection """
@app.route('/uploadcollection', methods=['POST'])
def upload():
	# Validate collection name
	name = request.form['name']
	pattern = re.compile("[^A-Za-z0-9_]")
	if pattern.search(name) is not None:
		return jsonify(
			success=False,
			message="The name and the filenames can only contain letters, numbers and underscores"
		)

	# Check that there is no collection with this name
	folder = os.path.join(app.config['UPLOAD_FOLDER'], name)
	if os.path.isdir(folder):
		return jsonify(
			success=False,
			message="This collection name exists"
		)

	# Save zip
	os.mkdir( folder );
	f = request.files.getlist("files")[0]
	filename = secure_filename(f.filename)
	zip_filename = os.path.join(folder, filename)
	f.save(zip_filename)

	# Export zip_filename
	zip_file = zipfile.ZipFile(zip_filename, 'r')
	zip_file.extractall(folder)
	zip_file.close()

	# Delete zip
	os.remove(zip_filename)

	# Preprocess collection and add to index
	preprocessCollection(name, uploaded=True)
	colindex = CollectionIndexer(app.config['UPLOAD_FOLDER'])
	colindex.addCollection(name)
	return jsonify(
		success=True
	)

def prepareLocalCols():
	"""
	Preprocesses and adds local collections in the db
	"""
	# Get all folders in collection directory
	collections = os.walk(app.config['UPLOAD_FOLDER']).next()[1]

	# If the folder is not already in the collection catalogue, preprocess and add it
	colindex = CollectionIndexer(app.config['UPLOAD_FOLDER'])
	collist = colindex.list
	for c in collections:
		if c not in collist:
			preprocessCollection(c)
			colindex.addCollection(c)

if __name__ == '__main__':
	nltk.download('stopwords')
	prepareLocalCols();
	app.run(debug=False)
