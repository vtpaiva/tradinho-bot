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

## Authors

<a href="https://github.com/HerbGlrt">
    <img src="https://avatars.githubusercontent.com/u/62862399?v=4" alt="Author 1" width="100px" height="auto" style="border-radius: 50%;">
</a>


<a href="https://github.com/vtpaiva">
    <img src="https://avatars.githubusercontent.com/u/105892477?v=4" alt="Author 2" width="100px" height="auto" style="border-radius: 50%;">
</a>