import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/Pokedex")
mydb = myclient["Pokedex"]
myColl = mydb["Pokemon"]
