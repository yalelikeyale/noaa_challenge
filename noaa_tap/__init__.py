#!/usr/bin/env python
# coding: utf-8

import itertools
import os
import sys
import time
import re
import json
import attr
import urllib
import requests
import backoff
from requests.auth import HTTPBasicAuth
import datetime
import dateutil
from dateutil import parser
import singer
import singer.metrics as metrics
from singer import utils




REQUIRED_CONFIG_KEYS = ["url","datasetid", "api_key", "start_date", "end_date"]
CONFIG = json.loads(open('config.json').read())
ENDPOINTS = {
    "gsom":"datasetid=GSOM&startdate={0}&enddate={1}&offset={2}&limit=999"
}
LOGGER = singer.get_logger()

def get_endpoint(endpoint, kwargs):
    '''Get the full url for the endpoint'''
    if endpoint not in ENDPOINTS:
        raise ValueError("Invalid endpoint {}".format(endpoint))
    
    datasetid = urllib.parse.quote(kwargs[0])
    startdate = kwargs[0]
    enddate = kwargs[1]
    offset = kwargs[2]
    return CONFIG["url"]+ENDPOINTS[endpoint].format(startdate,enddate,offset)


def get_start(STATE, tap_stream_id, bookmark_key):
    current_bookmark = singer.get_bookmark(STATE, tap_stream_id, bookmark_key)
    if current_bookmark is None:
        return 0
    return current_bookmark



def load_schema(entity):
    '''Returns the schema for the specified source'''
    schema = utils.load_json(get_abs_path("schemas/{}.json".format(entity)))

    return schema


def giveup(exc):
    return exc.response is not None and 400 <= exc.response.status_code < 500 and exc.response.status_code != 429


@backoff.on_exception(backoff.expo,
                      requests.exceptions.RequestException,
                      max_tries=5,
                      on_giveup=giveup)

@utils.ratelimit(20, 1)
def gen_request(stream_id, url):
    with metrics.http_request_timer(stream_id) as timer:
        resp = requests.get(url, headers={"token":CONFIG["api_key"]})
        timer.tags[metrics.Tag.http_status_code] = resp.status_code
        resp.raise_for_status()
        return resp.json()



def sync_gsom(STATE, catalog):
    schema = load_schema("gsom")
    singer.write_schema("gsom", schema, ["order_id"])

    start = get_start(STATE, "gsom", "last_update")
    LOGGER.info("Only syncing gsom updated since " + str(start))
    records_processed = start
    offset = 0
    with metrics.record_counter("gsom") as counter:
        while True:
            endpoint = get_endpoint("gsom", [CONFIG["start_date"],CONFIG["end_date"],offset])
            LOGGER.info("GET %s", endpoint)
            response = gen_request("gsom",endpoint)
            for result in response["results"]:
                counter.increment()
                singer.write_record("gsom", result)
            if len(response["results"])<999:
                break
            else:
                offset +=1000
    STATE = singer.write_bookmark(STATE, 'gsom', 'last_update', counter.value) 
    singer.write_state(STATE)
    LOGGER.info("Completed NOAA GSOM Sync")
    return STATE



@attr.s
class Stream(object):
    tap_stream_id = attr.ib()
    sync = attr.ib()



STREAMS = [
    Stream("gsom", sync_gsom)
]



def get_streams_to_sync(streams, state):
    '''Get the streams to sync'''
    current_stream = singer.get_currently_syncing(state)
    result = streams
    if current_stream:
        result = list(itertools.dropwhile(
            lambda x: x.tap_stream_id != current_stream, streams))
    if not result:
        raise Exception("Unknown stream {} in state".format(current_stream))
    return result



def get_selected_streams(remaining_streams, annotated_schema):
    selected_streams = []

    for stream in remaining_streams:
        tap_stream_id = stream.tap_stream_id
        for stream_idx, annotated_stream in enumerate(annotated_schema.streams):
            if tap_stream_id == annotated_stream.tap_stream_id:
                schema = annotated_stream.schema
                if (hasattr(schema, "selected")) and (schema.selected is True):
                    selected_streams.append(stream)

    return selected_streams



def do_sync(STATE, catalogs):
    '''Sync the streams that were selected'''
    remaining_streams = get_streams_to_sync(STREAMS, STATE)
    selected_streams = get_selected_streams(remaining_streams, catalogs)
    if len(selected_streams) < 1:
        LOGGER.info("No Streams selected, please check that you have a schema selected in your catalog")
        return

    LOGGER.info("Starting sync. Will sync these streams: %s", [stream.tap_stream_id for stream in selected_streams])

    for stream in selected_streams:
        LOGGER.info("Syncing %s", stream.tap_stream_id)
        singer.set_currently_syncing(STATE, stream.tap_stream_id)
        singer.write_state(STATE)

        try:
            catalog = [cat for cat in catalogs.streams if cat.stream == stream.tap_stream_id][0]
            STATE = stream.sync(STATE, catalog)
        except Exception as e:
            LOGGER.critical(e)
            raise e


def get_abs_path(path):
    '''Returns the absolute path'''
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)



def load_discovered_schema(stream):
    '''Attach inclusion automatic to each schema'''
    schema = load_schema(stream.tap_stream_id)
    for k in schema['properties']:
        schema['properties'][k]['inclusion'] = 'automatic'
    return schema

def discover_schemas():
    '''Iterate through streams, push to an array and return'''
    result = {'streams': []}
    for stream in STREAMS:
        LOGGER.info('Loading schema for %s', stream.tap_stream_id)
        result['streams'].append({'stream': stream.tap_stream_id,
                                  'tap_stream_id': stream.tap_stream_id,
                                  'schema': load_discovered_schema(stream)})
    return result

def do_discover():
    '''JSON dump the schemas to stdout'''
    LOGGER.info("Loading Schemas")
    json.dump(discover_schemas(), sys.stdout, indent=4)



@utils.handle_top_exception(LOGGER)
def main():
    '''Entry point'''
    args = utils.parse_args(REQUIRED_CONFIG_KEYS)

    CONFIG.update(args.config)
    STATE = {}

    if args.state:
        STATE.update(args.state)
    if args.discover:
        do_discover()
    elif args.properties:
        do_sync(STATE, args.properties)
    elif args.catalog:
        do_sync(STATE, args.catalog)
    else:
        LOGGER.info("No Streams were selected")


if __name__ == "__main__":
    main()

