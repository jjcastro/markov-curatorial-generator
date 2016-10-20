import markovify
import re
import sys  
import random

from flask          import Flask
from flask_cors     import CORS, cross_origin
from flask          import request
from flask_jsonpify import jsonify
from pymongo        import MongoClient

# FIX FOR ENCODING
# ===========================

reload(sys)  
sys.setdefaultencoding('utf8')


# DEFAULT VARIABLES
# ===========================

default_num = 5;
english_file = './files/become-english.txt'
spanish_file = './files/become-spanish.txt'

bits = {
    'english-influences': None,
    'spanish-influences': None,
    'english-cities': None,
    'spanish-cities': None
}


# CONNECTION TO MONGODB
# ===========================

uri = 'mongodb://becomeacurator:R2h83s4L9sQxzQ@ds021994.mlab.com:21994/become-a-curator'
client = MongoClient(uri)
db = client['become-a-curator']
collection = db['files']


# LOAD FILES AND DATABASE
# ===========================

with open(english_file) as f:
    text_english = f.read()
with open(spanish_file) as f:
    text_spanish = f.read()

# read the documents fromthe database
for key in bits:
    document = collection.find_one({ 'name': key })
    bits[key] = document['lines']


# LOGIC AND MARKOVIFY
# ===========================

app = Flask(__name__)

# enable CORS (Cross Origin Requests)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

text_model_english = markovify.Text(text_english)
text_model_spanish = markovify.Text(text_spanish)

def get_sentences(n, text_model, fname, lname):
    string = ''

    # use the default_num for sentences if not specified
    sentence_num = int(n) if n is not None else default_num;

    # generate the appropriate num of sentences
    for i in range(sentence_num):
        sentence = text_model.make_sentence()
        if sentence is not None:
            string += sentence

    # clean the resulting string
    clean_str = re.sub(r'\.([A-Z]|[a-z]|<)', r'. \1', string)
    return clean_str

def json_response(text, num, lang):
    message = {
        'sentences': int(num) if num is not None else default_num,
        'text': text,
        'language': lang
    }
    resp = jsonify(message)
    return resp

def process_name(text, fname, lname):
    # replace the artist's name (first full, then just last)
    full_name = fname + ' ' + lname
    string = text.replace(r'XXXX', '<i>'+full_name+'</i>', 1)
    named_str = re.sub(r'XXXX', '<i>'+lname+'</i>', string)
    return named_str

def process_bits(text, replaced, the_list):
    string = text
    ocurrences = text.count(replaced)

    # copy the list
    list_copy = list(the_list)

    # replace all ocurrences with random elements from *list*, and don't repeat
    for i in range(ocurrences):
        chosen_elem = random.choice(list_copy)
        string = string.replace(replaced, chosen_elem, 1)
        list_copy.remove(chosen_elem)

    return string

# ROUTES
# ===========================

@app.route('/')
def hello():
    message = {
        'test': 'The API is working!'
    }
    return jsonify(message)

@app.route('/english')
def english():
    request_num = request.args.get('num')
    fname = request.args.get('fname')
    lname = request.args.get('lname')

    if None in (fname, lname):
        message = { 'error': 'Must specify first name and last name.' }
        return jsonify(message)

    text = get_sentences(request_num, text_model_english, fname, lname)
    text = process_name(text, fname, lname)
    text = process_bits(text, 'AAAA', bits['english-influences'])
    text = process_bits(text, 'BBBB', bits['english-cities'])

    return json_response(text, request_num, 'english')

@app.route('/spanish')
def spanish():
    request_num = request.args.get('num')
    fname = request.args.get('fname')
    lname = request.args.get('lname')

    if None in (fname, lname):
        message = { 'error': 'Must specify first name and last name.' }
        return jsonify(message);

    text = get_sentences(request_num, text_model_spanish, fname, lname)
    text = process_name(text, fname, lname)
    text = process_bits(text, 'ZZZZ', bits['spanish-influences'])
    text = process_bits(text, 'YYYY', bits['spanish-cities'])

    return json_response(text, request_num, 'spanish')

@app.route('/bits', methods=['GET', 'POST'])
@cross_origin()
def add_bits():
    resp = jsonify({ 'Error': 'Couldn\'t find or open document.' })
    
    document_name = request.args.get('document')
    document = collection.find_one({ 'name':document_name })

    if document is not None:
        if request.method == 'POST':
            content = request.get_json()

            # write the string to the specified file
            result = collection.update_one(
                {'name': document_name},
                {
                    '$addToSet': {
                        'lines': content['string']
                    }
                }
            )

            # update the list with the modified file
            updated_document = collection.find_one({ 'name':document_name })
            bits[ document_name ] = updated_document['lines']

            # notify success
            message = {
                'success': True,
                'message': 'The string ' + content['string']
                         + ' has been added to the list ' + document_name
            }
            resp = jsonify(message)
        elif request.method == 'GET':
            message = {
                'name': document['name'],
                'lines': document['lines']
            }
            resp = jsonify(message)
    return resp

@app.route('/names', methods=['GET', 'POST'])
@cross_origin()
def add_bits():
    resp = jsonify({ 'Error': 'Couldn\'t find or open document.' })
    
    document = collection.find_one({ 'name':'users' })

    if document is not None:
        if request.method == 'POST':
            content = request.get_json()

            # write the string to the specified file
            result = collection.update_one(
                {'name': 'users'},
                {
                    '$addToSet': {
                        'users': content['user']
                    }
                }
            )

            # notify success
            message = {
                'success': True,
                'message': 'The name ' + content['user']
                         + ' has been added to the list.'
            }
            resp = jsonify(message)
        elif request.method == 'GET':
            message = {
                'users': document['users']
            }
            resp = jsonify(message)
    return resp

# MAIN
# ===========================

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000)
