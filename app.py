import time
from flask import Flask, render_template, request, url_for, redirect
import flask
from pymongo import MongoClient
import bcrypt
import jwt
import requests
import json
from auth_middlewear import token_required
app = Flask(__name__)

secret = 'aerop45gkaeh3$%Y^^YAc4'
# Secure this or something if actually deployed

client = MongoClient('localhost', 27017)

db = client.Pokedex
pokemon = db.Pokemon
users = db.Users

@app.route('/', methods=('GET', 'POST'))
def login():
    if request.method=='POST':
        try:
            username = request.form['username']
            password = request.form['password']
            

            foundUser = users.find_one({'username': username})

            passwordBytes = bytes(password, 'utf-8')
            foundUserPassBytes = bytes(foundUser['password'], 'utf-8')
            if bcrypt.checkpw(passwordBytes, foundUserPassBytes):
                print("Login Successful")
                try:
                    #experation of 8 hours
                    expiration = time.time() + 28800
                    encoded_jwt = jwt.encode({"exp":expiration, "username": username, "role": foundUser['role']}, secret, algorithm="HS256")            
                    res = flask.make_response(redirect(url_for('home')))
                    res.set_cookie("token", value=encoded_jwt)
                    #res.headers['location'] = url_for('home')
                    return res, 200
                except Exception as e:
                    return {
                        "error": "Something went wrong",
                        "message": str(e)
                    }, 500
            return {
                "message": "Error fetching auth token!, invalid email or password",
                "data": None,
                "error": "Unauthorized"
            }, 404
        except Exception as e:
            return {
                    "message": "Something went wrong!",
                    "error": str(e),
                    "data": None
            }, 500
        # return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/home', methods=('GET', 'POST'))
@token_required
def home(current_user):
    if request.method=='POST':
        pokedexNumber = int(request.form['pokedexNumber'])
        pokemonName = request.form['pokemonName']
        numberCaught = int(request.form['numberCaught'])
        
        pokemon.insert_one({'pokedexNumber': pokedexNumber, 'pokemonName': pokemonName, 'numberCaught': numberCaught})
        return redirect(url_for('home'))

    all_pokemon = pokemon.find()
    return render_template('home.html', pokemon=all_pokemon)


@app.route('/about')
def about():
    return '<h3>This is a Flask web application.</h3>'

@app.route('/downloadImages', methods=['GET'])
def download():
    req = requests.get('https://pokeapi.co/api/v2/pokemon-form/132')
    data = json.loads(req.content)
    return render_template('downloadImagesTest.html', data=data)
# data=data['all']
# data=data['property tag we specifically we want from the data so front_default']
# '<h3>This is a Flask web application.</h3>'