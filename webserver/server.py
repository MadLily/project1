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
from flask import Flask, request, render_template, g, url_for, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following uses the sqlite3 database test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111db.eastus.cloudapp.azure.com/username
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@w4111db.eastus.cloudapp.azure.com/ewu2493"
#
DATABASEURI = "postgresql://yb2356:GENXNR@w4111db.eastus.cloudapp.azure.com/yb2356"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 

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
  """
  Hid the List on index
  """
  # cursor = g.conn.execute("SELECT name FROM test")
  # names = []
  # for result in cursor:
  #   names.append(result['name'])  # can also be accessed using result[0]
  # cursor.close()

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
  # context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html")#, **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
# Example of adding new data to the database
# @app.route('/add', methods=['POST'])
# def add():
#   name = request.form['name']
#   g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
#   return redirect('/')



# """
# By Company
# """
# @app.route('/compsearch')
# def compsearch():
#   try: 
#     cursor = g.conn.execute("SELECT Company_Name FROM Company")
#   except Exception, e:
#     pass  
#   comp_names = []
#   for result in cursor:
#     comp_names.append(result[0])  # can also be accessed using result[0]
#   cursor.close()
#   context = dict(animation = comp_names)
#   return render_template("compsearch.html", **context)

"""
By Company
"""
@app.route('/compsearch', methods=['GET','POST'])
def compsearch():
  error = None
  try: 
    cursor = g.conn.execute("SELECT Company_Name FROM Company")
  except Exception, e:
    pass  
  comp_names = []
  for result in cursor:
    comp_names.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  #context = dict(animation = comp_names)
  if request.method == "POST":
    query_comp_name = request.form['comp_name']
    if query_comp_name not in comp_names:
      error = "The company your searched for is not in the database"
    else:
      rec = g.conn.execute("SELECT Company_Name FROM Company WHERE Company_Name = %s",(query_comp_name,))
      # rec = g.conn.execute("SELECT * FROM Comic_Draw_Publish c, Magazine m, Cartoonists d WHERE c.Comic_Name = %s,(query_comi_name,) AND c.Cartoonist_ID = d.Cartoonist_ID AND c.ISSN = m.ISSN")
      for res in rec:
        compNam=res['company_name']
      return redirect(url_for('company',compNam=compNam))
  return render_template("compsearch.html", comp_names=comp_names, error=error)


@app.route('/company/<compNam>')
def company(compNam):
  #global usrName
  rec = g.conn.execute("SELECT * FROM Company C WHERE C.company_name = %s",(compNam,))
  for res in rec:
    compName = res['company_name']
    compWeb = res['company_website']
    compCou = res['company_country']
    compDesc = res['company_description']
  an = g.conn.execute("SELECT * FROM Company C, Animation A WHERE C.company_name = %s AND C.company_name = A.company_name",(compNam,))
  compAni =[]
  for ani in an:
      compAni.append(ani['atitle'])
    # compAni = res['atitle']
    # carSex = res['cartoonist_gender']
    # carDesc = res['cartoonist_description']
    # magNam = res['magazine_name']
    # magLang = res['magazine_language']
    # magDesc = res['magazine_description']
  return render_template("company.html",compName=compName,compWeb=compWeb,compCou=compCou,compDesc=compDesc,compAni =compAni)
#  return render_template("comics.html",comID=comID,comDesc=comDesc,comIss=comIss,comNam=comNam,carNam=carNam,carBir=carBir,carSex=carSex,carDesc=carDesc)


# """
# By Company
# """
# @app.route('/compsearch')
# def compsearch():
#   try: 
#     cursor = g.conn.execute("SELECT Company_Name FROM Company")
#   except Exception, e:
#     pass  
#   comp_names = []
#   for result in cursor:
#     comp_names.append(result[0])  # can also be accessed using result[0]
#   cursor.close()

#   if request.method == 'POST':
#     query_comp_name = request.form['comp_name']
#     if query_comp_name not in comp_names:
#       error = "Invalid company name."
#     else:
#       rec = g.conn.execute("SELECT * FROM Company WHERE Company_Name = %s",(query_comp_name,))
      
#       for res in rec:
#         compNam=res['company_name']
#         compWeb = res['company_website']
#         compCou = res['company_country']
#         compDesc = res['company_description']
#         # aniDate = res['released_date']
#         # aniComp = res['company_name']
#         # aniCid = res['comic_id']
#       return render_template("company.html", compNam = compNam, compWeb = compWeb, compCou = compCou,
#        compDesc = compDesc) #, aniEpi = aniEpi,  aniComp = aniComp, cid = aniCid)
#   return render_template("compsearch.html", comp_names = comp_names, error=error)
  
  
  
  
"""
By Comic Name
"""
# @app.route('/comisearch')
# def comisearch():
#   try: 
#     cursor = g.conn.execute("SELECT Comic_Name FROM Comic_Draw_Publish")
#   except Exception, e:
#     pass  
#   comi_names = []
#   for result in cursor:
#     comi_names.append(result[0])  # can also be accessed using result[0]
#   cursor.close()
#   context = dict(comi = comi_names)
#   return render_template("comisearch.html", **context)

@app.route('/comisearch', methods=['GET','POST'])
def comisearch():
  error = None
  try: 
    cursor = g.conn.execute("SELECT Comic_Name FROM Comic_Draw_Publish")
  except Exception, e:
    pass  
  comi_names = []
  for result in cursor:
    comi_names.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  #context = dict()

  if request.method == 'POST':
    query_comi_name = request.form['comic_name'] #From comisearch.html
    if query_comi_name not in comi_names:
      error = "Invalid comic name."
    else:
      rec = g.conn.execute("SELECT Comic_ID FROM Comic_Draw_Publish C WHERE C.Comic_Name = %s",(query_comi_name,))
      # rec = g.conn.execute("SELECT * FROM Comic_Draw_Publish c, Magazine m, Cartoonists d WHERE c.Comic_Name = %s,(query_comi_name,) AND c.Cartoonist_ID = d.Cartoonist_ID AND c.ISSN = m.ISSN")
      for res in rec:
        comID=res['comic_id']
        # comDesc = res['comic_description']#[2]
        # cartID = res['cartoonist_id']#[3]
        # comIss = res['issn']#[4]
        # aniDate = res['released_date']
        # aniComp = res['company_name']
        # aniCid = res['comic_id']
      return redirect(url_for('comics',comID=comID))
      # return render_template("comics.html", comNam = comNam, comDesc = comDesc, cartID = cartID,
       # comIss = comIss) #, aniEpi = aniEpi,  aniComp = aniComp, cid = aniCid)
  return render_template("comisearch.html", comi = comi_names, error=error)

@app.route('/comics/<comID>', methods=['GET','POST'])
def comics(comID):
  #global usrName
  rec = g.conn.execute("SELECT * FROM Comic_Draw_Publish C, Cartoonists R, Magazine M, Animation A WHERE C.comic_id = %s AND C.comic_id = A.comic_id AND C.Cartoonist_ID = R.Cartoonist_ID AND M.ISSN = C.ISSN",(comID,))
  # rec = g.conn.execute("SELECT * FROM Comic_Draw_Publish C, Cartoonists R, Magazine M WHERE C.comic_id = %s AND C.Cartoonist_ID = R.Cartoonist_ID AND M.ISSN = C.ISSN",(comID,))
  #rec = g.conn.execute("SELECT * FROM Comic_Draw_Publish C, Cartoonists R WHERE C.comic_id = %s AND C.Cartoonist_ID = R.Cartoonist_ID",(comID,))
  for res in rec:
    comNam = res['comic_name']
    comDesc = res['comic_description']
    comIss = res['issn']
    carNam = res['cartoonist_name']
    carBir = res['date_of_birth']
    carSex = res['cartoonist_gender']
    carDesc = res['cartoonist_description']
    magNam = res['magazine_name']
    magLang = res['magazine_language']
    magDesc = res['magazine_description']
    aniName = res['atitle']
  return render_template("comics.html",comID=comID,comDesc=comDesc,comIss=comIss,comNam=comNam,carNam=carNam,carBir=carBir,carSex=carSex,carDesc=carDesc,magNam=magNam,magLang=magLang,magDesc=magDesc,aniName=aniName)
#  return render_template("comics.html",comID=comID,comDesc=comDesc,comIss=comIss,comNam=comNam,carNam=carNam,carBir=carBir,carSex=carSex,carDesc=carDesc)


# @app.route('/comics/<comID>', methods=['GET','POST'])
# def comics(comID):
#   #global usrName
#   rec = g.conn.execute("SELECT * FROM Comic_Draw_Publish C, Cartoonists R WHERE C.comic_id = %s AND C.Cartoonist_ID = R.Cartoonist_ID",(comID,))
#   # rec = g.conn.execute("SELECT * FROM Comic_Draw_Publish C WHERE C.comic_id = %s",(comID,))
#   for res in rec:
#     comDesc = res['comic_description']
#     comIss = res['issn']
#   return render_template("comics.html",comID=comID,comDesc=comDesc,comIss=comIss)


# @app.route('/comisearch', methods=['GET','POST'])
# def comisearch():
#   error = None
#   try: 
#     cursor = g.conn.execute("SELECT Comic_Name FROM Comic_Draw_Publish")
#   except Exception, e:
#     pass  
#   comi_names = []
#   for result in cursor:
#     comi_names.append(result[0])  # can also be accessed using result[0]
#   cursor.close()
#   #context = dict()

#   if request.method == 'POST':
#     query_comi_name = request.form['comic_name'] #From comisearch.html
#     if query_comi_name not in comi_names:
#       error = "Invalid comic name."
#     else:
#       rec = g.conn.execute("SELECT * FROM Comic_Draw_Publish C WHERE C.Comic_Name = %s",(query_comi_name,))
#       # rec = g.conn.execute("SELECT * FROM Comic_Draw_Publish c, Magazine m, Cartoonists d WHERE c.Comic_Name = %s,(query_comi_name,) AND c.Cartoonist_ID = d.Cartoonist_ID AND c.ISSN = m.ISSN")
#       for res in rec:
#         comNam=res['comic_name']#[1]#
#         comDesc = res['comic_description']#[2]
#         cartID = res['cartoonist_id']#[3]
#         comIss = res['issn']#[4]
#         # aniDate = res['released_date']
#         # aniComp = res['company_name']
#         # aniCid = res['comic_id']
#       return render_template("comics.html", comNam = comNam, comDesc = comDesc, cartID = cartID,
#        comIss = comIss) #, aniEpi = aniEpi,  aniComp = aniComp, cid = aniCid)
#   return render_template("comisearch.html", comi = comi_names, error=error)




# """
# By Cartoonist
# """
# @app.route('/cartsearch')
# def frontpage():
#   try: 
#     cursor = g.conn.execute("SELECT Cartoonist_Name FROM Cartoonists")
#   except Exception, e:
#     pass  
#   cart_names = []
#   for result in cursor:
#     cart_names.append(result[0])  # can also be accessed using result[0]
#   cursor.close()
#   context = dict(cart = cart_names)
#   return render_template("cartsearch.html", **context)

@app.route('/langsearch', methods=['GET','POST'])
def langsearch():
  error = None
  try: 
    cursor = g.conn.execute("SELECT DISTINCT language FROM Animation")
  except Exception, e:
    pass  
  ani_lang = []
  for result in cursor:
    ani_lang.append(result[0])  # can also be accessed using result[0]
  cursor.close()
  #context = dict()

  if request.method == 'POST':
    query_lang_name = request.form['langsearch'] #From comisearch.html
    if query_lang_name not in ani_lang:
      error = "Language Not Listed."
    else:
      rec = g.conn.execute("SELECT DISTINCT language FROM Animation WHERE language= %s",(query_lang_name,))
      # rec = g.conn.execute("SELECT * FROM Comic_Draw_Publish c, Magazine m, Cartoonists d WHERE c.Comic_Name = %s,(query_comi_name,) AND c.Cartoonist_ID = d.Cartoonist_ID AND c.ISSN = m.ISSN")
      for res in rec:
        langNam=res['language']
        # comDesc = res['comic_description']#[2]
        # cartID = res['cartoonist_id']#[3]
        # comIss = res['issn']#[4]
        # aniDate = res['released_date']
        # aniComp = res['company_name']
        # aniCid = res['comic_id']
      return redirect(url_for('language',langNam=langNam))
      # return render_template("comics.html", comNam = comNam, comDesc = comDesc, cartID = cartID,
       # comIss = comIss) #, aniEpi = aniEpi,  aniComp = aniComp, cid = aniCid)
  return render_template("langsearch.html", ani_lang = ani_lang, error=error)

@app.route('/language/<langNam>', methods=['GET','POST'])
def language(langNam):
  #global usrName
  rec = g.conn.execute("SELECT * FROM Animation A WHERE A.language = %s",(langNam,))
  # rec = g.conn.execute("SELECT * FROM Comic_Draw_Publish C, Cartoonists R, Magazine M WHERE C.comic_id = %s AND C.Cartoonist_ID = R.Cartoonist_ID AND M.ISSN = C.ISSN",(comID,))
  #rec = g.conn.execute("SELECT * FROM Comic_Draw_Publish C, Cartoonists R WHERE C.comic_id = %s AND C.Cartoonist_ID = R.Cartoonist_ID",(comID,))
  aniName = []
  for res in rec:
    aniName.append(res['atitle'])
  return render_template("language.html",aniName=aniName,langNam=langNam)





@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


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
