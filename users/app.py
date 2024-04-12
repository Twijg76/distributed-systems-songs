from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2
from flask import request
from flask_restful import reqparse
import requests


app = Flask("users")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="users", user="postgres", password="postgres", host="users_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")

def new_user(username, password):
    if not user_exists(username):
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s);", (username, password))
        conn.commit()
        return True
    return False

def user_exists(username):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE username = %s;", (username,))
    return bool(cur.fetchone()[0])  # Either True or False

def login_user(username, password):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE username = %s AND password = %s;", (username, password))
    return bool(cur.fetchone()[0])  # Either True or False



class User(Resource):
    def get(self, username):
        return user_exists(username)

class LoginUser(Resource):
    def post(self):
        username = request.form['username']
        password = request.form['password']
        return login_user(username, password), 201

class AddUser(Resource):
    def put(self):
        username = request.form['username']
        password = request.form['password']
        return new_user(username, password), 201

api.add_resource(User, '/users/<string:username>/')
api.add_resource(AddUser, '/users/add/')
api.add_resource(LoginUser, '/users/login/')

