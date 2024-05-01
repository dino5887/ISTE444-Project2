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
import logging
from datetime import datetime, timezone
app = Flask(__name__)

secret = 'aerop45gkaeh3$%Y^^YAc4'
# Secure this or something if actually deployed

app.logger.setLevel(logging.INFO)  # Set log level to INFO
handler = logging.FileHandler('app.log')  # Log to a file
app.logger.addHandler(handler)
formatter = logging.Formatter("%(asctime)s;%(levelname)s;%(message)s","%Y-%m-%d %H:%M:%ST%z")

# def utcformat(dt, timespecification='seconds'):
#     """convert datetime to string in UTC format (YYYY-mm-ddTHH:MM:SSZ)"""
#     iso_str = dt.astimezone(timezone.utc).isoformat(' ', timespecification)
#     return iso_str.replace('+00:00', 'TZ')

# def fromutcformat(utc_str, tz=None):
#     iso_str = utc_str.replace('Z', '+00:00')
#     return datetime.fromisoformat(iso_str).astimezone(tz)

# now = datetime.now(tz=timezone.utc)
# print(fromutcformat(utcformat(now)))

client = MongoClient('localhost', 27017)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

db = client.Pokedex
pokemon = db.Pokemon
users = db.Users
grid_fs = gridfs.GridFS(db)

@app.route('/', methods=('GET', 'POST'))
def login():
    app.logger.info('Start of the login route.')
    if request.method=='POST':
        try:
            username = request.form['username']
            password = request.form['password']
            

            foundUser = users.find_one({'username': username})

            passwordBytes = bytes(password, 'utf-8')
            foundUserPassBytes = bytes(foundUser['password'], 'utf-8')
            if bcrypt.checkpw(passwordBytes, foundUserPassBytes):
                print("Login Successful")
                app.logger.info('Login Successful.')
                try:
                    #expiration of 8 hours
                    expiration = time.time() + 28800
                    encoded_jwt = jwt.encode({"exp":expiration, "username": username, "role": foundUser['role']}, secret, algorithm="HS256")
                    res = flask.make_response(redirect(url_for('home'), 302))
                    res.set_cookie("token", value=encoded_jwt)
                    return res
                except Exception as e:
                    app.logger.exception('Login hit exception during password check.')
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
            app.logger.exception('Login hit exception during getting username and password from form.')
            return {
                    "message": "Something went wrong!2",
                    "error": str(e),
                    "data": None
            }, 500
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


    return render_template('home.html',current_user=current_user)

@app.route('/register', methods=('GET', 'POST'))
def register():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']

        # converting password to array of bytes 
        bytes = password.encode('utf-8') 

        # generating the salt 
        salt = bcrypt.gensalt() 

        hash = str(bcrypt.hashpw(bytes, salt))
        hash = hash[2:-1]
        #output is weird so it has to be truncated

        query = {
            'username': username,
            'password': hash,
            'role': 3
        }
        status = users.insert_one(query)

        return redirect(url_for('login'))


    return render_template('register.html')



@app.route('/singlePokemon')
@token_required
def singlePokemon(self):
    name = request.args.get('pokemonName', type = str)
    single_pokemon = pokemon.find_one({'pokemonName': name})
    image = grid_fs.get(single_pokemon['id'])
    base64_data = codecs.encode(image.read(), 'base64')
    image = base64_data.decode('utf-8')
    single_pokemon.update({"image":image})
    return render_template('singlePokemon.html', pokemonList=single_pokemon)


@app.route('/allPokemon')
@token_required
def allPokemon(self):

    all_pokemon = {}

    for single_pokemon in pokemon.find():
        image = grid_fs.get(single_pokemon['id'])
        base64_data = codecs.encode(image.read(), 'base64')
        image = base64_data.decode('utf-8')
        single_pokemon.update({"image":image})
        all_pokemon.update({single_pokemon['id']:single_pokemon})

    # for pkmn in all_pokemon:
    #     print(pkmn)

    return render_template('allPokemon.html', pokemonList=all_pokemon)


@app.route('/deletePokemon')
@token_required
def deletePokemon(self):
    name = request.args.get('pokemonName', type = str)
    single_pokemon = pokemon.find_one({'pokemonName': name})
    print(singlePokemon)
    print(single_pokemon['_id'])
    grid_fs.delete(single_pokemon['_id'])
    deleted_pokemon = pokemon.delete_one({'pokemonName': name})
    
    return render_template('deletedPokemon.html', deletedPokemon=deleted_pokemon)

@app.route('/updatePokemon', methods=('GET', 'POST'))
@token_required
def updatePokemon(current_user):
    if request.method=='POST':
        queryName = request.form['queryName']
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
        status = pokemon.update_one({'pokemonName': queryName},{"$set":query})

        return redirect(url_for('home'))


    return render_template('updatePokemon.html')

