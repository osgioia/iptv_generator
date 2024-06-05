#!/usr/bin/python3

import requests
import os
import sys
import streamlink
import logging
from logging.handlers import RotatingFileHandler
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  

log_file = "log.txt" 
file_handler = RotatingFileHandler(log_file)
file_handler.setLevel(logging.DEBUG) 

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

banner = r'''
######################################################################
#  _       _                                          _              #
# (_)     | |                                        | |             # 
#  _ _ __ | |___   __  __ _  ___ _ __   ___ _ __ __ _| |_ ___  _ __  #
# | | '_ \| __\ \ / / / _` |/ _ \ '_ \ / _ \ '__/ _` | __/ _ \| '__| #
# | | |_) | |_ \ V / | (_| |  __/ | | |  __/ | | (_| | || (_) | |    #
# |_| .__/ \__| \_/   \__, |\___|_| |_|\___|_|  \__,_|\__\___/|_|    #
#   | |         ______ __/ |                                         #
#   |_|        |______|___/                                          #
#                                                                    #
#                                                                    #
######################################################################
'''

def grab(url):
    try:
        if url.endswith('.m3u') or url.endswith('.m3u8') or ".ts" in url or ".mpd" in url:
            return url

        session = streamlink.Streamlink()
        streams = session.streams(url)
        logger.debug("URL Streams %s: %s", url, streams)
        if "best" in streams:
            return streams["best"].url
        return None
    except streamlink.exceptions.NoPluginError as err:
        logger.error("URL Error No PluginError %s: %s", url, err)
        return url
    except streamlink.StreamlinkError as err:
        logger.error("URL Error %s: %s", url, err)
        return None


def check_url(url):
    try:
        response = requests.head(url, timeout=15)
        if response.status_code == 200:
            logger.debug("URL Streams %s: %s", url, response)
            return True
    except requests.exceptions.RequestException as err:
        pass
    
    try:
        response = requests.head(url, timeout=15, verify=False)
        if response.status_code == 200:
            logger.debug("URL Streams %s: %s", url, response)
            return True
    except requests.exceptions.RequestException as err:
        logger.error("URL Error %s: %s", url, err)
        return None
    
    return False

channel_data = []
channel_data_json = []

channel_info = os.path.abspath(os.path.join(os.path.dirname(__file__), '../channel_info.txt'))

with open(channel_info) as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('~~'):
            continue
        if not line.startswith('http:') and len(line.split("|")) >= 5:
            line = line.split('|')
            ch_name = line[0].strip()
            grp_title = line[1].strip().title()
            tvg_logo = line[2].strip()
            tvg_id = line[3].strip()
            kid = line[4].strip() if len(line) > 4 else ""
            key = line[5].strip() if len(line) > 5 else ""
            license = line[6].strip() if len(line) > 6 else ""
            channel_data.append({
                'type': 'info',
                'ch_name': ch_name,
                'grp_title': grp_title,
                'tvg_logo': tvg_logo,
                'tvg_id': tvg_id,
                'kid': kid,
                'key': key,
                'license': license
            })
        else:
            link = grab(line)
            if link and check_url(link):
                channel_data.append({
                    'type': 'link',
                    'url': link
                })

def process_license(license):
    if license.startswith('{') and license.endswith('}'):
        # Assume it's a JSON string
        return f'{license}'
    else:
        # Assume it's a URL
        return license

with open("playlist.m3u8", "w") as f:
    f.write(banner)
    f.write(f'\n#EXTM3U')

    prev_item = None

    for item in channel_data:
        if item['type'] == 'info':
            prev_item = item
        if item['type'] == 'link' and item['url']:
            if item['url'].endswith('.mpd'):
                f.write(f'\n#EXTINF:-1 group-title="{prev_item["grp_title"]}" tvg-logo="{prev_item["tvg_logo"]}" tvg-id="{prev_item["tvg_id"]}", {prev_item["ch_name"]}')
                f.write('\n')
                f.write(f'#KODIPROP:inputstream.adaptive.license_type=org.w3.clearkey')
                f.write('\n')
                if prev_item["kid"] and prev_item["key"]:
                    f.write(f'#KODIPROP:inputstream.adaptive.license_key={prev_item["kid"]}:{prev_item["key"]}')
                elif prev_item["license"]:
                    f.write(f'#KODIPROP:inputstream.adaptive.license_key={process_license(prev_item["license"])}')
                f.write('\n')
                f.write(f'#KODIPROP:inputstream.adaptive.manifest_type=mpd')
                f.write('\n')
                f.write(f'#KODIPROP:mimetype=application/dash+xml')
                f.write('\n')
                f.write(item['url'])
                f.write('\n')
            else:
                f.write(f'\n#EXTINF:-1 group-title="{prev_item["grp_title"]}" tvg-logo="{prev_item["tvg_logo"]}" tvg-id="{prev_item["tvg_id"]}", {prev_item["ch_name"]}')
                f.write('\n')
                f.write(item['url'])
                f.write('\n')

prev_item = None

for item in channel_data:
    if item['type'] == 'info':
        prev_item = item
    if item['type'] == 'link' and item['url']:
        channel_data_json.append({
            "id": prev_item["tvg_id"],
            "name": prev_item["ch_name"],
            "alt_names": [""],
            "network": "",
            "owners": [""],
            "country": "AR",
            "subdivision": "",
            "city": "Buenos Aires",
            "broadcast_area": [""],
            "languages": ["spa"],
            "categories": [prev_item["grp_title"]],
            "is_nsfw": False,
            "launched": "2016-07-28",
            "closed": "2020-05-31",
            "replaced_by": "",
            "website": item['url'],
            "logo": prev_item["tvg_logo"]
        })

with open("playlist.json", "w") as f:
    json_data = json.dumps(channel_data_json, indent=2)
    f.write(json_data)
