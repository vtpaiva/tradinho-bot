from datetime import datetime, timedelta
import requests, json, re, pandas as pd

OK = 200 # Ok return value from request.
FIRST_DATE = datetime.strptime('2009-12-31', "%Y-%m-%d") # First date of interest of data.
DATE_LIMIT = datetime.strptime('2023-12-30', "%Y-%m-%d") # Last date od interest of data.
API_KEY = "your_apu_key"  # The Guardian API key (replace with your The Guardian API key).
BASE_URL = "https://content.guardianapis.com/search" # Base URL to The Guardian API.
EXTRACT_FIELDS = ['sectionId', 'webPublicationDate', 'webTitle'] # Interest fields from request.

"""Sends a request to The Guardian API to fetch articles.

Parameters:
    - item: dictionary containing request's parameters.
    - start_date: start date to request headlines.
    - fortnight: row's fortnight.
    - page_size: number of articles per page.

Returns:
    - Pandas dataframe with headlines."""

def fetch_articles(item: dict, start_date: datetime, fortnight: int, page_size: int = 200) -> pd.DataFrame:
    frame, end_date = [], start_date + timedelta(days=15)

    # Request parameters
    params = {
        'q': item['q'],
        'section': item['Section'],
        "order-by": 'oldest',
        'from-date': datetime.strftime(start_date, "%Y-%m-%d"),
        'to-date': datetime.strftime(end_date, "%Y-%m-%d"),
        'page-size': page_size,
        'api-key': API_KEY
    }

    # Sending the request
    response = requests.get(BASE_URL, params=params)

    if response.status_code == OK:
        data = response.json()

        for new in data['response']['results']:
            row = {key: new[key] for key in EXTRACT_FIELDS}

            row['webPublicationDate'] = re.match(r"([^T]+)", row['webPublicationDate']).group(0)
            row['fortnight'] = fortnight

            frame.append(row)

        return pd.DataFrame(frame)
    else:
        print("Error fetching articles:", response.status_code)
        return None

"""Returns database from fetch.

Parameters:
    - json_data: json file with the request parameters.
    - last_date: last date on the current database.
    - fortnight: row's fortnight.

Returns:
    - Pandas dataframe with the objects from fetch."""

def fetch_to_dataframe(json_data: json, last_date: datetime, fortnight: int) -> pd.DataFrame:
    final_fetch = pd.DataFrame()

    # Fetch and concatenate.
    for _, params in json_data.items():
        fetch_df = fetch_articles(params, start_date=last_date, fortnight=fortnight)

        if fetch_df is None:
            break

        final_fetch = pd.concat([final_fetch, fetch_df])

    final_fetch = final_fetch.drop_duplicates(subset='webTitle')
    final_fetch = final_fetch.sort_values(by=['fortnight', 'webPublicationDate'])

    return final_fetch

"""Increases the database from the current state, fetching headlines.

Parameters:
    - database: pandas database's path.
    - param_file: json file with request's parameters.

Returns:
    - None."""

def update_database(database: str = 'tradinho-headlines.csv', param_file: str = 'the-guardian-queries.json') -> None:
    base = pd.read_csv(database)

    with open(param_file, "r") as file:
        json_data = json.load(file)

    # If the database has at least one row, update it.
    if base.shape[0] > 0:
        last_row = base.iloc[-1]

        last_fortnight = counter = last_row['fortnight'] + 1
        last_date = FIRST_DATE + timedelta(days=int(15*last_fortnight + 2))

        # Increase until the date limit.
        while DATE_LIMIT > last_date:
            final_fetch = fetch_to_dataframe(json_data, last_date, counter)

            base = pd.concat([base, final_fetch])
            base.to_csv('tradinho-headlines.csv', index=False)

            last_date = last_date + timedelta(days=16)
            counter += 1
    else:
        print("Database doesn't exists.")

if __name__ == "__main__":
    update_database()