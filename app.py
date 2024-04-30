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

        target = os.path.join(APP_ROOT, 'pictures/')  #folder path
        if not os.path.isdir(target):
            os.mkdir(target)     # create folder if not exits

        upload = request.files['picture']
        filename = upload.filename
        destination = "/".join([target, filename])
        upload.save(destination)
        #pokemon.insert_one({'': filename})   #insert into database mongo db

        
        fs = gridfs.GridFS(db, collection='pokemon')

        with open(destination, filename) as file_data:
            data = file_data.read()

        fs.put(data, filename=filename)
        pokemon.insert_one({'pokedexNumber': pokedexNumber, 'pokemonName': pokemonName, 'numberCaught': numberCaught, 'picture': filename})
        return redirect(url_for('home'))

    #all_pokemon = pokemon.find()
    return render_template('home.html')


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