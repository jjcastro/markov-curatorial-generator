import markovify
import re
import sys  
import random

from flask import Flask
from flask import request
# from flask import jsonify
from flask_jsonpify import jsonify

# FIX FOR ENCODING
# ===========================

reload(sys)  
sys.setdefaultencoding('utf8')


# DEFAULT VARIABLES
# ===========================

default_num = 5;
english_file = './files/become-english.txt'
spanish_file = './files/become-spanish.txt'

files = {
    'english-influences': {
        'filename': './files/english-influences.txt',
        'list': None
    },
    'spanish-influences': {
        'filename': './files/spanish-influences.txt',
        'list': None
    },
    'english-cities': {
        'filename': './files/english-cities.txt',
        'list': None
    },
    'spanish-cities': {
        'filename': './files/spanish-cities.txt',
        'list': None
    }
}

# LOGIC AND MARKOVIFY
# ===========================

app = Flask(__name__)

with open(english_file) as f:
    text_english = f.read()
with open(spanish_file) as f:
    text_spanish = f.read()

with open(files['english-influences']['filename']) as f:
    files['english-influences']['list'] = f.read().splitlines() 

with open(files['spanish-influences']['filename']) as f:
    files['spanish-influences']['list'] = f.read().splitlines() 

with open(files['english-cities']['filename']) as f:
    files['english-cities']['list'] = f.read().splitlines() 

with open(files['spanish-cities']['filename']) as f:
    files['spanish-cities']['list'] = f.read().splitlines() 

text_model_english = markovify.Text(text_english)
text_model_spanish = markovify.Text(text_spanish)

def get_sentences(n, text_model, fname, lname):
    string = ""

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

@app.route("/")
def hello():
    message = {
        'test': 'The API is working!'
    }
    return jsonify(message)

@app.route("/english")
def english():
    request_num = request.args.get('num')
    fname = request.args.get('fname')
    lname = request.args.get('lname')

    if None in (fname, lname):
        message = { 'error': 'Must specify first name and last name.' }
        return jsonify(message)

    text = get_sentences(request_num, text_model_english, fname, lname)
    text = process_name(text, fname, lname)
    text = process_bits(text, 'AAAA', files['english-influences']['list'])
    text = process_bits(text, 'BBBB', files['english-cities']['list'])

    return json_response(text, request_num, 'english')

@app.route("/spanish")
def spanish():
    request_num = request.args.get('num')
    fname = request.args.get('fname')
    lname = request.args.get('lname')

    if None in (fname, lname):
        message = { 'error': 'Must specify first name and last name.' }
        return jsonify(message);

    text = get_sentences(request_num, text_model_spanish, fname, lname)
    text = process_name(text, fname, lname)
    text = process_bits(text, 'ZZZZ', files['spanish-influences']['list'])
    text = process_bits(text, 'YYYY', files['spanish-cities']['list'])

    return json_response(text, request_num, 'spanish')

@app.route('/add', methods=['GET', 'POST'])
def add_bits():
    print 'entering'
    print request.method
    resp = jsonify({ 'Error': 'Couldn\'t find or open file.' })
    
    file_from_req = request.args.get('file')
    file_name = files[ file_from_req ]['filename']

    with open(file_name, 'a+') as f:
        if request.method == 'POST':
            content = request.get_json()

            # write the string to the specified file
            f.write("\n")
            f.write(content['string'])

            # update the list with the modified file
            f.seek(0)
            files[ file_from_req ]['list'] = f.read().splitlines()

            # notify success
            message = {
                'success': True,
                'message': 'The string ' + content['string']
                         + ' has been added to the list ' + file_from_req
            }
            resp = jsonify(message)
        elif request.method == 'GET':
            f.seek(0)
            message = {
                'lines': f.read().splitlines()
            }
            resp = jsonify(message)
    return resp




# MAIN
# ===========================

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 5000)
