import codecs
import os
import time
from flask import Flask, render_template, request, url_for, redirect
import flask
from pymongo import MongoClient
import bcrypt
import jwt
import json
import requests
import gridfs
from auth_middlewear import token_required
app = Flask(__name__)

secret = 'aerop45gkaeh3$%Y^^YAc4'
# Secure this or something if actually deployed

client = MongoClient('localhost', 27017)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

db = client.Pokedex
pokemon = db.Pokemon
users = db.Users
grid_fs = gridfs.GridFS(db)

@app.route('/', methods=('GET', 'POST'))
def login():
    if request.method=='POST':
        try:
            username = request.form['username']
            password = request.form['password']
            

            foundUser = users.find_one({'username': username})

            passwordBytes = bytes(password, 'utf-8')
            print(foundUser)
            foundUserPassBytes = bytes(foundUser['password'], 'utf-8')
            print('hi')
            if bcrypt.checkpw(passwordBytes, foundUserPassBytes):
                print("Login Successful")
                try:
                    #experation of 8 hours
                    expiration = time.time() + 28800
                    encoded_jwt = jwt.encode({"exp":expiration, "username": username, "role": foundUser['role']}, secret, algorithm="HS256")            
                    #res = flask.make_response(redirect(url_for('home')))
                    res = flask.make_response(redirect(url_for('home'), 302))
                    res.set_cookie("token", value=encoded_jwt)
                    #res.headers['location'] = url_for('home')
                    return res
                except Exception as e:
                    return {
                        "error": "Something went wrong1",
                        "message": str(e)
                    }, 500
            return {
                "message": "Error fetching auth token!, invalid email or password",
                "data": None,
                "error": "Unauthorized"
            }, 404
        except Exception as e:
            return {
                    "message": "Something went wrong!2",
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
        print(request.files['picture'])

        image = request.files['picture']
        name = image.filename
        id = grid_fs.put(image, content_type = image.content_type, filename = name)
        query = {
            'id': id,
            'pokedexNumber': pokedexNumber,
            'pokemonName': pokemonName,
            'numberCaught': numberCaught,
        }
        status = pokemon.insert_one(query)

        return redirect(url_for('home'))


    return render_template('home.html')


@app.route('/singlePokemon')
@token_required
def singlePokemon(self):
    name = request.args.get('pokemonName', type = str)
    single_pokemon = pokemon.find_one({'pokemonName': name})
    image = grid_fs.get(single_pokemon['id'])
    base64_data = codecs.encode(image.read(), 'base64')
    image = base64_data.decode('utf-8')
    single_pokemon.update({"image":image})
    print(single_pokemon)
    return render_template('singlePokemon.html', pokemonList=single_pokemon)


@app.route('/allPokemon')
@token_required
def allPokemon():

    all_pokemon = pokemon.find()
    for single_pokemon in all_pokemon:
        image = grid_fs.get(pkmn['id'])

    return render_template('allPokemon.html', pokemonList=all_pokemon)

