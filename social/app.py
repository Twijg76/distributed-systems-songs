from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2
from flask import request
import requests

parser = reqparse.RequestParser()
parser.add_argument('username')

app = Flask("social")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="social", user="postgres", password="postgres", host="social_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")


def add_friend(username: str, friendname: str) -> bool:
    antwoord = requests.get("http://users:5000/users/" + friendname)
    if antwoord.status_code == 200 or antwoord.status_code == 201:
        if antwoord.json() == True:
            pass
        else:
            return False
    else:
        return False
    if not are_friends(username, friendname):
        cur = conn.cursor()
        cur.execute("INSERT INTO friends (username, friend) VALUES (%s, %s);", (username, friendname))
        conn.commit()
        add_event_to_feed(username, "added " + friendname + " as a friend")
        return True
    return False

def are_friends(username: str, friendname: str) -> bool:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM friends WHERE username = %s AND friend = %s;", (username, friendname))
    return bool(cur.fetchone()[0])

def add_event_to_feed(username: str, event: str) -> bool:
    cur = conn.cursor()
    # add user, time, event
    cur.execute("INSERT INTO feed (username, time, post) VALUES (%s, NOW(), %s);", (username, event))
    conn.commit()
    return True

def get_feed(username: str, limit: int) -> list:
    cur = conn.cursor()
    # select all feinds and their events
    cur.execute("SELECT f.time, f.post, f.username from feed f JOIN friends fr on f.username = fr.friend WHERE fr.username = %s ORDER BY f.time DESC LIMIT %s;", (username, str(limit)))
    result = cur.fetchall()
    out = []
    if result is None:
        return []
    for row in result:
        out.append([row[0].strftime("%Y-%m-%d %H:%M:%S"), row[1], row[2]])

    return out

def get_friends(username: str) -> list:
    cur = conn.cursor()
    cur.execute("SELECT friend FROM friends WHERE username = %s;", (username,))
    result = cur.fetchall()
    out = []
    for row in result:
        out.append(row[0])
    return out

def share_playlist(playlist_id: int, username: str, friendname: str) -> bool:
    antwoord = requests.post("http://songs:5000/playlists/", data={"playlist_id": playlist_id})
    print(antwoord, flush=True)
    playlist_name = ""
    if antwoord.status_code == 200 or antwoord.status_code == 201:
        if antwoord != "":
            playlist_name = antwoord.json()
            print(playlist_name, flush=True)
        else:
            return False
    else:
        return False
    cur = conn.cursor()
    cur.execute("INSERT INTO shared_playlists (friendname, playlist_id) VALUES (%s, %s);", (friendname, playlist_id))
    cur.execute("INSERT INTO feed (username, time, post) VALUES (%s, NOW(), %s);", (username, "shared playlist " + playlist_name + " with " + friendname))
    return True

def get_shared_playlists(username: str) -> list:
    cur = conn.cursor()
    cur.execute("SELECT playlist_id FROM shared_playlists WHERE friendname = %s;", (username,))
    result = cur.fetchall()
    out = []
    for row in result:
        name = requests.post("http://songs:5000/playlists/", data={"playlist_id": row[0]})
        out.append([row[0], name.json()])
    print(out, flush=True)
    return out

    

class Feed(Resource):
    def post(self, username):
        limit = request.form['limit']
        return get_feed(username, int(limit)), 201
    def put(self, username):
        event = request.form['event']
        return add_event_to_feed(username, event), 201

class Friends(Resource):
    def get(self, username):
        return get_friends(username)
    def post(self, username):
        friendname = request.form['friendname']
        return add_friend(username, friendname), 200

class SharedPlaylists(Resource):
    def get(self, username):
        return get_shared_playlists(username), 200

class SharePlaylist(Resource):
    def post(self):
        friendname = request.form['friendname']
        username = request.form['username']
        playlist_id = int(request.form['playlist_id'])
        return share_playlist(playlist_id, username, friendname), 200

api.add_resource(Feed, '/social/feed/<string:username>')
api.add_resource(Friends, '/social/friends/<string:username>')
api.add_resource(SharedPlaylists, '/social/shared_playlists/<string:username>')
api.add_resource(SharePlaylist, '/social/share_playlist/')


