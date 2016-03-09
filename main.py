from flask import Flask, render_template, request, jsonify
import json
import copy

from face_detector import detector

app = Flask(__name__)

@app.route('/api')
def api():
	url = request.args.get('url')
	face_type = request.args.get('face_type')
	detector.config_proxy('proxy.json')
	img = detector.get_image(url)
	region = detector.detect_face(face_type, img['image'])
	if region is None:
		return jsonify(error="failed")
	return jsonify(url=url, filename=img['filename'], region=region)


@app.route("/")
def index():
	return render_template("index.html")


if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True)
