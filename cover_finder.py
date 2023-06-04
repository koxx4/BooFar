import os
from get_cover_art import CoverFinder

'''
This module is responsible for finding, downloading and embeding art album covers into files
'''

def run(target_dir: str):
	"""
		Runs the process of scanning a folder to fetch and embed album covers for found music files.

		:param target_dir: The path to the folder with music files to be scanned.
		:type target_dir: str
	"""
	finder = CoverFinder()
	finder.scan_folder(target_dir)

	failed_songs = {}
	for file_path in finder.files_failed:
		file_name = os.path.basename(file_path)
		failed_songs[file_name] = file_path

	print(f'Those files were not processed beacuse of an error or missing ID3 tags: {failed_songs}')