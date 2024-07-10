from crypt import methods
from datetime import datetime
from operator import methodcaller
from flask import Flask, flash, redirect, render_template, request, session
import sqlite3
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlite3 import Error
from helpers import apology, login_required
from os import path
import math
from flask import Flask, request, jsonify
from transformers import GPT2Tokenizer, GPT2LMHeadModel
import torch

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
def createConnection(dbfile, moviename):
    conn = None
    try:
        ROOT = path.dirname(path.realpath(__file__))
        conn = sqlite3.connect(path.join(ROOT, dbfile))
        db = conn.cursor()
        db.execute("SELECT * FROM movies WHERE title = (?)",[moviename])
        conn.commit()
        return db.fetchall()

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
def runQuery(dbfile,query):
    conn = None
    try:
        ROOT = path.dirname(path.realpath(__file__))
        conn = sqlite3.connect(path.join(ROOT, dbfile))
        db = conn.cursor()
        db.execute(query)
        conn.commit()
        return db.fetchall()
    except Error as e:
        if conn:
            conn.close()


model_name = "distilgpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
conversation_history = []

@app.route('/generate', methods=['GET'])
def generate_text():
    global conversation_history
    user_input = "How are you?"  # Example string input

    # Add a prompt directly
    prompt = f"User: {user_input}\nBot:"
    
    # Append user input to conversation history
    conversation_history.append(prompt)
    
    # Concatenate conversation history and encode it
    input_text = "\n".join(conversation_history)
    inputs = tokenizer.encode(input_text, return_tensors='pt', padding=True, truncation=True, max_length=512)
    attention_mask = torch.ones(inputs.shape, dtype=torch.long)  # Create an attention mask with all ones

    with torch.no_grad():
        outputs = model.generate(inputs, attention_mask=attention_mask, max_length=100, num_return_sequences=1)
    
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract the chatbot's response and add to conversation history
    bot_response = generated_text[len(input_text):].strip()
    conversation_history.append(f"{bot_response}")
    
    return jsonify({'response': bot_response})

@app.route("/knowledge-base", methods=['GET','POST'])
def know_base():
    return render_template("knowledge-base.html")

@app.route("/settings", methods=["GET", "POST"])
def settings():
    is_valid = True
    ROOT = path.dirname(path.realpath(__file__))
    conn = sqlite3.connect(path.join(ROOT, "users.db"))
    db = conn.cursor()
    try: db.execute("SELECT username FROM userInfo WHERE id = (?)",[session["user_id"]])
    except: is_valid = False
    if is_valid:
        username = db.fetchall()[0][0]
        username = ", " + username
    else:
        username = ""
    username = username.replace(",","")
    username = username.replace(" ","")
    return render_template("settings.html", username=username)

@app.route("/profile", methods=['GET','POST'])
def profile():
    is_valid = True
    ROOT = path.dirname(path.realpath(__file__))
    conn = sqlite3.connect(path.join(ROOT, "users.db"))
    db = conn.cursor()
    try: db.execute("SELECT username FROM userInfo WHERE id = (?)",[session["user_id"]])
    except: is_valid = False
    if is_valid:
        username = db.fetchall()[0][0]
        username = ", " + username
    else:
        username = ""
    username = username.replace(",","")
    username = username.replace(" ","")
    return render_template("profile.html", username=username)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
@app.route("/chat", methods=["GET", "POST"])
def chat():
    return render_template("chat.html")

@app.route("/plant", methods=["GET", "POST"])
def plant():
    return render_template("plant.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        try:
            ROOT = path.dirname(path.realpath(__file__))
            conn = sqlite3.connect(path.join(ROOT, "users.db"))
            db = conn.cursor()
            db.execute("SELECT * FROM userInfo WHERE username = (?)",[request.form.get('username')])
            conn.commit()
            rows = db.fetchall()

        except Error as e:
            print(e)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout", methods=["GET","POST"])
def logout():
    del session["user_id"]
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    ROOT = path.dirname(path.realpath(__file__))
    conn = sqlite3.connect(path.join(ROOT, "users.db"))
    db = conn.cursor()
    username = request.form.get("username")
    password = request.form.get("password")
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("Username cant be blank")
        try:
            db.execute("SELECT username FROM userInfo WHERE username = (?)",[username])
            conn.commit()
            rows = db.fetchall()

        except Error as e:
            print(e)
        if len(rows) > 0:
            row = rows[0]
            if username == row[0]:
                return apology("Username already taken")
        if not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Password fields cant be empty")
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords dont match")
        try:
            db.execute("INSERT INTO userInfo (username, hash) VALUES (?,?)",[username,generate_password_hash(password)])
            conn.commit()
            user_id = db.lastrowid
        except Error as e:
            print(e)

        try:
            db.execute("SELECT * FROM userInfo WHERE username = ?",[username])
            conn.commit()
            rows = db.fetchall()
        except Error as e:
            print(e)
        row = rows[0]
        session["user_id"] = row[0]
        try:
            db.execute("UPDATE userInfo SET loggedfilms = 0 WHERE id = ?",[username,generate_password_hash(password)])
            conn.commit()
        except Error as e:
            print(e)
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/", methods=["GET","POST"])
def index():
    is_valid = True
    ROOT = path.dirname(path.realpath(__file__))
    conn = sqlite3.connect(path.join(ROOT, "users.db"))
    db = conn.cursor()
    try: db.execute("SELECT username FROM userInfo WHERE id = (?)",[session["user_id"]])
    except: is_valid = False
    if is_valid:
        username = db.fetchall()[0][0]
        username = ", " + username
    else:
        username = ""
    username = username.replace(",","")
    username = username.replace(" ","")
    return render_template("index.html", username = username)


@app.route("/movie",methods=["GET","POST"])
def movie():
    rating = {1:"unchecked", 2: "unchecked", 3:"unchecked", 4:"unchecked", 5:"unchecked"}
    if request.method == "POST":
        print(request.form.get("moviename"))
        movie = createConnection(r"movies.db",request.form.get("moviename"))
        print(movie)
        ROOT = path.dirname(path.realpath(__file__))
        conn = sqlite3.connect(path.join(ROOT, "users.db"))
        db = conn.cursor()
        try: db.execute("SELECT * FROM reviews WHERE user_id = (?) AND movie_id = (?)", [session["user_id"],movie[0][0]])
        except: return redirect("register")
        currentReviews = db.fetchall()
        db.execute("SELECT * FROM list WHERE user_id = (?)",[session["user_id"]])
        availableLists = db.fetchall()
        tmpReviews = []
        for currentReview in currentReviews:
            db.execute("SELECT username FROM userInfo WHERE id = (?)",[session["user_id"]])
            username = db.fetchall()[0][0]
            tmpList = list(currentReview)
            tmpList[1] = username
            tmpReviews.append(tmpList)
        db.execute("SELECT * FROM ratings WHERE user_id = (?) AND movie_id = (?)",[session["user_id"], movie[0][0]])
        ratingDatabase = db.fetchall()
        if len(ratingDatabase) == 0:
            pass
        else:
            rating[ratingDatabase[0][3]] = "checked"
        return render_template("movie.html", movie = movie, rating = rating, reviews = tmpReviews, lists = availableLists)
    else:
        ROOT = path.dirname(path.realpath(__file__))
        conn = sqlite3.connect(path.join(ROOT, "users.db"))
        db = conn.cursor()
        db.execute("SELECT * FROM list WHERE user_id = (?)",[session["user_id"]])
        availableLists = db.fetchall()
        movie = createConnection(r"movies.db",request.args["moviename"])
        selectedRating = request.args["rating"]
        movie_id = movie[0][0]
        db.execute("SELECT * FROM ratings WHERE user_id = (?) AND movie_id = (?)", [5, movie_id])
        ratingDatabase = db.fetchall()
        ROOT = path.dirname(path.realpath(__file__))
        conn = sqlite3.connect(path.join(ROOT, "users.db"))
        db = conn.cursor()
        db.execute("SELECT * FROM reviews WHERE user_id = (?) AND movie_id = (?)", [session["user_id"],movie_id])
        currentReviews = db.fetchall()
        tmpReviews = []
        for currentReview in currentReviews:
            db.execute("SELECT username FROM userInfo WHERE id = (?)",[session["user_id"]])
            username = db.fetchall()[0][0]
            tmpList = list(currentReview)
            tmpList[1] = username
            tmpReviews.append(tmpList)
        if len(ratingDatabase) == 0:
            db.execute("INSERT INTO ratings (user_id, movie_id, date, rating) VALUES (?,?,?,?)",[session["user_id"],movie_id,datetime.now(),selectedRating])
            conn.commit()
        elif ratingDatabase[0][3] == selectedRating:
            pass
        elif ratingDatabase[0][3] != selectedRating:
            db.execute("UPDATE ratings SET date = (?), rating = (?) WHERE user_id = (?) AND movie_id = (?)",[datetime.now(),selectedRating,session["user_id"], movie_id])
            conn.commit()
        return render_template("movie.html",movie = movie, rating = rating,reviews = tmpReviews, lists = availableLists)

@app.route("/search", methods =["GET","POST"])
def search():
    ROOT = path.dirname(path.realpath(__file__))
    conn = sqlite3.connect(path.join(ROOT, "movies.db"))
    db = conn.cursor()
    if request.method == "GET":
        return render_template("search.html")
    else:
        dbquery = "SELECT * FROM movies WHERE title LIKE '%"+ request.form.get("moviename")+ "%';"
        movies = db.execute(dbquery).fetchall()
        return render_template("searchresults.html", movies = movies, searchquery = request.form.get("moviename"))

@app.route("/year", methods=["GET", "POST"])
def year():
    ROOT = path.dirname(path.realpath(__file__))
    conn = sqlite3.connect(path.join(ROOT, "movies.db"))
    db = conn.cursor()
    if request.method == "POST":
        dbquery = "SELECT * FROM movies WHERE year = "+ request.form.get("releaseyear")+ ";"
        years = db.execute(dbquery).fetchall()
        return render_template("year.html", years = years)
    else:
        return redirect("/")

@app.route("/film", methods=["GET","POST"])
def film():
    ROOT = path.dirname(path.realpath(__file__))
    conn = sqlite3.connect(path.join(ROOT, "movies.db"))
    db = conn.cursor()
    if request.method == "GET":
        dbquery = "SELECT * FROM movies WHERE year = "+ request.form.get("releaseyear")+ ";"
        years = db.execute(dbquery).fetchall()
        return render_template("year.html", years = years)

@app.route("/community", methods = ["GET","POST"])
def films():
    ROOT = path.dirname(path.realpath(__file__))
    conn = sqlite3.connect(path.join(ROOT, "plant.db"))
    db = conn.cursor()
    db.execute("SELECT * FROM articles")
    articles = db.fetchall()
    print(articles)
    return render_template("community.html", articles = articles)


@app.route("/reviews", methods = ["GET","POST"])
def reviews():
    if request.method == "POST":
        reviewText = request.form.get("reviewText")
        movieID = request.form.get("movieID")
        ROOT = path.dirname(path.realpath(__file__))
        conn = sqlite3.connect(path.join(ROOT, "users.db"))
        db = conn.cursor()
        db.execute("INSERT INTO reviews (user_id, movie_id, date, text) VALUES (?,?,?,?)",[session["user_id"],movieID,datetime.now(),reviewText])
        conn.commit()
        db.execute("SELECT * FROM reviews WHERE user_id = (?)",[session["user_id"]])
        movies = db.fetchall()
        ROOT = path.dirname(path.realpath(__file__))
        conn = sqlite3.connect(path.join(ROOT, "movies.db"))
        db = conn.cursor()
        tmpMovies = []
        for movie in movies:
            db.execute("SELECT * FROM movies WHERE id = (?)",[movie[2]])
            result = db.fetchall()
            tmpList = list(movie)
            tmpList.append(result[0][1])
            tmpList.append(result[0][2])
            tmpMovies.append(tmpList)
        return render_template("review.html", movies = tmpMovies)
    else:
        ROOT = path.dirname(path.realpath(__file__))
        conn = sqlite3.connect(path.join(ROOT, "users.db"))
        db = conn.cursor()
        db.execute("SELECT * FROM reviews WHERE user_id = (?)",[session["user_id"]])
        movies = db.fetchall()
        ROOT = path.dirname(path.realpath(__file__))
        conn = sqlite3.connect(path.join(ROOT, "movies.db"))
        db = conn.cursor()
        tmpMovies = []
        for movie in movies:
            db.execute("SELECT * FROM movies WHERE id = (?)",[movie[2]])
            result = db.fetchall()
            tmpList = list(movie)
            tmpList.append(result[0][1])
            tmpList.append(result[0][2])
            tmpMovies.append(tmpList)
        return render_template("review.html", movies = tmpMovies)


@app.route("/list", methods=["GET","POST"])
def listRoute():
    if request.method == "POST":
        print(request.form)
        movieID = request.form.get("movieID")
        ROOT = path.dirname(path.realpath(__file__))
        conn = sqlite3.connect(path.join(ROOT, "users.db"))
        db = conn.cursor()
        listIDs = []
        numberLists = len(list(request.form))
        for i in range(1, numberLists):
            listIDs.append(list(request.form)[i])
        print(listIDs)
        for j in range(0,len(listIDs)):
            db.execute("INSERT INTO listEntries (list_id, user_id, movie_id) VALUES (?,?,?)", [request.form.get(listIDs[j]), session["user_id"], movieID])
            conn.commit()
        #db.execute("SELECT * FROM listEntries WHERE user_id = (?)", [session["user_id"]])
        db.execute("SELECT * FROM list WHERE user_id = (?)", [session["user_id"]])
        result = db.fetchall()
        finalList = []
        for i in range(0, len(result)):
            ROOT = path.dirname(path.realpath(__file__))
            conn = sqlite3.connect(path.join(ROOT, "users.db"))
            db = conn.cursor()
            db.execute("SELECT * FROM listEntries WHERE list_id = (?)",[result[i][0]])
            tmpList = list(db.fetchall())
            tmpList2 = []
            for entry in tmpList:
                ROOT = path.dirname(path.realpath(__file__))
                conn = sqlite3.connect(path.join(ROOT, "movies.db"))
                db = conn.cursor()
                db.execute("SELECT title FROM movies WHERE id = (?)",[entry[2]])
                tmp = list(entry)
                tmp.append(list(db.fetchall()[0])[0])
                tmpList2.append(tmp)
            finalList.append(tmpList2)
        print(finalList)
        for m in range(0, len(finalList)):
            if len(list(finalList)[m]) < 4:
                for n in range(len(finalList[m]) - 1, 3):
                    tmpList3 = ["","","",""]
                    tmpList4 = list(finalList)
                    tmpList4[m].append(tmpList3)
        print(result)
        return render_template("/list.html", results = result, finalList = finalList)
    if request.method == "GET":
        ROOT = path.dirname(path.realpath(__file__))
        conn = sqlite3.connect(path.join(ROOT, "users.db"))
        db = conn.cursor()
        db.execute("SELECT * FROM list WHERE user_id = (?)", [session["user_id"]])
        result = db.fetchall()
        finalList = []
        for i in range(0, len(result)):
            ROOT = path.dirname(path.realpath(__file__))
            conn = sqlite3.connect(path.join(ROOT, "users.db"))
            db = conn.cursor()
            db.execute("SELECT * FROM listEntries WHERE list_id = (?)",[result[i][0]])
            tmpList = list(db.fetchall())
            tmpList2 = []
            for entry in tmpList:
                ROOT = path.dirname(path.realpath(__file__))
                conn = sqlite3.connect(path.join(ROOT, "movies.db"))
                db = conn.cursor()
                db.execute("SELECT title FROM movies WHERE id = (?)",[entry[2]])
                tmp = list(entry)
                tmp.append(list(db.fetchall()[0])[0])
                tmpList2.append(tmp)
            finalList.append(tmpList2)
        print(finalList)
        for m in range(0, len(finalList)):
            if len(list(finalList)[m]) < 4:
                for n in range(len(list(finalList)[m]) - 1, 3):
                    tmpList3 = ["","","",""]
                    tmpList4 = list(finalList)
                    tmpList4[m].append(tmpList3)
        return render_template("/list.html", results = result, finalList = finalList)

@app.route("/list/<list_id>", methods=["GET","POST"])
def showMoviesinList(list_id):
    listID = list_id
    ROOT = path.dirname(path.realpath(__file__))
    conn = sqlite3.connect(path.join(ROOT, "users.db"))
    db = conn.cursor()
    db.execute("SELECT * FROM list WHERE user_id = (?) AND id = (?)", [session["user_id"],listID])
    result = db.fetchall()
    finalList = []
    for i in range(0, len(result)):
        ROOT = path.dirname(path.realpath(__file__))
        conn = sqlite3.connect(path.join(ROOT, "users.db"))
        db = conn.cursor()
        db.execute("SELECT * FROM listEntries WHERE list_id = (?)",[listID])
        tmpList = list(db.fetchall())
        tmpList2 = []
        for entry in tmpList:
            ROOT = path.dirname(path.realpath(__file__))
            conn = sqlite3.connect(path.join(ROOT, "movies.db"))
            db = conn.cursor()
            db.execute("SELECT title FROM movies WHERE id = (?)",[entry[2]])
            tmp = list(entry)
            tmp.append(list(db.fetchall()[0])[0])
            tmpList2.append(tmp)
        finalList.append(tmpList2)
    tmpList3 = []
    tmpLength = math.ceil(len(finalList[0]) / 4)
    frac, sth = math.modf(len(finalList[0]) / 4)
    frac = math.ceil((1 - frac) * 4)
    for l in range(0,tmpLength):
        tmpList3.append("")
    tmpList5 = list(finalList[0])
    for n in range(0, frac):
        tmpList4 = ["","","",""]
        tmpList5.append(tmpList4)
    return render_template("/listOverview.html",results = result, finalList = tmpList5, length = tmpList3)

@app.route("/list/new", methods = ["GET","POST"])
def newlist():
    if request.method == "GET":
        return render_template("newList.html")
    else:
        print(request.form)
        listname = request.form.get("listname")
        listdescription = request.form.get("description")
        ROOT = path.dirname(path.realpath(__file__))
        conn = sqlite3.connect(path.join(ROOT, "users.db"))
        db = conn.cursor()
        db.execute("INSERT INTO list (listname, description, user_id, moviecount) VALUES (?,?,?,?)",[listname, listdescription, session["user_id"],0])
        conn.commit()
        return render_template("newList.html")

@app.route("/actor/<actorname>", methods = ["GET","POST"])
def actor(actorname):
    ROOT = path.dirname(path.realpath(__file__))
    conn = sqlite3.connect(path.join(ROOT, "movies.db"))
    db = conn.cursor()
    db.execute("SELECT * FROM movies WHERE id in ( SELECT movie_id FROM stars WHERE person_id in ( SELECT id FROM people WHERE name LIKE (?)))",[actorname])
    movieList = db.fetchall()
    return render_template("actor.html", actorName = actorname, movies = movieList)