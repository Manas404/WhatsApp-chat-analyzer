import re
import pandas as pd


def preprocess(data):
    # Replace narrow no-break space with normal space
    data = data.replace("\u202f", " ")


    # Regex pattern to capture datetime
    pattern = r'\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2}\s[AP]M -'

    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    # Try multiple datetime formats (because WhatsApp exports differ by region)
    date_formats = [
        "%m/%d/%y, %I:%M %p -",
        "%m/%d/%Y, %I:%M %p -",
        "%d/%m/%y, %I:%M %p -",
        "%d/%m/%Y, %I:%M %p -"
    ]

    parsed_dates = None
    for fmt in date_formats:
        try:
            parsed_dates = pd.to_datetime(df['message_date'], format=fmt, errors="coerce")
            if parsed_dates.notnull().all():
                break
        except Exception:
            continue

    df['date'] = parsed_dates
    df.drop(columns=['message_date'], inplace=True)

    # Split user and message
    users, messages = [], []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages.append(entry[0])

    df['user'] = users
    df['message'] = messages
    df.drop(columns=['user_message'], inplace=True)

    # Extract datetime features
    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Define hourly periods
    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append("23-00")
        elif hour == 0:
            period.append("00-1")
        else:
            period.append(f"{hour}-{hour + 1}")
    df['period'] = period

    return df
