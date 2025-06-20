from flask import Flask, render_template, request
import googleapiclient.discovery
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
from tqdm import tqdm
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

# YouTube API Setup
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY =yourDeveloperKey
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

ps = PorterStemmer()
sia = SentimentIntensityAnalyzer()

# YouTube comments
def get_comments(video_id):
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        maxResults=100
    )
    comments = []
    comment_id = 1
    response = request.execute()
    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']   #for only top level comment(no reply)
        comments.append([
            comment_id,
            comment['authorDisplayName'],
            comment['likeCount'],
            comment['textOriginal'],
        ])
        comment_id += 1
    while 'nextPageToken' in response:
        nextPageToken = response['nextPageToken']
        nextRequest = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            maxResults=100,
            pageToken=nextPageToken
        )
        response = nextRequest.execute()
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append([
                comment_id,
                comment['authorDisplayName'],
                comment['likeCount'],
                comment['textOriginal'],
            ])
            comment_id += 1
    df = pd.DataFrame(comments, columns=['ID', 'author', 'like_count', 'text'])
    return df

# Function to check if the video ID is valid
def is_valid_video_id(video_id):
    try:
        youtube.videos().list(part="snippet", id=video_id).execute()
        return True
    except googleapiclient.errors.HttpError:
        return False

# Function to analyze sentiment
def analyze_sentiment(df):
    res = {}
    for i, row in tqdm(df.iterrows(), total=len(df)):  #iterrows-->key-value pair **tqdm-->progress bar
        text = row['text']
        sentences = nltk.sent_tokenize(text)
        corpus = []
        for sentence in sentences:
            review = re.sub(r'[^a-zA-Z\s]', '', sentence)
            review = review.lower()
            review = review.split()
            review = [ps.stem(word) for word in review if word not in set(stopwords.words('english'))]
            review = ' '.join(review)
            corpus.append(review)
        single_string = " ".join(corpus)
        myid = row['ID']
        res[myid] = sia.polarity_scores(single_string)
    vaders = pd.DataFrame(res).T
    vaders = vaders.reset_index().rename(columns={'index': 'ID'})
    vaders = vaders.merge(df, how='left')
    return vaders

# Function to compute a sentiment-based rating
def compute_rating(vaders):
    filtered_vaders = vaders[vaders['compound'] != 0]
    compound_mean = filtered_vaders['compound'].mean()
    positive_mean = filtered_vaders['pos'].mean()
    negative_mean = filtered_vaders['neg'].mean()
    if positive_mean > negative_mean + 0.3:
        positive_weight = 5
    elif positive_mean > negative_mean + 0.2:
        positive_weight = 3
    elif positive_mean > negative_mean + 0.15:
        positive_weight = 2
    else:
        positive_weight = 1

    negative_weight = 1.5

    dataset_rating = ((compound_mean + 1) / 2 * 3) + (positive_mean * positive_weight) - (negative_mean * negative_weight)
    dataset_rating = max(0, min(5, dataset_rating))  # Ensure rating stays between 0 and 5
    dataset_rating = round(dataset_rating, 2)
    return dataset_rating


# Initialize Flask
app = Flask(__name__)


# Flask route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    video_details = None
    rating = None
    error_message =None
    if request.method == 'POST':
        video_id = request.form['video_id']
        if 'v=' in video_id:
            video_id = video_id.split("v=")[1]
            if '&' in video_id:
                video_id = video_id.split("&")[0]
        else:
            error_message = "Invalid YouTube video URL format. Please enter a valid URL."
        if not is_valid_video_id(video_id):
            error_message = "Invalid Video ID. Please enter a valid YouTube video ID."
        if error_message is None:
            try:

                # Fetch video details
                video_details = get_video_details(video_id)
                # Fetch comments for the video
                df = get_comments(video_id)
                # Perform sentiment analysis on the comments
                vaders = analyze_sentiment(df)
                # Compute the video rating based on sentiment analysis
                rating = compute_rating(vaders)
            except Exception as e:
                error_message = str(e)

    return render_template('index.html', video_details=video_details, rating=rating,error_message=error_message)


def get_video_details(video_id):
    """Fetch video details including title and thumbnail."""
    response = youtube.videos().list(part="snippet", id=video_id).execute()
    
    video_details = response['items'][0]['snippet']
    return {
        "title": video_details['title'],
        "thumbnail_url": video_details['thumbnails']['high']['url']
    }

# Main function to run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080,debug=True)