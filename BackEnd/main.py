from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text

app = Flask(__name__)

# MySQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Ironhulkkichu135*@localhost/social_media_analytics'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Database Models
class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    age = db.Column(db.Integer)
    location = db.Column(db.String(100))
    joined_date = db.Column(db.DateTime)

class Posts(db.Model):
    post_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    likes_count = db.Column(db.Integer, default=0)
    shares_count = db.Column(db.Integer, default=0)

class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    comment_text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)

class Hashtags(db.Model):
    hashtag_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'))
    hashtag = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime)

class Top5(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), unique=True)
    rank = db.Column(db.Integer)

# CREATE API - Populate top_5 table
@app.route('/top5/create', methods=['POST'])
def create_top5():
    query = text("""
        SELECT posts.post_id, 
               (posts.likes_count + posts.shares_count + 
               (SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.post_id) + 
               (SELECT COUNT(*) FROM hashtags WHERE hashtags.post_id = posts.post_id)) AS engagement
        FROM posts
        ORDER BY engagement DESC
        LIMIT 5
    """)
    top_posts = db.session.execute(query).fetchall()

    # Clear existing data
    db.session.query(Top5).delete()

    # Insert new top 5
    for idx, row in enumerate(top_posts, start=1):
        post_id = row[0]
        new_entry = Top5(post_id=post_id, rank=idx)
        db.session.add(new_entry)

    db.session.commit()
    return jsonify({'message': 'Top 5 posts updated'}), 201

# READ API - Get top 5 posts based on engagement
@app.route('/top5/read', methods=['GET'])
def read_top5():
    query = text("""
        SELECT posts.post_id, posts.content, posts.likes_count, posts.shares_count
        FROM posts
        ORDER BY (posts.likes_count + posts.shares_count + 
                  (SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.post_id) + 
                  (SELECT COUNT(*) FROM hashtags WHERE hashtags.post_id = posts.post_id)) DESC
        LIMIT 5
    """)
    top_posts = db.session.execute(query).fetchall()

    result = [{'post_id': row[0], 'content': row[1], 'likes': row[2], 'shares': row[3]} for row in top_posts]
    return jsonify(result)

# UPDATE API - Recalculate top 5 when a new post, comment, or hashtag is added
@app.route('/top5/update', methods=['PUT'])
def update_top5():
    return create_top5()  # Re-run the logic

# DELETE API - Update rankings when a comment or hashtag is deleted
@app.route('/top5/delete', methods=['DELETE'])
def delete_top5_entry():
    return create_top5()  # Re-run the logic

if __name__ == '__main__':
    print("🔹 Starting Flask server...")
    with app.app_context():
        db.create_all()  # Ensure database tables are created
    print("🔹 Database checked. Running Flask now...")
    app.run(debug=True,port=5001,ssl_context=None)
