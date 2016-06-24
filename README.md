# Curatorial statement generator

Generates curatorial statements for contemporary art expositions, using Markov chains and texts from galleries around the world. For more info, text sources and a more detailed explanation visit [becomeacurator.com](http://becomeacurator.com).

## About the code

This is a streamlined backend written in Python using the Flask microframework, that connects to a MongoDB database that hosts the text. To install:

* Change the MongoDB connection in `app.py`
* Install dependencies described in `requirements.txt` using `pip`
* Run the server `python app.py`

Uses @jsvine's [markov chains implementation](https://github.com/jsvine/markovify/).
