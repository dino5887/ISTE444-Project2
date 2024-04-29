import requests

# url = 'http://google.com/favicon.ico'
url = 'https://pokeapi.co/api/v2/pokemon-form/132'
filename = url.split('/')[-1]
r = requests.get(url, allow_redirects=True)
open(filename, 'wb').write(r.content)