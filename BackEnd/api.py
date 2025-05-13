from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text  # Import text() for raw SQL queries

import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Database Configuration (PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Advaith007@localhost/social_media_analytics'
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
    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)
    likes_count = db.Column(db.Integer, default=0)
    shares_count = db.Column(db.Integer, default=0)

class Comments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

# CREATE POST API
@app.route('/posts/create', methods=['POST'])
def create_post():
    data = request.get_json()
    new_post = Posts(user_id=data['user_id'], content=data['content'])
    db.session.add(new_post)
    db.session.commit()
    return jsonify({'message': 'Post created successfully', 'post_id': new_post.post_id}), 201

# LIKE POST API
@app.route('/like', methods=['POST'])
def like_post():
    data = request.get_json()
    post = Posts.query.get(data['post_id'])
    if post:
        post.likes_count += 1
        db.session.commit()
        return jsonify({'message': 'Post liked', 'likes_count': post.likes_count}), 200
    return jsonify({'error': 'Post not found'}), 404

# SHARE POST API
@app.route('/share', methods=['POST'])
def share_post():
    data = request.get_json()
    post = Posts.query.get(data['post_id'])
    if post:
        post.shares_count += 1
        db.session.commit()
        return jsonify({'message': 'Post shared', 'shares_count': post.shares_count}), 200
    return jsonify({'error': 'Post not found'}), 404

# ADD COMMENT API
@app.route('/comment', methods=['POST'])
def add_comment():
    data = request.get_json()
    new_comment = Comments(post_id=data['post_id'], user_id=data['user_id'], comment_text=data['comment_text'])
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({'message': 'Comment added successfully', 'comment_id': new_comment.comment_id}), 201

# DELETE COMMENT API
@app.route('/comment/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment = Comments.query.get(comment_id)
    if comment:
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'message': 'Comment deleted successfully'}), 200
    return jsonify({'error': 'Comment not found'}), 404

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
    for idx, (post_id, _) in enumerate(top_posts, start=1):
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

    result = [{'post_id': post[0], 'content': post[1], 'likes': post[2], 'shares': post[3]} for post in top_posts]
    return jsonify(result)

# UPDATE API - Recalculate top 5 when a new post, comment, or hashtag is added
@app.route('/top5/update', methods=['PUT'])
def update_top5():
    return create_top5()  # Re-run the logic

# DELETE API - Update rankings when a comment or hashtag is deleted
@app.route('/top5/delete', methods=['DELETE'])
def delete_top5_entry():
    return create_top5()  # Re-run the logic

@app.route('/')
def home():
    return '''
    <html>
    <head>
        <title>API Home</title>
    </head>
    <body>
        <h1>Welcome to the Social Media Analytics API</h1>
        <p>Click the button below to view the Top 5 Posts.</p>
        <button onclick="window.location.href='/top5/read';">
            View Top 5 Posts
        </button>
    </body>
    </html>
    '''

from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')

@app.route('/top5/comments/sentiment', methods=['GET'])
def top5_comments_sentiment():
    # Step 1: Get top 5 posts
    top5_query = text("""
        SELECT posts.post_id, posts.content
        FROM posts
        ORDER BY (posts.likes_count + posts.shares_count + 
                  (SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.post_id) + 
                  (SELECT COUNT(*) FROM hashtags WHERE hashtags.post_id = posts.post_id)) DESC
        LIMIT 5
    """)
    top_posts = db.session.execute(top5_query).fetchall()

    sia = SentimentIntensityAnalyzer()
    results = []

    for post in top_posts:
        post_id, content = post

        # Step 2: Get top 3 comments for each post (by latest timestamp)
        comments_query = text("""
            SELECT comment_id, comment_text, timestamp 
            FROM comments 
            WHERE post_id = :post_id
            ORDER BY timestamp DESC
            LIMIT 3
        """)
        comments = db.session.execute(comments_query, {'post_id': post_id}).fetchall()

        # Step 3: Sentiment analysis on each comment
        comment_results = []
        for comment in comments:
            comment_id, comment_text, timestamp = comment
            score = sia.polarity_scores(comment_text)
            compound = score['compound']

            if compound >= 0.05:
                label = 'Positive'
            elif compound <= -0.05:
                label = 'Negative'
            else:
                label = 'Neutral'

            comment_results.append({
                'comment_id': comment_id,
                'text': comment_text,
                'timestamp': str(timestamp),
                'sentiment_score': score,
                'sentiment_label': label
            })

        results.append({
            'post_id': post_id,
            'post_content': content,
            'top_comments': comment_results
        })

    return jsonify(results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True, port=5001)

