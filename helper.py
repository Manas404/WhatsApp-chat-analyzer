from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import pandas as pd
import emoji

extract = URLExtract()


# ---------------- Basic Stats ----------------
def fetch_stats(user, df):
    if user != "Overall":
        df = df[df['user'] == user]

    num_messages = df.shape[0]
    words = sum(len(message.split()) for message in df['message'])
    num_media_messages = df[df['message'] == '<Media omitted>'].shape[0]

    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, words, num_media_messages, len(links)


# ---------------- Timelines ----------------
def monthly_timeline(user, df):
    if user != "Overall":
        df = df[df['user'] == user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    if timeline.empty:
        return pd.DataFrame()

    timeline['time'] = timeline['month'] + "-" + timeline['year'].astype(str)
    return timeline


def daily_timeline(user, df):
    if user != "Overall":
        df = df[df['user'] == user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline


# ---------------- Activity Maps ----------------
def week_activity_map(user, df):
    if user != "Overall":
        df = df[df['user'] == user]
    return df['day_name'].value_counts()


def month_activity_map(user, df):
    if user != "Overall":
        df = df[df['user'] == user]
    return df['month'].value_counts()


def activity_heatmap(user, df):
    if user != "Overall":
        df = df[df['user'] == user]
    return df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)


# ---------------- Most Busy Users ----------------
def most_busy_users(df):
    x = df['user'].value_counts().head()
    new_df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x, new_df


# ---------------- Wordcloud & Common Words ----------------
def create_wordcloud(user, df):
    if user != "Overall":
        df = df[df['user'] == user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>']

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    return wc.generate(" ".join(temp['message']))


def most_common_words(user, df):
    if user != "Overall":
        df = df[df['user'] == user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>']

    words = []
    for message in temp['message']:
        words.extend(message.lower().split())

    return pd.DataFrame(Counter(words).most_common(20))


# ---------------- Emoji Analysis ----------------
def emoji_helper(user, df):
    if user != "Overall":
        df = df[df['user'] == user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])

    return pd.DataFrame(Counter(emojis).most_common(len(emojis)))
