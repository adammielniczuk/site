from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import json
import random

app = Flask(__name__)

# Define paths
IMAGE_FOLDER = "static/"
DATA_FILE = "data/moves.json"

# Load or initialize the JSON data file
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

# Helper function to load images
def get_random_move():
    images = [f for f in os.listdir(IMAGE_FOLDER) if f.endswith('.png')]
    images.sort()
    move_id = random.randint(0,len(images)-1)
    img = images[move_id]
    if "after" in img.lower():
        img_after = img
        img_before = images[move_id+1]
    else:
        img_before = img
        img_after = images[move_id-1]
  
    return img_before, img_after

# Home page route
@app.route('/')
def index():
    return render_template("index.html")

# Game route
@app.route('/game', methods=['POST'])
def game():
    elo = request.form.get("elo")
    before_img, after_img= get_random_move()

    return render_template("game.html", elo=elo, before_img=before_img, after_img=after_img)

# Save result route
@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    elo = data["elo"]
    user_guess = data["user_guess"]
    correct_answer = data["correct"]

    with open(DATA_FILE, 'r') as f:
        moves_data = json.load(f)

    # Append new data
    moves_data.append({
        "elo": elo,
        "user_guess": user_guess,
        "correct_answer": correct_answer
    })

    with open(DATA_FILE, 'w') as f:
        json.dump(moves_data, f, indent=4)

    # Get new images for the next question
    before_img, after_img = get_random_move()
    return jsonify({
        "before_img": before_img,
        "after_img": after_img
        })

if __name__ == "__main__":
    app.run(debug=True)