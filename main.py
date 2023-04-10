import sys
import os
import argparse
import taglib

AUTHOR_KEY = 'ARTIST'
ALBUM_KEY = 'ALBUM'
GENRE_KEY = 'GENRE'
DATE_KEY = 'DATE'
TITLE_KEY = 'TITLE'

UNKNOWN_DIC = {AUTHOR_KEY: 'Nieznany artysta', ALBUM_KEY: 'Nieznany album', GENRE_KEY: 'Nieznany gatunek'} 
ALLOWED_MUSIC_EXT = ['.mp3', '.wav', '.flac', '.ogg', '.opus', '.m4a']

def run(music_lib_path: str, music_lib_dest: str, grouping_order: list[str], fix_filenames: bool):

	# Apply default grouping if grouping was not specified
	if not grouping_order:
		grouping_order = [AUTHOR_KEY, ALBUM_KEY, GENRE_KEY]

	for root, dirs, files in os.walk(music_lib_path, topdown=True):
		for file_name in files:
			file_path = os.path.join(root, file_name)

			if not any(file_path.endswith(ext) for ext in ALLOWED_MUSIC_EXT):
				continue

			print(f'--> CHECKING {file_path}')

			with taglib.File(file_path, save_on_exit=False) as song:

				new_destination = music_lib_path

				for group_type in grouping_order:
					group_value = song.tags.get(group_type, ['Nieznany'])[0]
					new_destination = os.path.join(new_destination, group_value)
				
				os.makedirs(new_destination, exist_ok=True)

				#Fix filenames if enabled and if even possible
				if fix_filenames and TITLE_KEY in song.tags:
					file_extension = os.path.splitext(file_name)[1]
					file_name = song.tags.get(TITLE_KEY)[0] + file_extension

				file_name = file_name.replace('/', ',')
				os.rename(file_path, os.path.join(new_destination, file_name))


if __name__ == '__main__':

	# Tworzenie parsera argumentów
	parser = argparse.ArgumentParser(description='BooFar - aplikacja organizująca bibliotekę muzyczną.')

	# Dodawanie flag dla grupowania po artyście, albumie i gatunku
	parser.add_argument('-g', '--group', type=str, help='Zdefiniuj grupowanie i jego kolejność', nargs=3, choices=[AUTHOR_KEY, ALBUM_KEY, GENRE_KEY])
	parser.add_argument('-f', '--fix-filenames', action='store_true', help='Naprawia nazwę pliku bazując na nazwie zamieszczonej w tagach')

	# Dodawanie flagi dla określenia ścieżki do biblioteki muzycznej użytkownika
	parser.add_argument('-t', '--target', type=str, help='Ścieżka do biblioteki muzycznej użytkownika', required=True)

	# Parsowanie argumentów
	args = parser.parse_args()
	
	if args.target:
		run(args.target, '', args.group, args.fix_filenames)