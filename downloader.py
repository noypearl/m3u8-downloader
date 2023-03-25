import m3u8
import subprocess
import requests
import os
import time
import random
import argparse

parser = argparse.ArgumentParser(description='Download an m3u8 file and convert it to an mp4 video.')
# for example for my own website - put the one that starts with steam.mux.com XD
parser.add_argument('url', type=str, help='URL of the m3u8 playlist file to download.')
parser.add_argument('output_filename', type=str, help='Name of the mp4 final video')

args = parser.parse_args()

url = args.url
output_filename = args.output_filename

proxies = {
   'http': 'http://localhost:8080',
   'https':'http://localhost:8080'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/110.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'Te': 'trailers'
}

def download_m3u8(m3u8_master_url, output_filename):
    response = requests.get(m3u8_master_url, headers=headers, proxies=proxies, verify=False)
    m3u8_data = response.text

    m3u8_master = m3u8.loads(m3u8_data)
    playlist_url = m3u8_master.playlists[1].absolute_uri
    response = requests.get(playlist_url, headers=headers, proxies=proxies, verify=False)
    m3u8_playlist = m3u8.loads(response.text)

    # Download each segment and combine them into one file
    counter = 0
    # random string to support multiple script runs
    random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=5))
    temp_name = f"temp_{counter}_{random_string}.ts"
    with open(temp_name, 'wb') as f:
        for segment in m3u8_playlist.segments:
            time.sleep(random.random())
            segment_url = segment.absolute_uri
            response = requests.get(segment_url, headers=headers, proxies=proxies, verify=False)
            if response.status_code == 404:
                print(f"got 404 response from a segment. Stopping. {response.content}") # TODO - implement retry mechanism / cache for already downloaded segments
                break
            counter+=1
            print(f"downloading {counter}/{len(m3u8_playlist.segments)}")
            f.write(response.content)
            f.flush()
            os.fsync(f.fileno())

    print('Video saved to:', temp_name)
    print(f'Converting {temp_name} to {output_filename} ')
    command = ["ffmpeg", "-i", temp_name, "-c:v", "libx264", output_filename]
    subprocess.call(command)
    
download_m3u8(url, output_filename)