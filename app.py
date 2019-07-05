from flask import Flask
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import datetime
import json

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'restdb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/restdb'

mongo = PyMongo(app)

mongo.db.stars.drop()
mongo.db.comments.drop()
mongo.db.restaurants.drop()


@app.route('/restaurants', methods=['GET'])
def get_all_restaurants():
    restaurant = mongo.db.restaurants
    output = []
    for r in restaurant.find():
        r['_id'] = str(r['_id'])
        output.append(r)
    return jsonify(output)


@app.route('/restaurants/<string:id>', methods=['GET'])
def get_restaurant(id):
    restaurant = mongo.db.restaurants
    r = restaurant.find_one({'_id': ObjectId(id)})
    if r:
        r['_id'] = str(r['_id'])
        output = r
    else:
        output = "No such restaurant"
    return jsonify(output)


@app.route('/restaurants/<string:id>/comments', methods=['GET'])
def get_comments(id):
    restaurant = mongo.db.restaurants
    r = restaurant.find_one({'_id': ObjectId(id)})
    output = []
    if r:
        for c_id in r['comments']:
            c = get_comment(c_id).json
            output.append(c)
    else:
        output = "No such restaurant"
    return jsonify(output)


def get_comment(id):
    comment = mongo.db.comments
    c = comment.find_one({'_id': ObjectId(id)})
    if c:
        c['_id'] = str(c['_id'])
        output = c
    else:
        output = "No such comment"
    return jsonify(output)


@app.route('/restaurants', methods=['POST'])
def add_restaurant():
    restaurant = mongo.db.restaurants
    name = request.json['name']
    logo = "/img/"
    openingTime = request.json['openingTime']
    closingTime = request.json['closingTime']
    averageRate = request.json['averageRate']
    address = request.json['address']
    categories = request.json['categories']
    foods = request.json['foods']
    comments = request.json['comments']
    restaurant_id = restaurant.insert(
        {'name': name, 'logo': logo, 'openingTime': openingTime, 'closingTime': closingTime, 'averageRate': averageRate,
         'address': address, 'categories': categories, 'foods': foods, 'comments': comments})
    new_restaurant = restaurant.find_one({'_id': restaurant_id})
    new_restaurant['_id'] = str(new_restaurant['_id'])
    return json.dumps(new_restaurant)


@app.route('/restaurants/<string:id>/comments', methods=['POST'])
def add_comment(id):
    comment = mongo.db.comments
    author = request.json['author']
    quality = request.json['quality']
    packaging = request.json['packaging']
    deliveryTime = request.json['deliveryTime']
    text = request.json['text']
    created_at = datetime.datetime.utcnow()
    comment_id = comment.insert(
        {'author': author, 'quality': quality, 'packaging': packaging, 'deliveryTime': deliveryTime, 'text': text,
         'created_at': created_at})
    restaurant = mongo.db.restaurants
    r = restaurant.find_one({'_id': ObjectId(id)})
    new_rate = ((quality + packaging + deliveryTime) / 3 + len(r['comments']) * r['averageRate']) / (
            len(r['comments']) + 1)
    restaurant.update({'_id': ObjectId(id)}, {'$set': {'averageRate': new_rate}})
    restaurant.update({'_id': ObjectId(id)}, {'$push': {'comments': str(comment_id)}})
    new_comment = comment.find_one({'_id': comment_id})
    new_comment['_id'] = str(new_comment['_id'])
    new_comment['created_at'] = str(new_comment['created_at'])
    return json.dumps(new_comment)


if __name__ == '__main__':
    app.run(debug=True)
