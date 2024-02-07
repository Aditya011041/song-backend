from flask import Flask, jsonify, render_template, request, redirect, url_for
from ytmusicapi import YTMusic
import pymongo
import requests

app = Flask(__name__)

# Initialize YTMusic API
yt = YTMusic('oauth.json')

# Connect to MongoDB
client = pymongo.MongoClient("mongodb+srv://adityaece20043:Aditya0101@<cluster>/<database>?retryWrites=true&w=majority")
db = client["myplaylist"]

# Create collection (equivalent to table in SQL)
songs_collection = db["songs"]

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    search_results = yt.search(query)
    top_5_results = search_results[:6]  # Slice to get only the top 5 results
    return render_template('results.html', results=top_5_results)

@app.route('/add_to_playlist', methods=['POST'])
def add_to_playlist():
    video_id = request.form['video_id']
    title = request.form['title']
    gaana_url = request.form['gaana_url']
    
    # Fetch MP3 link from Gaana API
    response = requests.get(f'http://127.0.0.1:8080/result/?url={gaana_url}')
    if response.status_code == 200:
        song_data = response.json()
        mp3_link = song_data.get('link')
    else:
        mp3_link = None
    
    # Insert song into MongoDB
    songs_collection.insert_one({"title": title, "video_id": video_id, "mp3_link": mp3_link})
    
    return redirect(url_for('index'))

@app.route('/saved_songs')
def saved_songs():
    songs = list(songs_collection.find())
    return render_template('saved_songs.html', songs=songs)

@app.route('/remove_from_playlist/<song_id>', methods=['POST'])
def remove_from_playlist(song_id):
    # Remove song from MongoDB
    songs_collection.delete_one({"_id": ObjectId(song_id)})
    return redirect(url_for('saved_songs'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
