import csv
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Constants
NUM_USERS = 100
NUM_POSTS = 300
NUM_HASHTAGS=500
NUM_COMMENTS = 500
NUM_SENTIMENTS = 500

# Ensure unique values using a set
unique_emails = set()

# ========================
# Generate Users
# ========================
users = []
while len(users) < NUM_USERS:
    email = fake.unique.email()
    if email not in unique_emails:
        unique_emails.add(email)
        users.append({
            'user_id': len(users) + 1,
            'name': fake.name(),
            'email': email,
            'age': random.randint(18, 70),
            'location': fake.city(),
            'joined_date': fake.date_time_this_decade()
        })

# Write to users.csv
with open('users.csv', 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=users[0].keys())
    writer.writeheader()
    writer.writerows(users)

print(f"✅ Generated {len(users)} unique user records in 'users.csv'")

# ========================
# Generate Posts
# ========================
posts = []
for _ in range(NUM_POSTS):
    posts.append({
        'post_id': _ + 1,
        'user_id': random.randint(1, NUM_USERS),
        'content': fake.sentence(nb_words=random.randint(5, 15)),  # Meaningful sentence
        'timestamp': fake.date_time_this_year(),
        'likes_count': random.randint(0, 500),
        'shares_count': random.randint(0, 100)
    })

# Write to posts.csv
with open('posts.csv', 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=posts[0].keys())
    writer.writeheader()
    writer.writerows(posts)

print(f"✅ Generated {len(posts)} posts in 'posts.csv'")


# Generate unique hashtags
hashtags = set()
while len(hashtags) < 200:
    hashtags.add(f"#{fake.word()}")

hashtags = list(hashtags)

# Generate data
data = []
for _ in range(NUM_HASHTAGS):
    post_id = random.randint(1,NUM_POSTS)
    hashtag = random.choice(hashtags)
    
    # Generate a random timestamp in the last 30 days
    timestamp = fake.date_time_between(start_date='-30d', end_date='now').strftime('%Y-%m-%d %H:%M:%S')
    
    data.append([post_id, hashtag, timestamp])

# Write to CSV
filename = "hashtag.csv"
with open(filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["post_id", "hashtag", "timestamp"])  # Write header
    writer.writerows(data)

print(f"✅ Generated {len(data)} hashtags in 'hashtag.csv'")



# ========================
# Generate Comments
# ========================
comments = []
for _ in range(NUM_COMMENTS):
    comments.append({
        'comment_id': _ + 1,
        'post_id': random.randint(1, NUM_POSTS),
        'user_id': random.randint(1, NUM_USERS),
        'comment_text': fake.sentence(nb_words=random.randint(10, 20)),  # Realistic sentence
        'timestamp': fake.date_time_this_year()
    })

# Write to comments.csv
with open('comments.csv', 'w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=comments[0].keys())
    writer.writeheader()
    writer.writerows(comments)

print(f"✅ Generated {len(comments)} comments in 'comments.csv'")

# ========================
# Generate Sentiments
# ========================
sentiment_categories = ['Positive', 'Negative', 'Neutral']
data = []
for _ in range(NUM_SENTIMENTS):
    post_id = random.randint(1,NUM_POSTS)
    sentiment_score = round(random.uniform(-1, 1), 2)
    category = random.choice(sentiment_categories)
    data.append([post_id, sentiment_score, category])

# Write to CSV
with open('sentiments.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['post_id', 'sentiment_score', 'category'])
    writer.writerows(data)

print(f"✅ Generated {len(data)} sentiment records in 'sentiments.csv'")

