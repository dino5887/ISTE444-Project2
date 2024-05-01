import bcrypt 

# example password 
password = '123'

# converting password to array of bytes 
bytes = password.encode('utf-8') 

# generating the salt 
salt = bcrypt.gensalt() 

# Hashing the password 
hash = str(bcrypt.hashpw(bytes, salt))
hash = hash[2:-1]
#output is weird so it has to be truncated

print(hash)
