import markovify
from flask import Flask

app = Flask(__name__)

# Get raw text as string.
with open("./become-english.txt") as f:
    text_english = f.read()

with open("./become-spanish.txt") as f:
    text_spanish = f.read()

# Build the model.
text_model_english = markovify.Text(text_english)
text_model_spanish = markovify.Text(text_spanish)

def get_sentences(n, text_model):
    string = ""
    for i in range(5):

        string += text_model.make_sentence()
    return string

@app.route("/english")
def english():
    return get_sentences(5, text_model_english)

@app.route("/spanish")
def spanish():
    return get_sentences(5, text_model_spanish)

if __name__ == "__main__":
    app.run()
