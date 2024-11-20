
import os
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

HEADERS = {	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
			AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
			}
DEFAULT_DEPTH = 5
DEFAULT_PATH = './data/'
EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')


'''
-function gets HTML content from URL
-header tricks other site to think we are a browser, help your requests appear 
	less "bot-like."
-timeout=times out if not bytes recieved otherwise we could be left hanging if no response
-raise_for_status() is a built in method for checking
status codes, if successful, it returns text (per my request)
and if not, it raises the RequestException response

'''
def	fetch_data(url):
	try:

		data = requests.get(url, headers=HEADERS, timeout=3) 

		data.raise_for_status()
		return data.text
	except requests.exceptions.RequestException as e:
		print(f"Error fetching URL {url}: {e}")
		return None

'''
extracting images
urljoin builds full URL path for image
'''
def	extract_images(data, path):
	soup = BeautifulSoup(data, 'html.parser')
	image_list = []
	for img in soup.find_all('img', src=True):
		img_url = urljoin(path, img['src'])
		if img_url.lower().endswith(EXTENSIONS):
			image_list.append(img_url)
	return image_list


'''download and save image
iter_content: 
	-it is recommended to process in batches when retrieving data, 
		chunk_size can be changed
	-it will automatically decode the gzip and deflate transfer-encodings too
'''
def	saving_images(url, path):
	try:
		data = requests.get(url, stream=True, headers=HEADERS, timeout=3)
		data.raise_for_status()
		file_name = os.path.basename(urlparse(url).path)
		full_path = os.path.join(path, file_name)
		with open(full_path,'wb') as file:
			for chunk in data.iter_content(chunk_size=128):
				file.write(chunk)
	except requests.exceptions.RequestException as e:
		print(f"Error saving image {url}: {e}")


'''parse website for links and download images, it checks if
image has been downloaded yet

netloc: Contains the network location - which includes the 
domain itself (and subdomain if present), the port number, 
along with an optional credentials in form of username:password. 
<user>:<password>@<host>:<port>  we check if current==next url to ensure
we are still on the same website/domain
'''
def parse(url, path, level, visited_links=None):
	if visited_links is None:
		visited_links = set()
	if level < 0 or url in visited_links:
		return
	print(f"parsing level: {level}")
	visited_links.add(url)
	data = fetch_data(url)
	if not data:
		return
	images = extract_images(data, url)
	os.makedirs(path, exist_ok=True)
	for img in images:
		saving_images(img, path)
	soup = BeautifulSoup(data, 'html.parser')
	for a_tag in soup.find_all('a', href=True):
		#this finds all <a> or anchor tags that have href attribute
		next_url = urljoin(url, a_tag['href']) 
		#build full URL for image
		if urlparse(next_url).netloc == urlparse(url).netloc:
			#this check ensures we stay on the specified website and don't 
			# check external/different sites
			parse(next_url, path, level - 1, visited_links)

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
	#converts path to absolute path to help with libraries.  Some require absolute path
	path = os.path.abspath(args.p)

	if not recursive and depth != DEFAULT_DEPTH:
		print("Error: The -l option can only be used with the -r flag.")
		return
		
	if recursive:
		parse(url, path, depth)
	else:
		data = fetch_data(url)
		if not data:
			return
		images = extract_images(data, url)
		os.makedirs(path, exist_ok=True)
		for img in images:
			saving_images(img, path)

if __name__=="__main__":
	main()