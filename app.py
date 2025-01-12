from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
import random

app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///local.db'  
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

IMAGE_FOLDER = "static/"

# Database Model
class Move(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    elo = db.Column(db.String(15), nullable=False)
    user_guess = db.Column(db.String(50), nullable=False)
    correct_answer = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'elo': self.elo,
            'user_guess': self.user_guess,
            'correct_answer': self.correct_answer,
            'timestamp': self.timestamp.isoformat()
        }

def get_random_move():
    images = [f for f in os.listdir(IMAGE_FOLDER) if f.endswith('.png')]
    images.sort()
    move_id = random.randint(0, len(images)-1)
    img = images[move_id]
    if "after" in img.lower():
        img_after = img
        img_before = images[move_id+1]
    else:
        img_before = img
        img_after = images[move_id-1]
    
    return img_before, img_after

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/game', methods=['POST'])
def game():
    elo = request.form.get("elo")  
    before_img, after_img = get_random_move()
    
    return render_template("game.html", elo=elo, before_img=before_img, after_img=after_img)


@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        
       
        user_guess = data["user_guess"]
        image_type = data["image_type"]  
        correct_answer = user_guess == image_type
        
        new_move = Move(
            elo=data["elo"], 
            user_guess=user_guess,
            correct_answer=correct_answer
        )
        
        db.session.add(new_move)
        db.session.commit()
        
   
        before_img, after_img = get_random_move()
        
        return jsonify({
            "status": "success",
            "before_img": before_img,
            "after_img": after_img
        })
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in submit: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/about')
def about():
    return render_template('about.html')
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(host='0.0.0.0', port=port)