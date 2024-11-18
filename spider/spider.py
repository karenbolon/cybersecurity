
import sys
import os
import re
import argparse
import requests
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse

DEFAULT_DEPTH = 5
DEFAULT_PATH = './data/'
EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')


'''
-function gets HTML content from URL
-raise_for_status() is a built in method for checking
status codes
'''
def	fetch_data(url):
	try:
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
			}
		data = requests.get(url, headers=headers)
		data.raise_for_status()
		return data.text
	except requests.exceptions.RequestException as e:
		print(f"Error fetching URL {url}: {e}")
		return None

'''extracting images'''
def	extract_images(data, path):
	soup = BeautifulSoup(data, 'html.parser')
	image_list = []
	for img in soup.find_all('img', src=True):
		img_url = urljoin(path, img['src']) #build full URL for image
		if img_url.lower().endswith(EXTENSIONS):
			image_list.append(img_url)
	return image_list


'''download and save image'''
def	saving_images(url, path):
	try:
#		headers = {
#			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
#			}
		data = requests.get(url, stream=True)#, headers=headers)
		data.raise_for_status()
		file_name = os.path.basename(urlparse(url).path)
		full_path = os.path.join(path, file_name)
		with open(full_path,'wb') as file:
			for item in data:
				file.write(item)
	except requests.exceptions.RequestException as e:
		print(f"Error saving image {url}: {e}")


'''parse website for links with option for parsing recursively and
download images'''
def parse(url, path, level, downloaded=None):
	print(f"parsing level: {level}")
	if downloaded is None:
		downloaded = set()#initialises downloaded on first call
	if level < 0 or url in downloaded:
		return
	downloaded.add(url)
	data = fetch_data(url)
	if not data:
		return
	images = extract_images(data, url)
	os.makedirs(path, exist_ok=True)
	for img in images:
		saving_images(img, path)
	soup = BeautifulSoup(data, 'html.parser')
	for a_tag in soup.find_all('a', href=True):
		next_url = urljoin(url, a_tag['href']) #build full URL for image
		if urlparse(next_url).netloc == urlparse(url).netloc:
			parse(next_url, path, level - 1, downloaded)

'''
if __name__=="__main__": ensures the code is only executed
when the script is run directly and not when it's imported
as a module
'''
def main():
	# Initialize argparse to parse arguments in the terminal
	parser = argparse.ArgumentParser(description="Download images from a URL")
	parser.add_argument("url", help="URL to start scraping from.")
	parser.add_argument("-r", action="store_true", help="Recursively scrape images.")
	parser.add_argument("-l", type=int, default=DEFAULT_DEPTH, help="Maximum depth for recursion.")
	parser.add_argument("-p", type=str, default=DEFAULT_PATH, help="Path to save images.")
	args = parser.parse_args()

	#it was faster to run if I saved the arguments as variables
	url = args.url
	recursive = args.r
	depth = args.l
	path = os.path.abspath(args.p)#checks for absolute path

	if recursive:
		parse(url, path, depth)
	else:
		data = fetch_data(url)
		if not data:
			return
		images = extract_images(data, url)
		os.makedirs(path, exist_ok=True)

if __name__=="__main__":
	main()