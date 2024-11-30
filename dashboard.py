from pytrends.request import TrendReq
import requests
import pandas as pd
import praw
from textblob import TextBlob


def get_interest_over_time(keywords, timeframe='today 5-y', geo='', output_format='dataframe'):
    """
    Fetches interest over time data for specified keywords using Google Trends API.

    Parameters:
        keywords (list): List of keywords to search for.
        timeframe (str): Time range for the data (default: 'today 5-y').
        geo (str): Regional filter (default: ''). Use ISO 3166-1 alpha-2 codes (e.g., 'US').
        output_format (str): Output format, either 'dataframe' or 'csv' (default: 'dataframe').

    Returns:
        pd.DataFrame: DataFrame containing search interest over time.
                      If output_format='csv', saves data to 'market_interest.csv'.
    """
    try:
        # Initialize the Google Trends API
        pytrends = TrendReq(hl='en-US', tz=360)

        # Build payload
        pytrends.build_payload(keywords, cat=0, timeframe=timeframe, geo=geo, gprop='')

        # Fetch interest over time data
        interest_data = pytrends.interest_over_time()

        # Check if data is returned
        if interest_data.empty:
            print("No data returned for the given keywords and parameters.")
            return None

        # Handle output format
        if output_format == 'csv':
            interest_data.to_csv('market_interest.csv')
            print("Data saved to 'market_interest.csv'.")
        else:
            return interest_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def time_series(data, keyword):
    """
    Extracts the time series for a specific keyword from the DataFrame.

    Parameters:
        data (pd.DataFrame): DataFrame containing interest over time data.
        keyword (str): The keyword for which the time series is extracted.

    Returns:
        pd.Series: A pandas Series with dates as index and interest values for the keyword.
    """
    if keyword not in data.columns:
        print(f"Keyword '{keyword}' not found in the data.")
        return None

    return data[keyword]

def get_interest_by_region(keywords, geo='', resolution='COUNTRY', output_format='dataframe'):
    """
    Fetches interest by region data for specified keywords using Google Trends API.

    Parameters:
        keywords (list): List of keywords to search for.
        geo (str): Regional filter (default: ''). Use ISO 3166-1 alpha-2 codes (e.g., 'US').
        resolution (str): Granularity of data. 'COUNTRY' (default), 'REGION', or 'CITY'.
        output_format (str): Output format, either 'dataframe' or 'csv' (default: 'dataframe').

    Returns:
        pd.DataFrame: DataFrame containing interest by region data.
                      If output_format='csv', saves data to 'interest_by_region.csv'.
    """
    try:
        # Initialize the Google Trends API
        pytrends = TrendReq(hl='en-US', tz=360)

        # Build payload
        pytrends.build_payload(keywords, cat=0, timeframe='today 5-y', geo=geo, gprop='')

        # Fetch interest by region data
        region_data = pytrends.interest_by_region(resolution=resolution, inc_low_vol=True, inc_geo_code=False)

        # Check if data is returned
        if region_data.empty:
            print("No data returned for the given keywords and parameters.")
            return None

        # Sort and filter non-zero interest regions
        region_data = region_data[region_data.sum(axis=1) > 0].sort_values(by=keywords[0], ascending=False)

        # Handle output format
        if output_format == 'csv':
            region_data.to_csv('interest_by_region.csv')
            print("Data saved to 'interest_by_region.csv'.")
        else:
            return region_data

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_related_queries(keywords):
    """
    Fetches related queries for the specified keywords using Google Trends API.

    Parameters:
        keywords (list): List of keywords to search for.

    Returns:
        dict: Dictionary containing top and rising related queries for each keyword.
    """
    try:
        # Initialize the Google Trends API
        pytrends = TrendReq(hl='en-US', tz=360)

        # Build payload
        pytrends.build_payload(keywords, cat=0, timeframe='today 12-m', geo='', gprop='')

        # Fetch related queries
        related_queries = pytrends.related_queries()

        # Check if data is returned
        if not related_queries:
            print("No related queries found for the given keywords.")
            return None

        return related_queries

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_tweet_count(keyword, bearer_token):
    """
    Fetches the number of posts or mentions containing a specific keyword or hashtag from Twitter API.

    Parameters:
        keyword (str): Keyword or hashtag to search for (e.g., "Python" or "#Python").
        bearer_token (str): Bearer token for Twitter API authentication.

    Returns:
        int: Count of tweets containing the keyword.
    """
    try:
        # Twitter API endpoint for tweet counts
        url = "https://api.twitter.com/2/tweets/counts/recent"

        # Query parameters
        params = {
            "query": keyword,  # Keyword or hashtag
            "granularity": "day"  # Daily counts (options: 'minute', 'hour', 'day')
        }

        # Headers for authentication
        headers = {
            "Authorization": f"Bearer {bearer_token}"
        }

        # Make the request
        response = requests.get(url, headers=headers, params=params)

        # Check for success
        if response.status_code != 200:
            print(f"Error: Unable to fetch data. Status Code: {response.status_code}")
            print(f"Response: {response.json()}")
            return None

        # Parse response
        data = response.json()

        # Sum total counts
        total_count = sum([entry["tweet_count"] for entry in data.get("data", [])])

        return total_count

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_reddit_post_count_praw(keyword, client_id, client_secret, user_agent):
    """
    Fetches the number of posts containing a specific keyword on Reddit using PRAW.

    Parameters:
        keyword (str): The keyword to search for.
        client_id (str): Reddit app client ID.
        client_secret (str): Reddit app client secret.
        user_agent (str): User agent for Reddit API.

    Returns:
        int: Count of posts containing the keyword.
    """
    try:
        # Initialize Reddit API
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

        # Search for the keyword
        post_count = 0
        for post in reddit.subreddit("all").search(keyword, limit=100):  # Searches across all subreddits
            post_count += 1

        return post_count

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def fetch_tweets(query, bearer_token, max_results=10):
    """
    Fetches tweets containing a specific keyword using the Twitter API.

    Parameters:
        query (str): The keyword or hashtag to search for.
        bearer_token (str): The Bearer Token for Twitter API authentication.
        max_results (int): The maximum number of tweets to fetch (max 100).

    Returns:
        list: A list of tweet texts.
    """
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    params = {
        "query": query,
        "max_results": max_results,
        "tweet.fields": "text"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  # Raise an error if the request fails
    tweets = response.json().get("data", [])
    return [tweet["text"] for tweet in tweets]

def analyze_tone(text):
    """
    Analyzes the tone of a given text using TextBlob.

    Parameters:
        text (str): The text to analyze.

    Returns:
        str: The tone of the text ('Positive', 'Negative', 'Neutral').
    """
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity  # Polarity ranges from -1 (negative) to 1 (positive)
    
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"
def fetch_reddit_posts(keyword, reddit, limit=10):
    """
    Fetches Reddit posts containing a specific keyword.

    Parameters:
        keyword (str): The keyword to search for in Reddit posts.
        reddit (praw.Reddit): Authenticated Reddit instance.
        limit (int): Number of posts to fetch.

    Returns:
        list: A list of post titles.
    """
    posts = []
    for submission in reddit.subreddit("all").search(keyword, limit=limit):
        posts.append(submission.title)
    return posts
def analyze_sentiment(text):
    """
    Analyzes the sentiment of a given text.

    Parameters:
        text (str): The text to analyze.

    Returns:
        dict: A dictionary containing the sentiment score and tone.
    """
    analysis = TextBlob(text)
    sentiment_score = analysis.sentiment.polarity  # Polarity: -1 (negative) to 1 (positive)
    
    if sentiment_score > 0:
        tone = "Positive"
    elif sentiment_score < 0:
        tone = "Negative"
    else:
        tone = "Neutral"
    
    return {"sentiment_score": sentiment_score, "tone": tone}
# Main Method
if __name__ == "__main__":
    # Define parameters
    keywords = ["Python", "Django"]
    timeframe = "today 12-m"  # Last 12 months
    keyword = "Python"
    geo = "US"  # United States
    output_format = "dataframe"
    resolution = "COUNTRY"
    bearer_token = "AAAAAAAAAAAAAAAAAAAAAKzyxAEAAAAAWBUZ5EqO%2Fjv%2Fc7iy8UtsxGsoudE%3DiCgpYHl9HzrpV3oQHqpAWmMPGcIRuK6LdAGnsGoHLCI1PZ6Fxb"  # Replace with your actual Bearer Token
    # Reddit API credentials
    CLIENT_ID = "VdSSItCkVjPLnOD76ddssA"  # Replace with your actual client ID
    CLIENT_SECRET = "_uZ1BUrGHu4SliJFYridYLSpY1FxQw"  # Replace with your actual client secret
    USER_AGENT = "u/Old_Agency5589"  # Replace with your app's user agent
    reddit = praw.Reddit(
            client_id="VdSSItCkVjPLnOD76ddssA",
            client_secret="_uZ1BUrGHu4SliJFYridYLSpY1FxQw",
            user_agent="u/Old_Agency5589"
        )

    # Fetch interest over time data
    # interest_data = get_interest_over_time(keywords, timeframe, geo, output_format)

    # if interest_data is not None:
    #     print("Interest Over Time Data:")
    #     print(interest_data)

    #     # Get time series for a specific keyword
        
    #     python_time_series = time_series(interest_data, keyword)

    #     if python_time_series is not None:
    #         print(f"\nTime Series for '{keyword}':")
    #         print(python_time_series)
    # interest_by_region = get_interest_by_region(keywords, geo, resolution, output_format)

    # if interest_by_region is not None:
    #     print("\nInterest by Region Data:")
    #     print(interest_by_region)

    # related_queries = get_related_queries(keywords)
    # if related_queries:
    #     print("Related Queries:")
    #     for kw, data in related_queries.items():
    #         print(f"\nKeyword: {kw}")
    #         print("Top Queries:")
    #         print(data['top'])  # Top related queries
    #         print("\nRising Queries:")
    #         print(data['rising'])  # Rising related queries
    # tweet_count = get_tweet_count(keyword, bearer_token)
    # if tweet_count is not None:
    #     print(f"\nTotal tweet count for '{keyword}': {tweet_count}")
    # post_count = get_reddit_post_count_praw(keyword, CLIENT_ID, CLIENT_SECRET, USER_AGENT)
    # if post_count is not None:
    #     print(f"The total number of posts mentioning '{keyword}' is: {post_count}")
    # print(f"Fetching tweets for query: {keyword}")
    # tweets = fetch_tweets(keyword, bearer_token, max_results=10)
    
    # # Analyze tone
    # print("\nAnalyzing tone of tweets:")
    # for idx, tweet in enumerate(tweets, start=1):
    #     tone = analyze_tone(tweet)
    #     print(f"{idx}. Tweet: {tweet}")
    #     print(f"   Tone: {tone}\n")
    print(f"Fetching posts for keyword: {keyword}")
    
    # Fetch Reddit posts
    posts = fetch_reddit_posts(keyword, reddit, limit=10)
    
    # Analyze sentiment of posts
    print("\nAnalyzing sentiment of posts:")
    for idx, post in enumerate(posts, start=1):
        sentiment = analyze_sentiment(post)
        print(f"{idx}. Post: {post}")
        print(f"   Sentiment Score: {sentiment['sentiment_score']:.2f}, Tone: {sentiment['tone']}\n")