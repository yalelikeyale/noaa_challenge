# noaa-tap

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/blob/master/SPEC.md).

This tap:

- Pulls raw data from [NOAA API](https://www.ncdc.noaa.gov/cdo-web/webservices/v2#gettingStarted)
- Extracts the following resources:
  - [GSOM](https://www.ncdc.noaa.gov/cdo-web/webservices/v2#data)
- Outputs the schema for the data?datasetid=GSOM dataset

Set-Up:

1. Clone this repo
2. Make sure you have pyenv installed otherwise run
```
pip install pipenv
```
3. Install the package and the dependencies
```
pipenv install -e .
```

Usage:

1. Request an API token [here](https://www.ncdc.noaa.gov/cdo-web/webservices/v2#gettingStarted)
2. Create Config file from sample-config.json
  - Replace the {API_Token} value with your API Token from step 1
  - Replace the {Start Date} and {End Date} values with the desired date range you'd like to pull

2. Discover

```
pipenv run noaa-challenge --config config.json --discover >> catalog.json
```
- Run the above to discover and store the API Scheme 
  - You'll need to store the schema in order to run the tap

3. Select Streams

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
- Add ```"selected":true``` within the schema object to select the stream

4.Run the tap

```
pipenv run noaa-challenge --config config.json --catalog catalog.json
```

5. Profit???
