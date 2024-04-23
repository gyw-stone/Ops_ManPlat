import random
import string
#def generate_random_password(length):
#    characters = string.ascii_letters + string.digits + string.punctuation
#    password = ''.join(random.choice(characters) for _ in range(length))
#    return password
def generate_random_password(length, types):
    characters = ''
    if 'number' in types:
        characters += string.digits
    if 'letter' in types:
        characters += string.ascii_letters
    if 'symbol' in types:
        characters += string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password
