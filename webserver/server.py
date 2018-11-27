#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort
import datetime
import numbers

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "jh4021"
DB_PASSWORD = "lezx36sj"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

engine.execute("""INSERT INTO test(name) VALUES ('grace'), ('alan'), ('ada');""")

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:
  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2
  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  #cursor = g.conn.execute("SELECT name FROM street")
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at
#
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
  return render_template("anotherfile.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print name
  # cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
  # g.conn.execute(text(cmd), name1 = name, name2 = name);

  cmd = 'INSERT INTO test(name) VALUES (:name1)'
  g.conn.execute(text(cmd), name1 = name)

  return redirect('/')

@app.route('/search')
def search():
  return render_template("search.html")

@app.route('/searchzip')
def searchzip():
  cursor = g.conn.execute("SELECT zipcode FROM street")
  names = []
  for result in cursor:
    names.append(result['zipcode'])  # can also be accessed using result[0]
  context = dict(data=names)
  return render_template("searchzip.html", **context)

@app.route('/addx', methods=['POST', 'GET'])
def addx():
  zipcode = request.form['zipcode']
  # cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
  # g.conn.execute(text(cmd), name1 = name, name2 = name);
  cmd = 'SELECT name FROM street WHERE zipcode=:zipcode1'
  try:
    g.conn.execute(text(cmd), zipcode1=zipcode)
  except:
    context = 1
  else:
    cursor = g.conn.execute(text(cmd), zipcode1=zipcode)
    names = []
    names.append(cursor.keys())
    for result in cursor:
      names.append(result['name'])  # can also be accessed using result[0]
    cursor.close()
    context = dict(data=names)

  if context != 1:
    return render_template("results.html", context=context)
  else:
    return redirect('/another')

@app.route('/searchcol')
def searchcol():
  return render_template("searchcol.html")

def transfer(crowd):
  for x in crowd:
    if isinstance(x, float):
      int(x)

def searchall(what, form, x):
  form = str(form)
  what2 = request.form[str(what)]
  x = str(x)
  cmd = 'SELECT ' + x + ' FROM ' + form + ' WHERE ' + what + \
        '=:what1'

  try:
    g.conn.execute(text(cmd), what1=what2)
  except:
    context = 1
  else:
    cursor = g.conn.execute(text(cmd), what1=what2)
    names = []
    names.append(cursor.keys())
    for result in cursor:
      try:
        datetime.time.strftime(result[0], '%H:%M')
      except:
        x1 = result[0]
      else:
        x1 = datetime.time.strftime(result[0], '%H:%M')
      #x1 = datetime.time.strftime(result[0], '%H:%M')
      try:
        datetime.date.strftime(result[1], '%D')
      except:
        x2 = result[1]
      else:
        x2 = datetime.date.strftime(result[1], '%D')
      #x2 = datetime.date.strftime(result[1], '%D')
      x3 = result[2].encode('UTF-8')
      x4 = result[3].encode('UTF-8')
      x5 = int(result[4])
      x = [x1, x2, x3, x4, x5]
      names.append(x)  # can also be accessed using result[0]
    cursor.close()
    context = dict(data=names)
  return context

@app.route('/searchdist')
def searchdist():
  return render_template("searchdist.html")

def groupby(what, form):
  form = str(form)
  what2 = request.form[str(what)]
  cmd = 'SELECT COUNT(*)' + ' FROM ' + form + ' WHERE ' + what + '=:what1 GROUP BY '+ \
        what
  try:
    cursor = g.conn.execute(text(cmd), what1=what2)
  except:
    context = 1
  else:
    names = []
    names.append(cursor.keys())
    for result in cursor:
      names.append(int(result[0]))  # can also be accessed using result[0]
    cursor.close()
    context = dict(data=names)
  return context

def dist(what, form):
  form = str(form)
  what2 = str(what)

  cmd = 'SELECT '+ what2 +', COUNT(*) count' + ' FROM ' + form + ' GROUP BY '+ what2 + \
        ' ORDER BY count DESC'
  try:
    g.conn.execute(text(cmd), what1=what2)
  except:
    context = 1
  else:
    cursor = g.conn.execute(text(cmd), what1=what2)
    names = []
    names.append(cursor.keys())
    for result in cursor:
      xs = []
      for x in result:
        if isinstance(x, datetime.time):
          try:
            datetime.time.strftime(x, '%H:%M')
          except:
            x1 = x
          else:
            x1 = datetime.time.strftime(x, '%H:%M')
        elif isinstance(x, datetime.date):
          try:
            datetime.date.strftime(x, '%D')
          except:
            x1 = x
          else:
            x1 = datetime.date.strftime(x, '%D')
        elif isinstance(x, unicode):
          x1 = x.encode('UTF-8')
        elif isinstance(x, numbers.Integral):
          x1 = int(x)
        else:
          x1 = x
        xs.append(x1)

      names.append(xs)  # can also be accessed using result[0]
    cursor.close()
    context = dict(data=names)
  return context

def avg(what, form):
  what2 = str(what)
  cmd = 'SELECT '+ what2 +', AVG(score) avg' + ' FROM ' + form + ' GROUP BY '+ what2 + \
        ' ORDER BY avg DESC'
  try:
    g.conn.execute(text(cmd), what1=what2)
  except:
    context = 1
  else:
    cursor = g.conn.execute(text(cmd), what1=what2)
    names = []
    names.append(cursor.keys())
    for result in cursor:
      x1 = result[0].encode('UTF-8')
      x2 = result[1].encode('UTF-8')
      x3 = round(result[2], 2)
      x = (x1, x2, x3)
      names.append(x)  # can also be accessed using result[0]
    cursor.close()
    context = dict(data=names)
  return context

def judge(context):
  if context != 1:
    return render_template("results.html", context = context)
  else:
    return redirect('/another')

@app.route('/resultdist', methods=['POST', 'GET'])
def resultdist():
  try:
    str(request.form['group_by_item'])
  except:
    item = 100
  else:
    item = str(request.form['group_by_item'])

  if item == '1':
    context = dist('type_code', 'contributeby_vehicle')

  elif item == '2':
    context = dist('factor', 'contributeby_vehicle')

  elif item == '3':
    context = dist('c_time, c_date, name, borough', 'report')

  elif item == '4':
    context = dist('name, borough', 'collision_occurat')

  elif item == '5':
    context = dist('name, borough', 'written_comment_about')

  elif item == '6':
    context = avg('name, borough', 'evaluate')

  else:
    context = 1

  return judge(context)


@app.route('/results', methods=['POST', 'GET'])
def resultveh():
  context = groupby('type_code', 'contributeby_vehicle')
  return judge(context)

@app.route('/searchveh', methods=['POST', 'GET'])
def searchveh():
  cursor = g.conn.execute("SELECT distinct type_code FROM contributeby_vehicle")
  names = []
  for result in cursor:
    names.append(result[0].encode('UTF-8'))  # can also be accessed using result[0]
  context = dict(data=names)
  return render_template("searchveh.html", **context)

@app.route('/resultcol', methods=['POST', 'GET'])
def resultcol():
  context = searchall('c_time', 'collision_occurat', '*')
  return judge(context)


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()

