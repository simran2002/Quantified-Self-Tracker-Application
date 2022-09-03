from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    email = db.column(db.String)
    name = db.Column(db.String)
    password = db.Column(db.String)

class Trackers(db.Model):
  __tablename__ = "Trackers"
  id = db.Column(db.Integer, primary_key = True, autoincrement = True)
  name = db.Column(db.String)
  description = db.Column(db.String)
  type = db.Column(db.String)

class Logs(db.Model):
  __tablename__ = "Logs"
  id = db.Column(db.Integer, primary_key = True, autoincrement = True)
  value = db.Column(db.String)
  timestamp = db.Column(db.String)
  note = db.Column(db.String)
  
class users_trackers(db.Model):
  id = db.Column(db.Integer, autoincrement = True, primary_key = True)
  user_id = db.Column(db.String, db.ForeignKey("Users.id"))
  tracker_id = db.Column(db.String, db.ForeignKey("Trackers.id"))

class trackers_logs(db.Model):
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  log_id = db.Column(db.String, db.ForeignKey("Logs.id"))
  tracker_id = db.Column(db.String, db.ForeignKey("Trackers.id"))

class mcq_options(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tracker_id = db.Column(db.String, db.ForeignKey("Trackers.id"))
    options = db.Column(db.String)