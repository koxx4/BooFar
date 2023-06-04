''' This module contains core utilities functions and constatns used in application
'''

from argparse import ArgumentParser
from os import walk, listdir, rmdir, cpu_count, walk, path

AUTHOR_KEY = 'ARTIST'
ALBUM_KEY = 'ALBUM'
GENRE_KEY = 'GENRE'
DATE_KEY = 'DATE'
TITLE_KEY = 'TITLE'

DEFAULT_GROUPING_ORDER = [GENRE_KEY, AUTHOR_KEY, ALBUM_KEY]

UNKNOWN_DIC = {
	AUTHOR_KEY: 'Unknown artist',
	ALBUM_KEY: 'Unknown album',
	GENRE_KEY: 'Unknown genre',
	"FALLBACK": 'Unknown'
}

ALLOWED_MUSIC_EXT = ['.mp3', '.wav', '.flac', '.ogg', '.opus', '.m4a']

def estimate_number_of_threads() -> int:
	cpus = cpu_count()
	thread_count = 2

	if cpus:
		thread_count = cpus * 2

	return thread_count

def split_into_chunks(arr: list[any], chunk_size: int) -> list[list[any]]:
	chunks = []

	for i in range(0, len(arr), chunk_size):
		chunk = []
		for j in range(chunk_size):
			if j + i >= len(arr):
				break
			chunk.append(arr[j + i])
		chunks.append(chunk)

	return chunks

def get_music_files_paths(music_lib_path: str) -> list[str]:

	music_files = []

	for root, _, files in walk(music_lib_path):
		for file_name in files:

			if not file_has_valid_music_extension(file_name):
				continue

			file_absolute_path = path.join(root, file_name)

			# We ommit any possible sym links
			if path.islink(file_absolute_path):
				continue

			music_files.append(file_absolute_path)

	return music_files

def delete_empty_dirs_from_folder(path: str):
	for root, _, _ in walk(path, topdown=False):
		if not listdir(root):
			rmdir(root)

def file_has_valid_music_extension(filename: str) -> bool:
	return any(filename.endswith(ext) for ext in ALLOWED_MUSIC_EXT)

def define_and_build_program_arguments():
	'''This function contains program arguments, flags, etc. definitions.
	Arguments are parsed, validated and returned in an object.

	Returns:
		Parsed arguments build by invoking argparse.ArgumentParser.parse_args()
	'''

	# Tworzenie parsera argumentów
	parser = ArgumentParser(description='BooFar - aplikacja organizująca bibliotekę muzyczną.')

	parser.add_argument('-o', '--organize', action='store_true', help='Włącza organizowanie bibliotekii muzycznej.')
	parser.add_argument('-a', '--album-artworks', action='store_true', help='Włącza pobieranie okładen dla plików muzycznych')
	parser.add_argument('-i', '--id3-tags', action='store_true', help='Włącza tryb interaktywnego uzupełniania tagów ID3 na podstawie nazwy pliku i bazy danych Musicbrainz')

	# Dodawanie flag dla grupowania po artyście, albumie i gatunku
	parser.add_argument('-g', '--group', type=str, help='Zdefiniuj grupowanie i kolejność podczas organizowania bilbiotekii', nargs=3, choices=[AUTHOR_KEY, ALBUM_KEY, GENRE_KEY], default=DEFAULT_GROUPING_ORDER)
	parser.add_argument('-f', '--fix-filenames', action='store_true', help='Naprawia nazwę pliku bazując na nazwie zamieszczonej w tagach')

	# Dodawanie flagi dla określenia ścieżki do biblioteki muzycznej użytkownika
	parser.add_argument('-t', '--target', type=str, help='Ścieżka do biblioteki muzycznej użytkownika', required=True)
	parser.add_argument('-d', '--destination', type=str, help='Ścieżka gdzie zapisana będzie wygenerowana biblioteka')

	# Parsowanie argumentów
	return parser.parse_args()
