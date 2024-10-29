from datetime import datetime, timedelta
import requests, json, re, pandas as pd

OK = 200
FIRST_DATE = datetime.strptime('2009-12-31', "%Y-%m-%d") 
DATE_LIMIT = datetime.strptime('2023-12-30', "%Y-%m-%d") 
API_KEY = "your_api_key"  # Replace with your The Guardian API key
BASE_URL = "https://content.guardianapis.com/search"
EXTRACT_FIELDS = ['sectionId', 'webPublicationDate', 'webTitle']

"""Sends a request to The Guardian API to fetch articles.

Parameters:
    - config: dictionary containing parameters `q`, `Section`, and `production-office`.
    - page_size: number of articles per page.

Returns:
    - JSON with article data."""

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

    if start_date > datetime.strptime('2013-04-20', "%Y-%m-%d"):
        params['production-office'] = item['production-office'] 

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

def increasing_database(database: str = 'tradinho-database.csv', param_file: str = 'queries.json') -> None:
    base = pd.read_csv(database)

    with open(param_file, "r") as file:
        json_data = json.load(file)

    if base.shape[0] > 0:
        last_row = base.iloc[-1]

        last_fortnight = counter = last_row['fortnight'] + 1
        last_date = FIRST_DATE + timedelta(days=int(15*last_fortnight + 2))

        while DATE_LIMIT > last_date:
            for _, params in json_data.items():
                fetch_df = fetch_articles(params, start_date=last_date, fortnight=counter)

                if fetch_df is None:
                    break

                base = pd.concat([base, fetch_df])

            base.to_csv('tradinho-database.csv', index=False)

            last_date = last_date + timedelta(days=15)

            counter += 1
    else:
        print("Base doesn't exists.")

if __name__ == "__main__":
    increasing_database()