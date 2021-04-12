import os
from flask import Flask, request, jsonify, make_response, url_for, json
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)

def search(searchObj):
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	json_data_url = os.path.join(SITE_ROOT, "data", "products.json")
	data = json.load(open(json_data_url))
	search_data = list()
	for product in data:
		if searchObj['product_name'] != ' ' and searchObj['product_name'] == product.title:
			search_data.append(product)

	return search_data
