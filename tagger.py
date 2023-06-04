'''
This module contains funcionalities realted to interactive manual
music files tagging using data fetched from Musicbrainz API.
'''
import os
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDAT
import musicbrainzngs
import core

musicbrainzngs.set_useragent("BooFar", "1.0", "https://github.com/koxx4/BooFar")

def run(target_dir: str):
	'''
	Starts interactive ID3 tags searching and embeding

	:param target_dir: The path to the target directory.
	:type target_dir: str
	'''
	music_files = list(filter(file_has_no_id3_tags, core.get_music_files_paths(target_dir)))

	for file in music_files:
		search_and_display_results(file)


def file_has_no_id3_tags(file_path) -> bool:
	"""
	Checks if a file has no ID3 tags.

	:param file_path: The path to the file to be checked.
	:type file_path: str
	:return: True if the file has no ID3 tags, False otherwise.
	:rtype: bool
	"""
	try:
		audio = ID3(file_path)
	except:
		return True

	return audio and "TIT2" not in audio and "TPE1" not in audio and "TALB" not in audio


def set_id3_tags(recording_data, file_path):
	"""
	Sets ID3 tags for a given audio file.

	:param recording_data: The recording data containing the tag information.
					It should have the following structure:
					{'artist': str, 'title': str, 'album': str, 'date': str}}
	:type recording_data: dict
	:param file_path: The path to the audio file.
	:type file_path: str
	"""
	audio = ID3(file_path)
	audio["TIT2"] = TIT2(encoding=3, text=recording_data['title'])
	audio["TPE1"] = TPE1(encoding=3, text=recording_data['artist'])
	audio["TALB"] = TALB(encoding=3, text=recording_data['album'])
	audio["TDAT"] = TDAT(encoding=3, text=recording_data['date'])
	audio.save()
	print('Saved!')


def search_and_display_results(file_name: str, offset: int = 0):
	"""
	Searches for recordings in Muscibrainz API based on a file name and displays an interactive search results.
	Only first 12 results are presented. Selected result will be saved into ID3 tags of a music file. 

	:param file_name: The name of the music file to search for in Musicbrainz API.
	:type file_name: str
	:param offset: The offset for pagination of search results, defaults to 0.
	:type offset: int, optional
	"""
	results = musicbrainzngs.search_recordings(
		query=os.path.basename(file_name), limit=12, offset=offset)
	data = []

	if 'recording-list' in results:
		recordings = enumerate(results['recording-list'])
		print(f'\n\nChoose tags for {os.path.basename(file_name)}')

		for i, recording in recordings:
			print('-----------------------------')
			artist = recording['artist-credit'][0]['artist']['name']
			title = recording['title']
			album = recording['release-list'][0]['title']
			release_date = 'XXXX'
			if 'date' in recording['release-list'][0]:
				release_date = recording['release-list'][0]['date']

			label_text = f"Artist: {artist}, Title: {title}, Album: {album}, Release Date: {release_date}"

			print(f'#{i+1}: {label_text}')
			data.append({'artist': artist, 'title': title, 'album': album,
						'date': release_date if release_date != 'XXXX' else None})

		choice = input(
			'\nChoose proposed data (type in a number or 0 to skip): ')
		try:
			choice = int(choice)
		except:
			return

		if (choice <= 0):
			return

		set_id3_tags(recording_data=data[int(choice)-1], file_path=file_name)
