import markovify
import re

from flask import Flask
from flask import request


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

def get_sentences(n, text_model):
    string = ""
    sentence_num = n if n is not None else default_num;
    for i in range(sentence_num):
        sentence = text_model.make_sentence()
        if sentence is not None:
            string += sentence
    clean_str = re.sub(r'\.([A-Z])', r'. \1', string)
    return clean_str


# ROUTES
# ===========================

@app.route("/english")
def english():
    request_num = int(request.args.get('num'));
    return get_sentences(request_num, text_model_english)

@app.route("/spanish")
def spanish():
    request_num = int(request.args.get('num'));
    return get_sentences(request_num, text_model_spanish)

@app.route("/")
def hello():
    return "Working"


# MAIN
# ===========================

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 5000)
