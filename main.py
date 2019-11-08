from sys import argv
from database import Database
from professor import Professor
from flask import Flask, request, make_response, redirect, url_for
from flask import render_template

app = Flask(__name__, template_folder='.')

#-------------------------------------------------------------------------------

@app.route('/')
def index():

    database = Database()
    database.connect()
    results = database.search(formInfo)
    database.disconnect()

    response = make_response('index.html', professors = results)
    return(response)

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    if len(argv) != 2:
        print('Usage: ' + argv[0] + ' port')
        exit(1)
    app.run(host='0.0.0.0', port=int(argv[1]), debug=True)
