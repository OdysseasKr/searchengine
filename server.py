import os
import re
from flask import Flask, render_template, request, url_for, jsonify
from werkzeug.utils import secure_filename
from fakedata import search_results
from preprocess import preprocessCollection
from collectionindexer import CollectionIndexer

app = Flask(__name__)

UPLOAD_FOLDER = 'collections'
ALLOWED_EXTENSIONS = set(['txt', 'html', 'csv'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
	return '.' in filename and \
		   filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
@app.route("/index")
@app.route("/home")
def homepage():
	colindex = CollectionIndexer(app.config['UPLOAD_FOLDER'])
	return render_template("index.html", collections=colindex.list)

@app.route("/results")
def results():
	query = request.args.get('q')
	return render_template("results.html", results=search_results)

@app.route("/new-collection")
def newCollection():
	return render_template("upload.html")

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

	preprocessCollection(name)
	colindex = CollectionIndexer(app.config['UPLOAD_FOLDER'])
	colindex.addCollection(name)
	return jsonify(
		success=True
	)

if __name__ == '__main__':
	collections = os.walk(app.config['UPLOAD_FOLDER']).next()[1]
	for c in collections:
		print(c)
		preprocessCollection(c)
	colindex = CollectionIndexer(app.config['UPLOAD_FOLDER'])
	colindex.addCurrentFolders()
	app.run(debug=True)
