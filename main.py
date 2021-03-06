from flask import Flask, request
from flask import render_template
# from flask.ext.sqlalchemy import SQLAlchemy

from wtforms.validators import DataRequired
from wtforms import StringField, SubmitField, TextAreaField
from flask_wtf import FlaskForm

from typing import Dict, List
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm

import re


config = {
    "DEBUG": True,           # some Flask specific configs
    "CACHE_TYPE": "simple",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}

# import datetime

# from functools import lru_cache
# @lru_cache(maxsize=None)

config = {
    "DEBUG": True,           # some Flask specific configs
    "CACHE_TYPE": "simple",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
}


app = Flask(__name__)
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
app.config.from_mapping(config)
# cache = Cache(app)

app.config['SECRET_KEY'] = 'abc123'
bootstrap = Bootstrap(app)


# latest changes
latest_changes = "8-8-2020"

# read rumi jawi data
f = open("rumi-jawi-unicode.txt", mode="r", encoding='utf-8')
# rjDict1 = {}
# rjDict2 = {}
# rjDict3 = {}

# dummy values
rjDict1: Dict[str, List[str]] = {1: [1]}
# rjDict2: Dict[str, str] = {1: [1]}
# rjDict3: Dict[str, str] = {1: [1]}

# read line, append if homograph

# there are some double entry
# abc, اني
# abc, اني
# not homograph
for line in f:
    line = line.strip()
    r, j = line.split(",")
    r = r.strip()
    if r not in rjDict1:
        rjDict1[r] = [j]
    else:
        if ' '.join(rjDict1[r]) == j:
            continue
        rjDict1[r].append(j)

# read name data base
g = open("name-db.txt", mode="r", encoding='utf-8')
nDict: Dict[str, str] = {}
for line in g:
    line = line.strip()
    r, j = line.split(",")
    nDict[r] = j

# just keys == rumi
# keysDict = rjDict1.keys()

keysrjDict = list(rjDict1)

# norvig
alphabet = 'abcdefghijklmnopqrstuvwxyz'


def edits1(word):
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1]
    replaces = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts = [a + c + b for a, b in splits for c in alphabet]
    return set(deletes + transposes + replaces + inserts)


##
def edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1))


class RumiForm(FlaskForm):
    rumi = StringField('kata rumi', validators=[DataRequired()])
    submit = SubmitField('Submit')



@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404



@app.route('/transliterate', methods=['POST'])
# @cache.cached(timeout=50)
def transliterate():
    rumi = request.form['rumi']
    # print not working on browser
    # print "hello world"
    # print("The email address is in signup function '" + email + "'")

    # rumi.lower().strip() ## no effect ~~ 8/8/2020

    r = rumi.lower().strip()

    # similar words beli, belian, belian, etc belia
    r2: Dict[str, str] = {}

    if r in rjDict1:
        for k in keysrjDict:
            if re.search(str(r), str(k)):
                r2[k] = ' '.join(rjDict1[k])
        jawi = rjDict1[r]
        jawi = ' '.join(jawi)

        return render_template('transliterate.html',
                               rumi=r,
                               jawi=jawi,
                               r2=r2,
                               latest_changes=latest_changes)
    else:
        guest1 = edits1(r)
        guest2 = []
        for c in guest1:
            if c in rjDict1:
                guest2.append(c)
        return render_template('not_found_transliterasi.html',
                               rumi=r,
                               guesses=guest2,
                               latest_changes=latest_changes)
    # return pass


# set the secret key.  keep this really secret:


@app.route('/')
@app.route('/rumijawi')
# @cache.cached(timeout=50)
def rumijawi():
    # Store the current access time in Datastore.
    # store_time(datetime.datetime.now())

    # Fetch the most recent 10 access times from Datastore.
    # times = fetch_times(10)

    # return render_template('rumijawi.html', times=times,
    #                       latest_changes=latest_changes)
    return render_template('rumijawi.html', latest_changes=latest_changes)

@app.route('/index', methods=['GET', 'POST'])
def index():
    rumi = ''
    d = []
    form = RumiForm()
    jawi = ''

    if form.validate_on_submit():
        rumi = form.rumi.data
        form.rumi.data = ''
        # return render_template('index.html', form=form, melayu=melayu, d=d)

    if rumi == '':
        return render_template('index.html', form=form, rumi=rumi)

    r = rumi.lower().strip()

    # similar words beli, belian, belian, etc belia
    r2: Dict[str, str] = {}

    if r in rjDict1:
        # search for similar words: beli, belian, pembelian
        # keys = list(rjDict1)
        for k in keysrjDict:
            if re.search(str(r), str(k)):
                r2[k] = ' '.join(rjDict1[k])
        jawi = rjDict1[r]
        jawi = ' '.join(jawi)

        return render_template('index.html',
                               rumi=r,
                               form=form,
                               jawi=jawi,
                               r2=r2,
                               latest_changes=latest_changes)
    else:
        guest1 = edits1(r)
        guest2 = []
        for c in guest1:
            if c in rjDict1:
                guest2.append(c)
        return render_template('not_found_transliterasi.html',
                               rumi=r,
                               guesses=guest2,
                               latest_changes=latest_changes)



@app.route('/rumijawi_paragraph')
# @cache.cached(timeout=50)
def rumijawi_paragraph():
    return render_template('rumijawi_paragraph.html',
                           latest_changes=latest_changes)


@app.route('/transliterate_paragraph', methods=['POST'])
# @cache.cached(timeout=50)
def transliterate_paragraph():
    rumi = request.form['rumi']
    rumi = re.split(r"(\W)", rumi)

    # print not working on browser
    # print "hello world"
    # print("The email address is in signup function '" + email + "'")

    punc =      ['.', ',','?',':', ';', '-','(',')','!', '`', '"', '“',"'",',',"' "]
    punc_arab = ['.', ',','؟', ':', '؛', '-', ')','(', '!', '’', '"', '"',"'",',',"' "]


    paragraph_rumi = []
    paragraph_jawi = []
    cannot_transliterasi = []
    rj = {}
    number_of_untransliterate = 0
    for j in rumi:
        r = j.strip().lower()
        if r.lower().strip() == '':
            continue
        if r.lower().strip() == ' ':
            continue
        if r in rjDict1:
            paragraph_rumi.append(r)
            paragraph_jawi.append(' '.join(rjDict1[r])) # append string! not list 28/8/2020
            rj[r] = rjDict1[r]
        # elif r in punc:
        #     paragraph_rumi.append(r)
        #     paragraph_jawi.append(punc_arab[punc.index(r)])

        # any single char such as (,), ? , etc
        elif re.match("^.$",r):
            paragraph_rumi.append(r)
            paragraph_jawi.append(r)
        # check if numbor
        elif re.match("[0-9]",r):
            paragraph_rumi.append(r)
            paragraph_jawi.append(r)
        else:
            paragraph_rumi.append(r)
            paragraph_jawi.append('؟')
            number_of_untransliterate = number_of_untransliterate + 1
            cannot_transliterasi.append(r)

    return render_template('transliterate_paragraph.html',
                           paragraph_rumi=paragraph_rumi,
                           paragraph_jawi=paragraph_jawi,
                           number_of_untransliterate=number_of_untransliterate,
                           number_of_words=len(paragraph_jawi),
                           rj=rj, cannot_transliterasi=cannot_transliterasi,
                           latest_changes=latest_changes)
    # return pass


@app.route('/overview')
# @cache.cached(timeout=50)
def overview():
    return render_template('overview.html', latest_changes=latest_changes)


@app.route('/teknikal')
# @cache.cached(timeout=50)
def teknikal():
    return render_template('teknikal.html', latest_changes=latest_changes)


@app.route('/hubungi')
# @cache.cached(timeout=50)
def hubungi():
    return render_template('hubungi.html', latest_changes=latest_changes)


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


@app.route('/nama')
# @cache.cached(timeout=50)
def nama():
    return render_template('nama.html', latest_changes=latest_changes)


@app.route('/transliterate_name', methods=['POST'])
# @cache.cached(timeout=50)
def transliterate_name():

    rumi = request.form['rumi']
    rumi = re.split('(\W)', rumi)

    name_rumi = []
    name_jawi = []
    guest2 = []

    for r in rumi:
        if r.lower().strip() == '':
            continue
        if r.lower().strip() == ' ':
            continue
        if r.lower() in nDict:
            name_rumi.append(r.lower())
            name_jawi.append(nDict[r.lower()])
        else:
            name_rumi.append(r.lower())
            name_jawi.append("?")
            guest1 = edits1(r.lower())

            for c in guest1:
                if c in nDict:
                    guest2.append(c)

    return render_template('transliterate_name.html',
                           name_rumi=name_rumi,
                           name_jawi=name_jawi,
                           guest2=guest2)
