from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow


# from flask_heroku import Heroku
# from flask_cors import CORS
# from dotenv import load_dotenv
import os

# load_dotenv()

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)
# heroku = Heroku(app)
# CORS(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, unique=False, nullable=False)

    def __init__(self, username, password):
        self.username = username
        self.password = password

class UserSchema(ma.Schema):
    class Meta:
        fields =("id", "username")

user_schema = UserSchema()
multiple_user_schema = UserSchema(many=True)


class Workout(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    exercise = db.Column(db.String, nullable=False)
    muscle_group = db.Column(db.String, nullable=False)
    equiptment = db.Column(db.String, nullable=False)

    
    def __init__(self, exercise, muscle_group, equiptment):
        self.exercise = exercise
        self.muscle_group = muscle_group
        self.equiptment = equiptment

class WorkoutSchema(ma.Schema):
    class Meta:
        fields = ("id", "exercise", "muscle_group", "equiptment")

workout_schema = WorkoutSchema()
multiple_workout_schema = WorkoutSchema(many=True)

# User Endpoints

@app.route("/user/add", methods=["POST"])
def add_user():
    if request.content_type != "application/json":
        return "Error: Data must be sent as JSON."

    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")

    possible_duplicate = db.session.query(User).filter(User.username == username).first()
    if possible_duplicate is not None:
        return jsonify("Error: choose another username")


    record = User(username, password)
    db.session.add(record)
    db.session.commit()

    return jsonify("User Added")

@app.route("/user/get", methods=["GET"])
def get_all_users():
    all_users = db.session.query(User).all()
    return jsonify(multiple_user_schema.dump(all_users))

# Workout Endpoints 
@app.route("/workout/add", methods=["POST"])
def add_workout():
    if request.content_type != "application/json":
        return "Error: Data must be sent as JSON."
    
    post_data = request.get_json()
    exercise = post_data.get("exercise")
    muscle_group = post_data.get("muscle_group")
    equiptment = post_data.get("equiptment")

    record = Workout(exercise, muscle_group, equiptment)
    db.session.add(record)
    db.session.commit()

    return jsonify("Workout Added Successfully")

@app.route("/workout/add/multiple", methods=["POST"])
def add_multiple_workouts():
    if request.content_type != "application/json":
        return jsonify("Error: Data must be sent as JSON.")

    post_data = request.get_json()
    for workout in post_data:
        record = Workout(workout["exercise"], workout["muscle_group"], workout["equiptment"])
        db.session.add(record)
    
    db.session.commit()

    return jsonify("All workouts added")


@app.route("/workout/get", methods=["GET"])
def get_all_workouts():

    all_workouts = db.session.query(Workout).all()
    return jsonify(multiple_workout_schema.dump(all_workouts))

@app.route("/workout/delete/<id>", methods=["DELETE"])
def delete_workouts_by_id(id):
    workout = db.session.query(Workout).filter(Workout.id == id).first()
    db.session.delete(workout)
    db.session.commit()
    return jsonify("Workout Deleted")


if __name__ == "__main__":
    app.run(debug=True)