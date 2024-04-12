from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2

parser = reqparse.RequestParser()
parser.add_argument('title')
parser.add_argument('artist')

app = Flask("songs")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="songs", user="postgres", password="postgres", host="songs_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")


def all_songs(limit=1000):
    cur = conn.cursor()
    cur.execute(f"SELECT title, artist FROM songs LIMIT {limit};")
    return cur.fetchall()

def add_song(title, artist):
    if not song_exists(title, artist):
        cur = conn.cursor()
        cur.execute("INSERT INTO songs (title, artist) VALUES (%s, %s);", (title, artist))
        conn.commit()
        return True
    return False

def song_exists(title, artist):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM songs (WHERE title = %s AND artist = %s);", (title, artist))
    return bool(cur.fetchone()[0])  # Either True or False


def make_playlist(name, username):
    cur = conn.cursor()
    cur.execute("INSERT INTO playlists (name, username) VALUES (%s, %s);", (name, username))
    conn.commit()
    return True

def add_song_to_playlist(playlist_id, song_title, song_artist):
    cur = conn.cursor()
    cur.execute("INSERT INTO playlist_songs (playlist_id, title, artist) VALUES (%s, %s, %s);", (playlist_id, song_title, song_artist))
    conn.commit()
    return True

def get_user_playlists(username: str):
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM playlists WHERE username = %s;", (username,))
    return cur.fetchall()


def get_playlist_songs(playlist_id: int) -> list:
    cur = conn.cursor()
    cur.execute("SELECT title, artist FROM playlist_songs WHERE playlist_id = %s;", (playlist_id,))

    return cur.fetchall()

def playlist_exists(playlist_id: int) -> str:
    cur = conn.cursor()
    cur.execute("SELECT name FROM playlists WHERE id = %s", (playlist_id,))
    opl = cur.fetchone()
    if opl is None:
        return ""
    else:
        return opl[0]

class AllSongsResource(Resource):
    def get(self):
        return all_songs(), 200

class SongExists(Resource):
    def get(self):
        args = flask_request.args
        return song_exists(args['title'], args['artist']), 200

class AddSong(Resource):
    def put(self):
        args = flask_request.args
        return add_song(args['title'], args['artist']), 200

class PlaylistUser(Resource):
    def get(self, username: str):
        return get_user_playlists(username), 200

    def put(self, username):
        name = flask_request.form['name']
        return make_playlist(name, username), 200

class Playlist(Resource):
    def get(self, playlist_id: int):
        return get_playlist_songs(playlist_id), 200
    
    def put(self, playlist_id: int):
        song_title: str = flask_request.form['title']
        song_artist: str = flask_request.form['artist']
        return add_song_to_playlist(playlist_id, song_title, song_artist), 200

class Playlists(Resource):
    def post(self):
        playlist_id = int(flask_request.form['playlist_id'])
        return playlist_exists(playlist_id), 200


api.add_resource(AllSongsResource, '/songs/')
api.add_resource(SongExists, '/songs/exist/')
api.add_resource(AddSong, '/songs/add/')
api.add_resource(PlaylistUser, '/userplaylists/<string:username>/')
api.add_resource(Playlist, '/playlists/<int:playlist_id>/')
api.add_resource(Playlists, '/playlists/')

