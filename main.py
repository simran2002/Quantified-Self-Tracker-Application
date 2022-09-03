from flask import Flask, url_for, request, render_template, redirect
from models import Users, Trackers, Logs, users_trackers, trackers_logs, db, mcq_options
from werkzeug.security import generate_password_hash, check_password_hash

'''Users = models.Users()
Trackers = models.Trackers
Logs = models.Logs
users_trackers = models.users_trackers
trackers_logs = models.trackers_logs'''

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///trackers.db"
db.init_app(app)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        temp = Users.query.filter_by(name=username).first()
        temp1 = Users.query.filter_by(email = email).first()
        if temp == None and temp1 == None:
            password1 = request.form.get("password1")
            password2 = request.form.get("password2")

            if password1 == password2:
                password = generate_password_hash(password1)
                new = Users(name=username, email = email, password=password)
                db.session.add(new)
                db.session.commit()
            else:
                return render_template("signup.html", msg="Both passwords do not match. Try Again!!!")
        else:
            return render_template("signup.html", msg="User with this username already exists. Try another one!!!")
    else:
        return render_template("signup.html", msg="")
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        record = Users.query.filter_by(name=username).first()
        passw = record.password

        if record != None:
            if check_password_hash(passw, password):
                return redirect(url_for('home', userid=record.id))
            else:
                return render_template('login.html', msg="Incorrect password...")
        else:
            return render_template('signup.html', msg="User with this username does not exist. Sign-up for new user...")

    elif request.method == 'GET':
        return render_template('login.html')
    else:
        return render_template('signup.html')


@app.route("/logout/<int:userid>", methods=["GET", "POST"])
def logout(userid):
    return render_template('login.html', msg="Current user logged out successfully!!!")


@app.route("/home/<int:userid>", methods=["GET", "POST"])
def home(userid):
    user_record = Users.query.filter_by(id=userid).first()
    u_t = users_trackers.query.filter_by(user_id=userid).all()
    tracker_record = []
    for i in u_t:
        temp = Trackers.query.filter_by(id=i.tracker_id).first()
        tracker_record.append(temp)
    return render_template("home.html", Tracker=tracker_record, User=user_record)


@app.route("/add_tracker/<int:userid>", methods=["GET", "POST"])
def add_tracker(userid):
    if request.method == "POST":
        name = request.form.get("name")
        desc = request.form.get("description")
        type = request.form.get("type")
        new1 = Trackers(name=name, description=desc, type=type)
        db.session.add(new1)
        db.session.commit()
        trackerid = new1.id

        new = users_trackers(user_id=userid, tracker_id=trackerid)
        db.session.add(new)
        db.session.commit()
        if (type == 'multiple'):
            return redirect(url_for('add_mcq', trackerid=trackerid, userid=userid))
        else:
            return redirect(url_for("home", userid=userid))

    elif request.method == "GET":
        return render_template('add_tracker.html', userid=userid)

    else:
        return redirect(url_for("home", userid=userid))


@app.route("/add_mcq/<int:trackerid>/<int:userid>", methods=["GET", "POST"])
def add_mcq(trackerid, userid):
    tracker_rec = Trackers.query.filter_by(id = trackerid).first()
    if request.method == "POST":
        options = request.form.get("options")
        mcqObj = mcq_options(tracker_id=trackerid, options=options)
        db.session.add(mcqObj)
        db.session.commit()
    elif request.method == "GET":
        return render_template('multiple_choice.html', tracker=tracker_rec, userid=userid)
    return redirect(url_for("home", userid=userid))


@app.route("/edit_tracker/<int:trackerid>", methods=["GET", "POST"])
def edit_tracker(trackerid):
    tracker_record = Trackers.query.filter_by(id=trackerid).first()
    userid = users_trackers.query.filter_by(
        tracker_id=tracker_record.id).first().user_id

    if request.method == "POST":
        name = request.form.get("name")
        desc = request.form.get("description")
        type = request.form.get("type")
        tracker_record.name = name
        tracker_record.description = desc
        tracker_record.type = type
        db.session.commit()
        return redirect(url_for("home", userid=userid))
    elif request.method == "GET":
        return render_template("edit_tracker.html", Tracker=tracker_record, userid = userid)
    else:
        return render_template("home.html", User=(Users.query.filter_by(id=userid).first()), Tracker=tracker_record)


@app.route("/delete_tracker/<int:trackerid>", methods=["GET", "POST"])
def delete_tracker(trackerid):
    temp = users_trackers.query.filter_by(tracker_id=trackerid).all()
    userid = temp[0].user_id
    for i in temp:
        db.session.delete(i)
    temp = trackers_logs.query.filter_by(tracker_id=trackerid).all()

    if len(temp) != 0:
        for i in temp:
            logs = trackers_logs.query.filter_by(log_id=i.log_id).all()
            if len(logs) != 0:
                for j in logs:
                    db.session.delete(j)
            db.session.delete(i)
    tracker = Trackers.query.filter_by(id=trackerid).first()
    db.session.delete(tracker)
    db.session.commit()
    return redirect(url_for("home", userid=userid))


@app.route("/add_log/<int:trackerid>", methods=["GET", "POST"])
def add_log(trackerid):
    tracker_render = Trackers.query.filter_by(id=trackerid).first()
    userid = users_trackers.query.filter_by(
        tracker_id=tracker_render.id).first().user_id
    trackertype = Trackers.query.filter_by(id=trackerid).first().type

    from datetime import datetime
    if request.method == "POST":
        val = request.form.get("value")
        note = request.form.get("note")
        timestamp = str(datetime.now())

        new = Logs(value=val, note=note, timestamp=timestamp)
        db.session.add(new)
        db.session.commit()
        logid = new.id

        new = trackers_logs(tracker_id=trackerid, log_id=logid)
        db.session.add(new)
        db.session.commit()
        return redirect(url_for("home", userid=userid))

    elif request.method == "GET":

        if trackertype == "multiple":
            options = mcq_options.query.filter_by(
                tracker_id=trackerid).first().options
            options = options.split(",")
            return render_template("add_log.html", Tracker=tracker_render, mcq=options, userid = userid)
        else:
            return render_template("add_log.html", Tracker=tracker_render, mcq=False, userid = userid)


@app.route("/edit_log/<int:logid>", methods=["GET", "POST"])
def edit_log(logid):
    # fetching log record for updation
    log = Logs.query.filter_by(id=logid).first()
    # fetching tracker log record for tracker id
    trackerid = trackers_logs.query.filter_by(log_id=logid).first().tracker_id
    tracker_record = Trackers.query.filter_by(id=trackerid).first()
    userid = users_trackers.query.filter_by(
        tracker_id=tracker_record.id).first().user_id
    user = Users.query.filter_by(id=userid).first()

    u_t = users_trackers.query.filter_by(user_id=userid).all()
    tracker_records = []
    for i in u_t:
        temp = Trackers.query.filter_by(id=i.tracker_id).first()
        tracker_records.append(temp)

    from datetime import datetime

    if request.method == "POST":
        val = request.form.get("value")
        note = request.form.get("note")
        timestamp = str(datetime.now())

        log.value = val
        log.note = note
        log.timestamp = timestamp

        db.session.commit()
        return render_template("home.html", User=user, Tracker=tracker_records)

    elif request.method == "GET":
        options = []
        if (tracker_record.type == "multiple"):
            options = mcq_options.query.filter_by(
                tracker_id=trackerid).first().options
            options = options.split(",")
        return render_template("edit_log.html", Log=log, tracker=tracker_record, mcq=options, userid =userid)


@app.route("/delete_log/<int:logid>", methods=["GET", "POST"])
def delete_log(logid):
    trac_log_rec = trackers_logs.query.filter_by(log_id=logid).all()
    trackerid = trac_log_rec[0].tracker_id
    userid = users_trackers.query.filter_by(
        tracker_id=trackerid).first().user_id

    for record in trac_log_rec:
        db.session.delete(record)

    log = Logs.query.filter_by(id=logid).first()
    db.session.delete(log)
    db.session.commit()

    return redirect(url_for('display', trackerid = trackerid, userid=userid))


@app.route("/display/<int:trackerid>", methods=["GET", "POST"])
def display(trackerid):
    """tracker = Trackers.query.filter_by(id = trackerid).first()
    temp = trackers_logs.query.filter_by(tracker_id = trackerid).all()

    logs = []

    for record in temp:
      logs.append(Logs.query.filter_by(id = record.log_id).first())
    val = []
    time = []
    if logs != None:
      for i in logs:
          val.append(i.value)
          time.append(i.timestamp)



    plt.plot(time, val)
    plt.xlabel('Timestamp')
    plt.ylabel('Values')

    plt.savefig('static/graph.jpg')
    return render_template("display.html", Tracker = tracker, logs = logs)"""
    import matplotlib.pyplot as plt
    plt.switch_backend('Agg')
    logs = []
    values = []
    timestamps = []

    tracker = Trackers.query.filter_by(id=trackerid).first()
    userid = users_trackers.query.filter_by(
        tracker_id=trackerid).first().user_id
    user = Users.query.filter_by(id=userid).first()
    intermediate_logs = trackers_logs.query.filter_by(
        tracker_id=trackerid).all()

    for i in intermediate_logs:
        tracker_logs = Logs.query.filter_by(id=i.log_id).first()
        logs.append(tracker_logs)
    for j in logs:
        values.append(j.value)
        timestamps.append(j.timestamp)
    plot = plt.figure()
    plt.bar(timestamps, values)
    plt.ylabel('Values')
    plt.xlabel('Timestamp')
    plot.savefig('static/graph.jpg')
    return render_template("display.html", Tracker=tracker, Log=logs, User=user)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
