from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient 
app = Flask(__name__)

client = MongoClient('localhost', 27017)

db = client.Pokedex
pokemon = db.Pokemon

@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method=='POST':
        pokedexNumber = int(request.form['pokedexNumber'])
        pokemonName = request.form['pokemonName']
        numberCaught = int(request.form['numberCaught'])
        
        pokemon.insert_one({'pokedexNumber': pokedexNumber, 'pokemonName': pokemonName, 'numberCaught': numberCaught})
        return redirect(url_for('index'))

    all_pokemon = pokemon.find()
    return render_template('index.html', pokemon=all_pokemon)

# @app.route('/')
# def hello():
#     return '<h1>Hello, World!</h1>'

@app.route('/about')
def about():
    return '<h3>This is a Flask web application.</h3>'