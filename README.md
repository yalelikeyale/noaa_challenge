# noaa-tap

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started).

This tap:

- Pulls raw data from [NOAA API](https://www.ncdc.noaa.gov/cdo-web/webservices/v2#gettingStarted)
- Extracts the following resources:
  - [GSOM](https://www.ncdc.noaa.gov/cdo-web/webservices/v2#data)
- Outputs the data in json files with a 10,000 result limit

Set-Up:

1. Clone this repo
2. Make sure you have pipenv installed otherwise run
```
pip install pipenv
```
3. Install the package and the dependencies
```
pipenv install -e .
```
4. Request an API token [here](https://www.ncdc.noaa.gov/cdo-web/webservices/v2#gettingStarted)
5. Create a config.json file from sample-config.json
  - Provide the API Key acquired from step 1
  - Provide the start_date and end_date to determine the date range that you're interested in
  - Save the file as config.json


Usage:
1. Activate your pipenv environment
```
pipenv shell
```

2. Discover
  - Run the following to view the available streams the tap supports
```
noaa-challenge --config config.json --discover >> catalog.json
```

3. Select Streams
  - Add ```"selected":true``` within the schema object to select the stream

```
    {
       "schema": {
            "properties": {...},
            "type": "object",
            "selected": true
        },
        "stream": "orders",
        "tap_stream_id": "orders"
    }
```


4.Run the tap

```
noaa-challenge --config config.json --catalog catalog.json
```

5. Profit???
