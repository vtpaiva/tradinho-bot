# tradinho-bot

<img align="right" src="assets/Tradinho.png" alt="Tradinho Logo" width="250px" height="auto" border-radius="50%">

This repository was created to store the process of ***Tradinho Bot***, a brazilian citzen inspired model to predict **S&P 500** stocks prices along the last years to participate of the *Itau Quant Challenge 2024*.

## Resources

The major language in use is Python, this includes web scrapping, data analysis, data engineering and model training.

To make it possible, we're using the **The Guardian** *API* to fetch related news headlines and, in order to get the **S&P 500** stocks prices, **Yahoo Finance** and **FRED** *APIs* along the years of interest (2009-2023).

## Web scrapping

First, on the web scrapping phase, we've used Python to make requests for **The Guardian** *API*, **Yahoo Finance** *API* and **FRED** *API*.

This code is related to to main process of building the news's headlines database from **The Guardian**.

```python
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
```

With this, it was possible to extract data from the APIs from December 30, 2009 to October 30, 2024 and build the datasets for analysis and training.

## Bot Operation

This report explores the application of machine learning methods to predict variations in the S&P500 index prices. It leverages economic and sentiment-based data to structure a **Quant** algorithm designed for real-world market applications. The analysis is based on publicly available data, including news headlines retrieved through the British newspaper *The Guardian's API* and financial data from the S&P500 index sourced via *Yahoo Finance's API*. Additionally, fifteen U.S. economic indicators, such as interest and unemployment rates, were incorporated to create a robust dataset reflecting market conditions, covering the period from late 2009 to October 2024.

The primary application will be named **Tradinho**, a nod to a Brazilian investor persona, aiming to build a charismatic yet serious and reliable image of a national investor growing their wealth by investing in foreign stocks.

### Main Objective
The central goal is to forecast the price difference of the S&P500 index over defined two-week intervals (*fortnights*). In a real-world scenario, the algorithm will use the forecast generated on the last day of a *fortnight* to predict the relative price change for the next interval. This prediction will serve as the basis for a trading signal, executed at the beginning of the following window.

### Methodology
The theoretical framework assumes that future asset prices depend on U.S. economic indicators and the global economic context. Therefore:
1. **Historical Data Feedback:** The algorithm incorporates historical prices and economic indicators for temporal sequence learning.
2. **Sentiment Analysis:** Global socioeconomic sentiment is analyzed using headlines from *The Guardian* to understand how global trends impact asset prices.

Two forecasting tasks are implemented:
- **Time Series Analysis:** U.S. economic data and daily S&P500 prices from *FRED* and *Yahoo Finance* are used to predict internal price variations within a *fortnight*.
- **Sentiment Analysis:** Global socioeconomic sentiment derived from news is used to predict price differences.

Finally, the outputs from these regressions are combined using a weighted average to generate the final prediction and trading signal.

## Authors

<a href="https://github.com/HerbGlrt">
    <img src="https://avatars.githubusercontent.com/u/62862399?v=4" alt="Author 1" width="100px" height="auto" style="border-radius: 50%;">
</a>


<a href="https://github.com/vtpaiva">
    <img src="https://avatars.githubusercontent.com/u/105892477?v=4" alt="Author 2" width="100px" height="auto" style="border-radius: 50%;">
</a>