import codecs
import os
import time
from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
import bcrypt
import jwt
import json
import requests
import gridfs
from auth_middlewear import token_required
import logging
from datetime import datetime, timezone

# Creating formats needed for logging. This is easily swappable if you want.
# Was a little confused on what timezone you wanted. I have this written in my notes
# Logging Date Format: YYYY-MM-DD HH:MM:SS Timezone/Z
# time_format = "%Y-%m-%d %H:%M:%ST%Z"
time_format = "%Y-%m-%d %H:%M:%S T/%Z"
log_format = fmt='%(asctime)s - %(levelname)s - %(message)s'

# Create a logger and set the custom formatter
# Also sets log level to INFO
# Could be (DEBUG, INFO, WARNING, ERROR, CRITICAL)
logging.basicConfig(filename='app.log', encoding='utf-8', level=logging.INFO, format=log_format, datefmt=time_format)

app = Flask(__name__)

# Secure this if actually deployed
secret = 'aerop45gkaeh3$%Y^^YAc4'

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
                app.logger.info('Login Successful for user ', username)
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
            app.logger.error('Error with fetching the auth token. Username or password must be invalid')
            return {
                "message": "Error fetching auth token!, invalid username or password",
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
    app.logger.info('Now rendering login page.')
    return render_template('login.html')

@app.route('/home', methods=('GET', 'POST'))
@token_required
def home(current_user):
    app.logger.info('Start of the home route. This is where users can insert Pokemon they caught to their Pokedex.')
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
        app.logger.info('Successful insert of the Pokemon! Redirecting now for ', current_user)
        return redirect(url_for('home'))

    app.logger.info('Now rendering home page.')
    return render_template('home.html',current_user=current_user)

@app.route('/register', methods=('GET', 'POST'))
def register():
    app.logger.info('Start of the register route. This is where a user can sign up.')
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
        app.logger.info('Successful registration of the user! Redirecting now for ', username)
        return redirect(url_for('login'))

    app.logger.info('Now rendering register page.')
    return render_template('register.html')

@app.route('/singlePokemon')
@token_required
def singlePokemon(self):
    app.logger.info('Start of the singlePokemon route. This is where the user can view a single pokemon of their choosing.')
    name = request.args.get('pokemonName', type = str)
    single_pokemon = pokemon.find_one({'pokemonName': name})
    image = grid_fs.get(single_pokemon['id'])
    base64_data = codecs.encode(image.read(), 'base64')
    image = base64_data.decode('utf-8')
    single_pokemon.update({"image":image})
    app.logger.info('If user input an existing Pokemon with the right name, they should see a Pokemon now.')
    app.logger.info('Now rendering singlePokemon page.')
    return render_template('singlePokemon.html', pokemonList=single_pokemon)

@app.route('/allPokemon')
@token_required
def allPokemon(self):
    app.logger.info('Start of the allPokemon route. This is where the user can view all existing/inputted pokemon.')
    all_pokemon = {}

    app.logger.info('In front of for loop. Should start displaying pokemon now if any exist.')
    for single_pokemon in pokemon.find():
        image = grid_fs.get(single_pokemon['id'])
        base64_data = codecs.encode(image.read(), 'base64')
        image = base64_data.decode('utf-8')
        single_pokemon.update({"image":image})
        all_pokemon.update({single_pokemon['id']:single_pokemon})

    app.logger.info('Now rendering allPokemon page.')
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
    
    app.logger.info('Now rendering deletePokemon page.')
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

        app.logger.info('Successful update of the Pokemon! Redirecting now for ', current_user)
        return redirect(url_for('home'))

    app.logger.info('Now rendering updatePokemon page.')
    return render_template('updatePokemon.html')