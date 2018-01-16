import os
import re
import nltk
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
	print(result_filenames)

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
	query = str(request.args.get('q'))
	collection_name = str(request.args.get('collection'))
	goodRes = request.get_json()['good']
	badRes = request.get_json()['bad']
	k = int(request.args.get('topk'))

	# Find results from the algorithm
	result_filenames = feedbackSearch(query, goodRes, badRes, collection_name, top_k=k)
	print(result_filenames)

	# Get documents for results
	search_results = []
	index = InvertedIndexDB(collection_name)
	for filename in result_filenames:
		properties = index.getDocumentProperties(filename)
		obj = {
			"title": properties['title'],
			"url": "/result/"+collection_name+"/"+filename,
			"excerpt": properties['desc'],
			"id": filename
		}
		search_results.append(obj)

	return jsonify(search_results)

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
	name = request.form['name']
	pattern = re.compile("[^A-Za-z0-9_]")
	if pattern.search(name) is not None:
		return jsonify(
			success=False,
			message="The name and the filenames can only contain letters, numbers and underscores"
		)

	folder = os.path.join(app.config['UPLOAD_FOLDER'], name)
	if os.path.isdir(folder):
		return jsonify(
			success=False,
			message="This collection name exists"
		)

	os.mkdir( folder );
	for f in request.files.getlist("files"):
		filename = secure_filename(f.filename)
		if pattern.search(name) is not None:
			continue;
		f.save(os.path.join(folder, filename))

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
	collections = os.walk(app.config['UPLOAD_FOLDER']).next()[1]
	for c in collections:
		preprocessCollection(c)
	colindex = CollectionIndexer(app.config['UPLOAD_FOLDER'])
	colindex.addCurrentFolders()

if __name__ == '__main__':
	nltk.download('stopwords')
	#prepareLocalCols();
	app.run(debug=False)
