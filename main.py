from sys import argv
from database import Database
from professor import Professor
from re import sub
from flask import Flask, request, make_response, redirect, url_for, session
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_heroku import Heroku
from CASClient import CASClient

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# generated by os.urandom(16)
app.secret_key = b'm\xb5\xe6\xef4\xb5\x02_\x8f\xe4\xffpw\xccu\xc4'
heroku = Heroku(app)
db = SQLAlchemy(app)

#-------------------------------------------------------------------------------
@app.route('/login', methods=['GET'])
def login():
    CASClient().authenticate()
    return redirect(url_for('index'))

#-------------------------------------------------------------------------------

@app.route('/', methods=['GET', 'POST'])
def index():

    profPics = {
        'Adam Finkelstein': 'https://live.staticflickr.com/65535/49174808528_55680f30e5_n.jpg',
        'Alan Kaplan': 'https://live.staticflickr.com/65535/49174827063_25053c72cf_n.jpg',
        'Amit Levy': 'https://live.staticflickr.com/65535/49179992102_0d98b2bb34_n.jpg',
        'Andrew Appel': 'https://live.staticflickr.com/65535/49179992102_0d98b2bb34_n.jpg',
        'Arvind Narayanan': 'https://live.staticflickr.com/65535/49179784711_637259a4b4_n.jpg',
        'Barbara Engelhardt': 'https://live.staticflickr.com/65535/49179992077_74492d2c16_n.jpg',
        'Bernard Chazelle': 'https://live.staticflickr.com/65535/49179293028_bef3e4930c_n.jpg',
        'Brian Kernighan': 'https://live.staticflickr.com/65535/49179784656_afdd306907_n.jpg',
        'Christiane Fellbaum': 'https://live.staticflickr.com/65535/49179784631_705b6aa1c5_n.jpg',
        'Christopher Moretti': 'https://live.staticflickr.com/65535/49179329783_eac0ed1d8d_n.jpg',
        'Daniel Leyzberg': 'https://live.staticflickr.com/65535/49179992022_209f93deb7_n.jpg',
        'Danqi Chen': 'https://live.staticflickr.com/65535/49179292963_7c04f27026_n.jpg',
        'David August': 'https://live.staticflickr.com/65535/49179292933_c4246282e8_n.jpg',
        'David Dobkin': 'https://live.staticflickr.com/65535/49179292923_a84d098dab_n.jpg',
        'David Walker': 'https://live.staticflickr.com/65535/49179784551_8c893c24be_n.jpg',
    }

    if 'username' not in session:
         session['profs'] = None
         html = render_template('login.html')
         response = make_response(html)
         return(response)

    username = session['username']

    allAreas = ['Computational Biology', 'Computer Architecture', 'Economics/Computation', 'Graphics', 'Vision', 'Machine Learning', 'AI', 'Natural Language Processing', 'Policy', 'Programming Languages/Compilers', 'Security & Privacy', 'Systems', 'Theory']
    profList = session['profs']
    profData = Professor('', '', '', '', '', '', '')

    if request.method == 'GET':
        if request.args.get('profid') is not None:
            profid = request.args.get('profid')
            if  profid.strip() == '':
                errorMsg = 'Missing profid'
                return redirect(url_for('error', errorMsg=errorMsg))
            try:
                int(profid)
            except ValueError:
                errorMsg = 'Profid is not numeric'
                return redirect(url_for('error', errorMsg=errorMsg))

            database = Database()
            database.connect()
            profData = database.profSearch(profid)
            database.disconnect()

            profTitles = profData.getTitles()
            profLinks = profData.getLinks()

        else:
            profTitles = ''
            profLinks = ''

    html = render_template('index.html', user=username, professors = profList, prof = profData, titles = profTitles, links = profLinks, profPics = profPics)
    response = make_response(html)
    
    session['profs'] = profList
    return(response)

#-------------------------------------------------------------------------------

@app.route('/searchresults')
def searchResults():
    allAreas = ['Computational Biology', 'Computer Architecture', 'Economics/Computation', 'Graphics', 'Vision', 'Machine Learning', 'AI', 'Natural Language Processing', 'Policy', 'Programming Languages/Compilers', 'Security & Privacy', 'Systems', 'Theory']

    areas = request.args.getlist('areas')
    keywords = request.args.getlist('keywords')

    if len(areas) == 0 and len(keywords) == 0:
        areas = allAreas

    searchInput = [areas, keywords]

    database = Database()
    database.connect()
    results = database.search(searchInput)
    profDict = database.rankResults(results)
    database.disconnect()

    profList = []
    for prof in profDict:
        profname = prof[0]
        areas = prof[2]
        profid = prof[1]
        info = [profname, areas, profid] #create a list for the prof
        profList.append(info)
    resultsnum = len(profList)

    html = '<hr></hr> <h3>'+str(resultsnum)+' Search Results</h3><h3>Advisors</h3><ul>'
    for prof in profList:
        html += '<li><a href="/?profid='+str(prof[2])+'">'+str(prof[0]) + ' ' + str(prof[1])+'</li></a>'
    html += '</ul>'
    html.encode('utf-8')
    response = make_response(html)
    session['profs'] = profList
    return(response)

#-------------------------------------------------------------------------------

@app.route('/resources')
def resources():
    if 'username' not in session:
         return redirect(url_for('index'))
    html = render_template('resources.html')
    response = make_response(html)
    return(response)

#-------------------------------------------------------------------------------
@app.route('/error')
def error():
    if 'username' not in session:
        return redirect(url_for('index'))
    errorMsg = request.args.get('errorMsg')

    html = render_template('error.html', errorMsg=errorMsg)
    response = make_response(html)
    return(response)
#-------------------------------------------------------------------------------

@app.route('/logout')
def logout():
    return CASClient().logout()
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    if len(argv) != 2:
        print('Usage: ' + argv[0] + ' port')
        exit(1)
    app.run(host='0.0.0.0', port=int(argv[1]), debug=True)