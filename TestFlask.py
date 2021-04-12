import os
import datetime
from flask import Flask, request, jsonify, make_response, url_for, json
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
import datetime
from markupsafe import escape
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY']='Tsh1Sha256Tls2Sha512'

def token_required(f):
	@wraps(f)
	def decorator(*args, **kwargs):
		token = None
		if 'Authorization' in request.headers:
			token = request.headers['Authorization']
			print(token)
		if not token:
			return jsonify({'success':0, 'message': 'Token missing'})
		try:
			data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
			current_user = data["name"]
		except:
			return jsonify({'success':0, 'message': 'Invalid token'})
		return f(*args, **kwargs)
	return decorator

@app.route('/api/authenticate', methods=["POST"])
@cross_origin()
def authenticate():
	login_data = request.get_json()
	# print(generate_password_hash(login_data['password'], method='sha256'))
	if not login_data or not login_data["username"] or not login_data["password"]:
		return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})
	user = filterUserByUsername(login_data)
	if user:
		if check_password_hash(user["Password"], login_data["password"]):
			token = jwt.encode({'name': user["Name"], 'username': user["Username"], 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm="HS256")
			return jsonify({'token' : token, 'success':1 ,'message': 'Login successfully'})
	# return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})
	return jsonify({'success':0 ,'message': 'Invalid login details'})

@app.route('/api/products', methods=["POST"])
@cross_origin()
@token_required
def get_products():
	request_data = request.get_json()
	#print(request_data['product_name'])
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	json_data_url = os.path.join(SITE_ROOT, "data", "products.json")
	data = json.load(open(json_data_url))
	data = process_data(data)
	if request_data['SearchQuery']:
		data = search(request_data['SearchQuery'],data)
	json_meta_url = os.path.join(SITE_ROOT, "data", "meta.json")
	meta = json.load(open(json_meta_url))
	return jsonify({'success':1 ,'message': 'Data fetch successfully', 'data': data, 'meta': meta})


def search(searchObj,data):
	product_name = searchObj['product_name']
	product_price = searchObj['product_price']
	search_data = list()
	for product in data:
		conditions = []
		if product_name != "":
			condition = product_name in product['title']
			conditions.append(condition)
		if product_price != '':
			condition = product['price'] <= float(product_price)
			conditions.append(condition)
		print(conditions)
		if all(conditions):
			search_data.append(product)
	return search_data

def process_data(data):
	today_date = datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d')
	for product in data:
		product["display_date"] = datetime.datetime.strptime(product['expiry'],'%Y-%m-%d')
		if today_date > product["display_date"]:
			product["expire"] = "Expired"
		else:
			product["expire"] = "Not Expired"
		product["display_date"] = product["display_date"].strftime("%d/%m/%Y")
		product["display_price"] = str(product["price"]) + " AED"
		product["discount"] = str(product["discount"]) + " AED"
	return data

def filterUserByUsername(login_data):
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	json_data_url = os.path.join(SITE_ROOT, "data", "users.json")
	users = json.load(open(json_data_url))
	for user in users:
		if user["Username"] == login_data["username"]:
			return user
	return False
