from flask import Flask, redirect
from flask import jsonify
from flask import request
from flask_pymongo import PyMongo
import datetime
import json

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'restdb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/restdb'

mongo = PyMongo(app)

mongo.db.stars.drop()
mongo.db.comments.drop()
mongo.db.restaurants.drop()


@app.route('/star', methods=['GET'])
def get_all_stars():
    star = mongo.db.stars
    output = []
    for s in star.find():
        output.append({'name': s['name'], 'distance': s['distance']})
    return jsonify({'result': output})


@app.route('/restaurants', methods=['GET'])
def get_all_restaurants():
    restaurant = mongo.db.restaurants
    output = []
    for s in restaurant.find():
        s['_id'] = str(s['_id'])
        output.append(s)
    return jsonify(output)


@app.route('/star/<string:name>', methods=['GET'])
def get_one_star(name):
    star = mongo.db.stars
    s = star.find_one({'name': name})
    if s:
        output = {'name': s['name'], 'distance': s['distance']}
    else:
        output = "No such name"
    return jsonify({'result': output})


@app.route('/restaurants/<string:id>', methods=['GET'])
def get_restaurant(id):
    r = mongo.db.restaurants.find_one({'id': id})
    if r:
        output = {'id': r['id'], 'distance': r['distance']}
    else:
        output = "No such name"
    return jsonify({'result': output})


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


@app.route('/star', methods=['POST'])
def add_star():
    mongo.db.stars.insert(request.json)
    return redirect('star/' + request.json['name'])


@app.route('/comment', methods=['POST'])
def add_comment():
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
    new_comment = comment.find_one({'_id': comment_id})
    new_comment['_id'] = str(new_comment['_id'])
    new_comment['created_at'] = str(new_comment['created_at'])
    return json.dumps(new_comment)


if __name__ == '__main__':
    app.run(debug=True)
