import os
from flask import Flask, render_template, request, url_for, jsonify
from werkzeug.utils import secure_filename
from fakedata import search_results
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
	collections = os.listdir(app.config['UPLOAD_FOLDER'])
	return render_template("index.html", collections=collections)

@app.route("/results")
def results():
	query = request.args.get('q')
	return render_template("results.html", results=search_results)

@app.route("/new-collection")
def newCollection():
	return render_template("upload.html")

@app.route('/uploadcollection', methods=['POST'])
def upload():
	folder = os.path.join(app.config['UPLOAD_FOLDER'], request.form['name'])
	if os.path.isdir(folder):
		return jsonify(
			success=False,
			message="This collection name exists"
		)

	os.mkdir( folder );
	for f in request.files.getlist("files"):
		filename = secure_filename(f.filename)
		f.save(os.path.join(folder, filename))
	return jsonify(
		success=True
	)

if __name__ == '__main__':
	app.run(debug=True)
