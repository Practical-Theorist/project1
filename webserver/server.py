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
from flask import Flask, request, render_template, g, redirect, Response, session, flash
import time
import datetime
import numbers

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

comment_id = 3
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

DATABASEURI = "postgresql://" + DB_USER + ":" + DB_PASSWORD + "@" + DB_SERVER + "/w4111"

#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


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
        import traceback;
        traceback.print_exc()
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
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        s = session['email_address']
        context = dict(data=s)
        return render_template('home.html', **context)


@app.route('/login', methods=['POST'])
def login():
    email_address = request.form['email_address']
    password = request.form['password']
    cursor = engine.execute("SELECT email_address, password FROM Users")
    for res in cursor:
        if (email_address, password) == res:
            session['logged_in'] = True
            session['email_address'] = res[0]
        else:
            flash('wrong information!')
    cursor.close()
    return home()


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


# Example of adding new data to the database

# strict slash? not sure
@app.route('/street/<name>/<borough>')
def specific_street(name, borough, check_op=False):
    name1 = name
    borough1 = borough
    # cmd = 'SELECT * FROM written_comment_about where name =' + (:name1) + 'and borough ='+ (:borough1)+';'
    cmd_p = 'SELECT avg(score) from evaluate where name = :x and borough = :y '
    cursor1 = g.conn.execute(text(cmd_p), x=name1, y=borough1)
    for result in cursor1:
        data_p = str(result[0])
    if data_p != 'None':
        data_p = float(data_p)
        data_p = float("{0:.2f}".format(data_p))
    else:
        data_p = 'None'

    cmd = 'SELECT content,uid,written_comment_about.time FROM written_comment_about where name = :x and borough = :y order by written_comment_about.time desc';

    cursor = g.conn.execute(text(cmd), x=name1, y=borough1)
    street_part = []
    for result in cursor:
        # print result[0]
        try:
            st_1 = result[0]
            st_1 = st_1.decode('UTF-8')
            st_2 = result[1]
            st_2 = st_2.decode('UTF-8')
            st_a = st_1.encode('UTF-8')
            st_b = st_2.encode('UTF-8')
            st_c = result[2]
        except:
            continue
        else:
            modified_result = st_a, st_b, st_c
            street_part.append(modified_result)
    cursor.close()
    context = dict(data=street_part, data1=name1, data2=borough1, data_3=data_p, check_op=check_op)

    return render_template('street_specific.html', **context)


@app.route('/street')
def street():
    cmd = 'SELECT name, borough FROM street order by name, borough;'

    cursor = g.conn.execute(text(cmd))
    street_part = []
    for result in cursor:
        # print result[0]
        try:
            st_1 = result[0]
            st_1 = st_1.decode('UTF-8')
            st_2 = result[1]
            st_2 = st_2.decode('UTF-8')
            st_a = st_1.encode('UTF-8')
            st_b = st_2.encode('UTF-8')
            print st_a, st_b
        except:
            continue
        else:
            modified_result = st_a, st_b
            street_part.append(modified_result)
    print street_part
    cursor.close()
    context = dict(data=street_part)

    return render_template('street_main.html', **context)


@app.route('/street/streetsearch', methods=['POST'])
def street_search():
    # if name == None or borough == None:
    name1 = request.form['street_name']
    borough1 = request.form['borough']

    cmd_c = 'SELECT name,borough from street where name = :x and borough = :y '

    cursor = g.conn.execute(text(cmd_c), x=name1, y=borough1)
    found = cursor.fetchall()
    print found
    if not found:
        cursor.close()
        return redirect('/street')
    else:

        cmd_p = 'SELECT avg(score) from evaluate where name = :x and borough = :y '
        cursor = g.conn.execute(text(cmd_p), x=name1, y=borough1)
        # print cursor1
        for result in cursor:
            data_p = str(result[0])
        # print data_p
        if data_p != 'None':
            data_p = float(data_p)
            data_p = float("{0:.2f}".format(data_p))
        else:
            data_p = 'None'
        cmd = 'SELECT content,uid,written_comment_about.time FROM written_comment_about where name = :x and borough = :y order by written_comment_about.time desc';

        cursor = g.conn.execute(text(cmd), x=name1, y=borough1)
        street_part = []
        for result in cursor:
            # print result[0]
            try:
                st_1 = result[0]
                st_1 = st_1.decode('UTF-8')
                st_2 = result[1]
                st_2 = st_2.decode('UTF-8')
                st_a = st_1.encode('UTF-8')
                st_b = st_2.encode('UTF-8')
                st_c = result[2]
            except:
                continue
            else:
                modified_result = st_a, st_b, st_c
                street_part.append(modified_result)

        cursor.close()

        context = dict(data=street_part, data1=name1, data2=borough1, data_3=data_p)

        return render_template('street_specific.html', **context)


@app.route('/comment', methods=['POST'])
def comment():
    user_email = session['email_address']
    name1 = request.form['street_name']
    # print name1
    borough1 = request.form['borough']
    comment = request.form['comment']
    check = str(comment)
    if len(comment) == 0:
        return specific_street(name1, borough1)

    date_c = time.strftime("%Y-%m-%d", time.localtime())
    cmd_c = 'SELECT max(cid) FROM written_comment_about where name = :x and borough = :y'
    try:
        g.conn.execute(text(cmd_c), x = name1, y = borough1)
    except:
        print 'works'
        cid = 0
    else:
        cursor = g.conn.execute(text(cmd_c),x = name1, y = borough1)
        row = cursor.fetchall()
        if row[0][0] is not None:
            print row
            print str(row[0][0])
            print(len(row))
            cid = int(str(row[0][0]))
        else:
            print 'workselse'
            cid = 0
    cid = cid + 1
    try:
        cmd = 'INSERT INTO written_comment_about (cid,name,borough,content,uid,"time") VALUES ((:cid),(:name),(:borough), (:content),(:uid),(:time_c))';
        g.conn.execute(text(cmd), cid=cid, name=name1, borough=borough1, uid=user_email, content=comment, time_c=date_c)
    except:
        return specific_street(name1, borough1)
    else:
        return specific_street(name1, borough1)


@app.route('/evaluate', methods=['POST'])
def evaluate():
    user_email = session['email_address']
    name1 = request.form['street_name']
    # print name1
    borough1 = request.form['borough']
    score = request.form['score']
    if len(score) == 0:
        return specific_street(name1, borough1)
    date_c = time.strftime("%Y-%m-%d", time.localtime())
    try:
        cmd = 'INSERT INTO evaluate (uid,name,borough,score,since) VALUES ((:uid),(:name),(:borough), (:score),(:since))';
        g.conn.execute(text(cmd), uid=user_email, name=name1, borough=borough1, score=score, since=date_c)

    except:
        return specific_street(name1, borough1)
    else:
        return specific_street(name1, borough1, check_op=True)


@app.route('/report', methods=['POST'])
def report():
    name1 = request.form['street_name']
    borough1 = request.form['borough']
    user_email = session['email_address']
    # print name1
    time1 = request.form['time']
    date1 = request.form['date']
    casualty = request.form['casualty']
    if len(casualty) == 0 or len(time1) == 0 or len(date1) == 0:
        return specific_street(name1, borough1)
    try:
        cmd1 = 'INSERT INTO collision_occurat(c_time,c_date,name,borough,casualty_number) VALUES ((:c_time),(:c_date),(:name), (:borough),(:casualty_number))';

        g.conn.execute(text(cmd1), c_time=time1, c_date=date1, borough=borough1, name=name1, casualty_number=casualty)

        cmd2 = 'INSERT INTO report(c_time,c_date,name,borough,uid) VALUES ((:c_time),(:c_date),(:name), (:borough),(:uid))';

        g.conn.execute(text(cmd2), c_time=time1, c_date=date1, borough=borough1, name=name1, uid=user_email)
    except:
        return specific_street(name1, borough1)
    # cmd3 = 'INSERT INTO contributeby_vehicle(c_time,c_date,name,borough,vid, type_code, factor) VALUES ((:c_time),(:c_date),(:name), (:borough),(:vid),(:type_code),(:factor))';

    # g.conn.execute(text(cmd3), c_time = time_1, c_date = date1, borough = borough1, name = name1, uid = user_email)
    else:
        return specific_street(name1, borough1, check_op=True)


@app.route('/street/reportnew', methods=['POST'])
def reportnew():
    name1 = request.form['street_name']
    borough1 = request.form['borough']
    user_email = session['email_address']
    zipcode = request.form['zipcode']
    time1 = request.form['time']
    date1 = request.form['date']
    casualty = request.form['casualty']
    if len(name1) == 0 or len(borough1) == 0 or len(zipcode) == 0 or len(casualty) == 0 or len(time1) == 0 or len(
            date1) == 0:
        print 1
        return redirect('/street')
    try:
        cmd_c = 'SELECT name,borough from street where name = :x and borough = :y '
        cursor = g.conn.execute(text(cmd_c), x=name1, y=borough1)
        found = cursor.fetchall()
        print found
        if not found:

            cmd0 = 'INSERT INTO street(name,borough,zipcode) VALUES ((:x), ( :y), ( :z)) '

            g.conn.execute(text(cmd0), x=name1, y=borough1, z=zipcode)

            cmd1 = 'INSERT INTO collision_occurat(c_time,c_date,name,borough,casualty_number) VALUES ((:c_time),(:c_date),(:name), (:borough),(:casualty_number))';

            g.conn.execute(text(cmd1), c_time=time1, c_date=date1, borough=borough1, name=name1,
                           casualty_number=casualty)

            cmd2 = 'INSERT INTO report(c_time,c_date,name,borough,uid) VALUES ((:c_time),(:c_date),(:name), (:borough),(:uid))';

            g.conn.execute(text(cmd2), c_time=time1, c_date=date1, borough=borough1, name=name1, uid=user_email)

        else:

            print 1

            cmd1 = 'INSERT INTO collision_occurat(c_time,c_date,name,borough,casualty_number) VALUES ((:c_time),(:c_date),(:name), (:borough),(:casualty_number))';

            g.conn.execute(text(cmd1), c_time=time1, c_date=date1, borough=borough1, name=name1,
                           casualty_number=casualty)

            cmd2 = 'INSERT INTO report(c_time,c_date,name,borough,uid) VALUES ((:c_time),(:c_date),(:name), (:borough),(:uid))';

            g.conn.execute(text(cmd2), c_time=time1, c_date=date1, borough=borough1, name=name1, uid=user_email)
    except:

        return redirect('/street')
        # cmd3 = 'INSERT INTO contributeby_vehicle(c_time,c_date,name,borough,vid, type_code, factor) VALUES ((:c_time),(:c_date),(:name), (:borough),(:vid),(:type_code),(:factor))';

        # g.conn.execute(text(cmd3), c_time = time_1, c_date = date1, borough = borough1, name = name1, uid = user_email)
    else:
        print 3
        return home()
    #return home()


####another author #################################################3333
@app.route('/another')
def another():
    return render_template("anotherfile.html")


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
        col = []
        for y in cursor.keys():
            y = y.decode('UTF-8').encode('UTF-8')
            col.append(y)

        names.append(col)
        for result in cursor:
            try:
                datetime.time.strftime(result[0], '%H:%M')
            except:
                x1 = result[0]
            else:
                x1 = datetime.time.strftime(result[0], '%H:%M')
            # x1 = datetime.time.strftime(result[0], '%H:%M')
            try:
                datetime.date.strftime(result[1], '%b-%d-%Y')
            except:
                x2 = result[1]
            else:
                x2 = datetime.date.strftime(result[1], '%b-%d-%Y')
            # x2 = datetime.date.strftime(result[1], '%D')
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
    cmd = 'SELECT COUNT(*)' + ' FROM ' + form + ' WHERE ' + what + '=:what1 GROUP BY ' + \
          what
    try:
        cursor = g.conn.execute(text(cmd), what1=what2)
    except:
        context = 1
    else:
        names = []
        for result in cursor:
            names.append(int(result[0]))  # can also be accessed using result[0]
        cursor.close()
        context = dict(data=names)
    return context


def dist(what, form):
    form = str(form)
    what2 = str(what)

    cmd = 'SELECT ' + what2 + ', COUNT(*) count' + ' FROM ' + form + ' GROUP BY ' + what2 + \
          ' ORDER BY count DESC'
    try:
        g.conn.execute(text(cmd), what1=what2)
    except:
        context = 1
    else:
        cursor = g.conn.execute(text(cmd), what1=what2)
        names = []
        col = []
        for y in cursor.keys():
            y = y.decode('UTF-8').encode('UTF-8')
            col.append(y)

        names.append(col)

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
                        datetime.date.strftime(x, '%b-%d-%Y')
                    except:
                        x1 = x
                    else:
                        x1 = datetime.date.strftime(x, '%b-%d-%Y')
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
    cmd = 'SELECT ' + what2 + ', AVG(score) avg_score' + ' FROM ' + form + ' GROUP BY ' + what2 + \
          ' ORDER BY avg_score DESC'
    try:
        g.conn.execute(text(cmd), what1=what2)
    except:
        context = 1
    else:
        cursor = g.conn.execute(text(cmd), what1=what2)
        names = []
        col = []
        for y in cursor.keys():
            y = y.decode('UTF-8').encode('UTF-8')
            col.append(y)

        names.append(col)
        for result in cursor:
            x1 = result[0].encode('UTF-8')
            x2 = result[1].encode('UTF-8')
            x3 = round(result[2], 2)
            x = [x1, x2, x3]
            names.append(x)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data=names)
    return context


def judge(context):
    if context != 1:
        return render_template("results.html", context=context)
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

@app.route('/reportre')
def resultre():
    x = session['email_address']
    cmd = "SELECT * FROM report WHERE uid=" + "'"+str(x)+"'"
    cursor = g.conn.execute(cmd)
    names = []
    col = []
    for y in cursor.keys():
        y = y.decode('UTF-8').encode('UTF-8')
        col.append(y)

    names.append(col)

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
                    datetime.date.strftime(x, '%b-%d-%Y')
                except:
                    x1 = x
                else:
                    x1 = datetime.date.strftime(x, '%b-%d-%Y')
            elif isinstance(x, unicode):
                x1 = x.encode('UTF-8')
            elif isinstance(x, numbers.Integral):
                x1 = int(x)
            else:
                x1 = x
            xs.append(x1)

        names.append(xs)

    context = dict(data=names)
    return judge(context)


if __name__ == "__main__":
    import click

    app.secret_key = os.urandom(12)


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
