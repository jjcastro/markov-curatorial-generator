import markovify
import re
import sys  

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
english_file = "./become-english.txt";
spanish_file = "./become-spanish.txt";


# LOGIC AND MARKOVIFY
# ===========================

app = Flask(__name__)

with open(english_file) as f:
    text_english = f.read()
with open(spanish_file) as f:
    text_spanish = f.read()

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

    # replace the artist's name (first full, then just last)
    full_name = fname + ' ' + lname
    string = string.replace(r'XXXX', '<i>'+full_name+'</i>', 1)
    named_str = re.sub(r'XXXX', '<i>'+lname+'</i>', string)

    # clean the resulting string
    clean_str = re.sub(r'\.([A-Z]|[a-z]|<)', r'. \1', named_str)

    return clean_str

def json_response(text, num, lang):
    message = {
        'sentences': int(num) if num is not None else default_num,
        'text': text,
        'language': lang
    }
    resp = jsonify(message)
    return resp

# ROUTES
# ===========================

@app.route("/english")
def english():
    request_num = request.args.get('num')
    fname = request.args.get('fname')
    lname = request.args.get('lname')

    if None in (fname, lname):
        message = { 'error': 'Must specify first name and last name.' }
        return jsonify(message)

    text = get_sentences(request_num, text_model_english, fname, lname)
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
    return json_response(text, request_num, 'spanish')

@app.route("/")
def hello():
    message = {
        'test': 'The API is working!'
    }
    return jsonify(message)


# MAIN
# ===========================

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 5000)
