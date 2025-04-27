from flask import Flask, request, jsonify,render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text  # Import text() for raw SQL queries
from datetime import datetime
from flask_cors import CORS
from sqlalchemy.sql import text
from sqlalchemy import func
from flask_cors import CORS
from sqlalchemy import and_, func, Date, cast
from sqlalchemy.orm import aliased
from datetime import datetime, timedelta


app = Flask(__name__)
CORS(app)


import logging
logging.basicConfig(level=logging.DEBUG)



# Database Configuration (PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/social_media_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class SentimentAnalysis(db.Model):
    __tablename__ = 'sentiment_analysis'
    
    post_id = db.Column(db.Integer, db.ForeignKey('posts.post_id'), primary_key=True)
    sentiment_score = db.Column(db.Float)
    category = db.Column(db.String(50))


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

@app.route('/')
def home():
    routes = [
        ("/static/<path:filename>", "Static Files"),
        ("/posts/create", "Create Post"),
        ("/like", "Like Post"),
        ("/share", "Share Post"),
        ("/comment", "Add Comment"),
        ("/comment/<int:comment_id>", "Delete Comment"),
        ("/top5/create", "Create Top 5"),
        ("/top5/update", "Update Top 5"),
        ("/top5/delete", "Delete Top 5"),
        ("/engagement/timeline", "Engagement Timeline"),
        ("/top5/sentiment/posts", "Sentiment for Top 5 Posts"),
        ("/recent/posts", "Recent Posts"),
        ("/top5/users", "Top 5 Users"),
        ("/top5/read", "Read Top 5")
        
    ]
    return render_template('home.html', routes=routes)


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

#Engagement
@app.route('/engagement/timeline', methods=['GET'])
def engagement_timeline():
    query = text("""
        WITH post_engagement AS (
            SELECT DATE(timestamp) AS date,
                   SUM(likes_count) AS total_likes,
                   SUM(shares_count) AS total_shares
            FROM posts
            GROUP BY DATE(timestamp)
        ),
        comment_engagement AS (
            SELECT DATE(timestamp) AS date,
                   COUNT(*) AS total_comments
            FROM comments
            GROUP BY DATE(timestamp)
        ),
        hashtag_engagement AS (
            SELECT DATE(timestamp) AS date,
                   COUNT(*) AS total_hashtags
            FROM hashtags
            GROUP BY DATE(timestamp)
        )
        SELECT 
            p.date,
            COALESCE(p.total_likes, 0) + 
            COALESCE(p.total_shares, 0) + 
            COALESCE(c.total_comments, 0) + 
            COALESCE(h.total_hashtags, 0) AS engagement
        FROM post_engagement p
        LEFT JOIN comment_engagement c ON p.date = c.date
        LEFT JOIN hashtag_engagement h ON p.date = h.date
        ORDER BY p.date
    """)
    
    result = db.session.execute(query).fetchall()
    timeline = [{"date": str(row[0]), "engagement": int(row[1])} for row in result]
    total_engagement = sum(item["engagement"] for item in timeline)
    
    return jsonify({
        "timeline": timeline,
        "total_engagement": total_engagement
    })


#Get Sentiment Analysis
from sqlalchemy import text, func

@app.route('/top5/sentiment/posts', methods=['GET'])
def get_top5_post_sentiments():
    # Step 1: Get top 5 posts based on total engagement (likes + shares + comments)
    top_posts = db.session.execute(text("""
        SELECT 
            p.post_id,
            p.content,
            (p.likes_count + p.shares_count + COALESCE(c.comment_count, 0)) AS engagement
        FROM posts p
        LEFT JOIN (
            SELECT post_id, COUNT(*) AS comment_count
            FROM comments
            GROUP BY post_id
        ) c ON p.post_id = c.post_id
        ORDER BY engagement DESC
        LIMIT 5
    """)).fetchall()

    post_ids = [row.post_id for row in top_posts]

    # Step 2: Get sentiment scores for these posts
    sentiment_data = db.session.query(
        SentimentAnalysis.post_id,
        SentimentAnalysis.category,
        func.avg(SentimentAnalysis.sentiment_score).label("avg_score")
    ).filter(SentimentAnalysis.post_id.in_(post_ids))\
     .group_by(SentimentAnalysis.post_id, SentimentAnalysis.category).all()

    # Step 3: Structure the response
    sentiment_map = {}
    for row in sentiment_data:
        if row.post_id not in sentiment_map:
            sentiment_map[row.post_id] = {}
        sentiment_map[row.post_id][row.category.lower()] = round(row.avg_score, 2)

    response = []
    for row in top_posts:
        sentiments = sentiment_map.get(row.post_id, {})
        response.append({
            "post_id": row.post_id,
            "content": row.content,
            "sentiments": {
                "positive": sentiments.get("positive", 0),
                "neutral": sentiments.get("neutral", 0),
                "negative": sentiments.get("negative", 0)
            }
        })

    return jsonify(response)

#Get user details of a user
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    query = text("SELECT name FROM users WHERE user_id = :user_id")
    result = db.session.execute(query, {'user_id': user_id}).fetchone()
    if result:
        return jsonify({"name": result[0]})
    return jsonify({"error": "User not found"}), 404

#Get Recent Posts
@app.route('/recent/posts',methods=['GET'])
def get_recent_posts():
    query = text("""
        SELECT p.post_id, p.content, p.timestamp, u.name AS username
        FROM posts p
        JOIN users u ON p.user_id = u.user_id
        ORDER BY p.timestamp DESC
        LIMIT 5
    """)

    result = db.session.execute(query)
    
    posts = [
        {
            "post_id": row.post_id,
            "content": row.content,
            "timestamp": row.timestamp.strftime("%Y-%m-%d %H:%M"),
            "username": row.username
        }
        for row in result
    ]
    return jsonify(posts)

#Get top 5 Users based on engagement
@app.route('/top5/users',methods=['GET'])
def get_top_users():
    query = text("""
        SELECT 
            u.user_id,
            u.name,
            COALESCE(SUM(p.likes_count), 0) AS total_likes,
            COALESCE(SUM(p.shares_count), 0) AS total_shares,
            COALESCE(COUNT(c.comment_id), 0) AS total_comments,
            COALESCE(SUM(p.likes_count), 0) + COALESCE(SUM(p.shares_count), 0) + COALESCE(COUNT(c.comment_id), 0) AS total_engagement
        FROM users u
        LEFT JOIN posts p ON u.user_id = p.user_id
        LEFT JOIN comments c ON p.post_id = c.post_id
        GROUP BY u.user_id, u.name
        ORDER BY total_engagement DESC
        LIMIT 5;
    """)

    result = db.session.execute(query).fetchall()

    top_users = [
        {
            "user_id": row.user_id,
            "name": row.name,
            "likes": row.total_likes,
            "shares": row.total_shares,
            "comments": row.total_comments,
            "total_engagement": row.total_engagement
        }
        for row in result
    ]

    return jsonify(top_users)

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



@app.route('/engagement/timeline/<int:user_id>', methods=['GET'])
def engagement_timeline_user(user_id):
    try:
        # Get actual activity dates from database
        post_dates = db.session.query(
            func.date_trunc('day', Posts.timestamp).label('date')
        ).filter(Posts.user_id == user_id).distinct()

        comment_dates = db.session.query(
            func.date_trunc('day', Comments.timestamp).label('date')
        ).filter(Comments.user_id == user_id).distinct()

        # Combine and sort unique dates
        all_dates = {row.date.date() for row in post_dates.union(comment_dates).all()}
        
        # Create timeline with actual activity
        timeline = []
        for single_date in sorted(all_dates):
            posts = db.session.query(
                func.coalesce(func.sum(Posts.likes_count + Posts.shares_count), 0)
            ).filter(
                Posts.user_id == user_id,
                func.date_trunc('day', Posts.timestamp) == single_date
            ).scalar()

            comments = db.session.query(
                func.count(Comments.comment_id)
            ).filter(
                Comments.user_id == user_id,
                func.date_trunc('day', Comments.timestamp) == single_date
            ).scalar()

            timeline.append({
                "date": single_date.isoformat(),
                "engagement": posts + comments
            })

        # Calculate total engagement
        total_engagement = sum(item["engagement"] for item in timeline)
        
        return jsonify({
            "timeline": timeline,
            "total_engagement": total_engagement,
            "message": f"Found {len(timeline)} active days for user {user_id}"
        })

    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e),
            "timeline": [],
            "total_engagement": 0
        }), 500




@app.route('/recent/posts/<int:user_id>', methods=['GET'])
def get_recent_posts_user(user_id):
    query = text("""
        SELECT p.post_id, p.content, p.timestamp, u.name AS username
        FROM posts p
        JOIN users u ON p.user_id = u.user_id
        WHERE p.user_id = :user_id
        ORDER BY p.timestamp DESC
        LIMIT 5
    """)
    result = db.session.execute(query, {'user_id': user_id})
    
    posts = [
        {
            "post_id": row.post_id,
            "content": row.content,
            "timestamp": row.timestamp.strftime("%Y-%m-%d %H:%M"),
            "username": row.username
        }
        for row in result
    ]
    return jsonify(posts)
@app.route('/top5/posts/<int:user_id>', methods=['GET'])
def get_top5_posts_user(user_id):
    query = text("""
        SELECT posts.post_id, posts.content, 
               (posts.likes_count + posts.shares_count + 
                (SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.post_id)) AS engagement
        FROM posts
        WHERE posts.user_id = :user_id
        ORDER BY engagement DESC
        LIMIT 5
    """)
    result = db.session.execute(query, {'user_id': user_id}).fetchall()
    
    top_posts = [
        {
            "post_id": row.post_id,
            "content": row.content,
            "engagement": row.engagement
        }
        for row in result
    ]
    return jsonify(top_posts)
@app.route('/top5/sentiment/posts/<int:user_id>', methods=['GET'])
def get_top5_post_sentiments_user(user_id):
    top_posts_query = text("""
        SELECT 
            p.post_id,
            p.content,
            (p.likes_count + p.shares_count + COALESCE(c.comment_count, 0)) AS engagement
        FROM posts p
        LEFT JOIN (
            SELECT post_id, COUNT(*) AS comment_count
            FROM comments
            GROUP BY post_id
        ) c ON p.post_id = c.post_id
        WHERE p.user_id = :user_id
        ORDER BY engagement DESC
        LIMIT 5
    """)
    
    top_posts = db.session.execute(top_posts_query, {'user_id': user_id}).fetchall()
    post_ids = [row.post_id for row in top_posts]
    
    sentiment_data_query = db.session.query(
        SentimentAnalysis.post_id,
        SentimentAnalysis.category,
        func.avg(SentimentAnalysis.sentiment_score).label("avg_score")
    ).filter(SentimentAnalysis.post_id.in_(post_ids))\
     .group_by(SentimentAnalysis.post_id, SentimentAnalysis.category).all()

    sentiment_map = {}
    for row in sentiment_data_query:
        if row.post_id not in sentiment_map:
            sentiment_map[row.post_id] = {}
        sentiment_map[row.post_id][row.category.lower()] = round(row.avg_score, 2)

    response = []
    for row in top_posts:
        sentiments = sentiment_map.get(row.post_id, {})
        response.append({
            "post_id": row.post_id,
            "content": row.content,
            "sentiments": {
                "positive": sentiments.get("positive", 0),
                "neutral": sentiments.get("neutral", 0),
                "negative": sentiments.get("negative", 0)
            }
        })

    return jsonify(response)

@app.route('/top5/comments/user/<int:user_id>', methods=['GET'])
def get_user_top_comments(user_id):
    try:
        # Get all posts by the user
        user_posts = db.session.query(Posts.post_id).filter(Posts.user_id == user_id).all()
        post_ids = [post.post_id for post in user_posts]

        if not post_ids:
            return jsonify({"message": "No posts found for this user", "comments": []})

        # Get top 5 comments for these posts
        comments_query = text("""
            SELECT c.comment_id, c.comment_text, c.timestamp, p.content AS post_content
            FROM comments c
            JOIN posts p ON c.post_id = p.post_id
            WHERE c.post_id IN :post_ids
            ORDER BY c.timestamp DESC
            LIMIT 5
        """)
        comments = db.session.execute(comments_query, {'post_ids': tuple(post_ids)}).fetchall()

        formatted_comments = [{
            "comment_id": row.comment_id,
            "comment_text": row.comment_text,
            "timestamp": row.timestamp.strftime("%Y-%m-%d %H:%M"),
            "post_content": row.post_content
        } for row in comments]

        return jsonify({"comments": formatted_comments})

    except Exception as e:
        app.logger.error(f"Error fetching comments for user {user_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    return render_template('index.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("Running on http://localhost:5001")
    print("Registered Routes:")
    for rule in app.url_map.iter_rules():
        print(rule)
    app.run(debug=True, port=5001)
