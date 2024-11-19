

import argparse
import sys
from PIL import Image
from PIL.ExifTags import TAGS

'''
I looked into what attributes Image objects can provide and
made a list based on EXIF data on Wiki
'''
def pull_attributes(image_path):
	try:
		image = Image.open(image_path)
		info_dict = {
			"Filename": image.filename,
			"Image Size": image.size,
			"Image Height": image.height,
			"Image Width": image.width,
			"Image Format": image.format,
			"Image Mode": image.mode,
			"Image is Animated": getattr(image, "img_is_animated", False),
			"Frames in Image": getattr(image, "n_frames", 1)
		}
		print("Attributes found:")
		for label, value in info_dict.items():
			print(f"{label}: {value}")
		return image
	except Exception as e:
		print(f"Error reading {image_path}: {e}")
		sys.exit(1)


'''
fcn processes an image object from Pillow, extracts its EXIF
metadata if found and displays it in a readable format
'''
def image_processing(image):
	try:
		exif_data = image.getexif()
		#.getexif retrieves metadata from the Image object as a dictionary
		if exif_data:
			for tag_id, value in exif_data.items():
				tag = TAGS.get(tag_id, tag_id)
				#TAGS dictionary from PIL maps numeric EXIF tag IDs to human-
				#readable tag names
				if isinstance(value, bytes):
				#some EXIF values are stores as binary data/encoded strings
				#checks if the value is of type bytes
					try:
						value = value.decode()
					except Exception:
						value = "Binary data (non-decodable)"
				print(f"{tag}: {value}")
		else:
			print ("\nno EXIF data found")
	except Exception as e:
		print(f"Error extracting EXIF data: {e}")

def	extract_non_exif_metadata(image):
	if image.info:
		for key, value in image.info.items():
			print(f"{key}: {value}")

def main():
	# Initialize argparse to parse arguments in the terminal
	parser = argparse.ArgumentParser(description="Pull metadata from Images")
	parser.add_argument("image_files", nargs='+', help="One or more image files to pull metadata from.")
	args = parser.parse_args()

	images = args.image_files

	for img in images:
		image_item = pull_attributes(img)
		image_processing(image_item)
#		extract_non_exif_metadata(image_item)

if __name__=="__main__":
	main()