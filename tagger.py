import os
import core
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDAT
import musicbrainzngs

musicbrainzngs.set_useragent("BooFar", "1.0", "https://github.com/koxx4/BooFar")

def run(target_dir):

	music_files = list(filter(lambda f: file_has_no_id3_tags(f), core.get_music_files_paths(target_dir)))
	print(music_files)

	for f in music_files:
		search_and_display_results(f)


def file_has_no_id3_tags(file_path) -> bool:
	try:
		audio = ID3(file_path)
	except:
		return True

	return audio and "TIT2" not in audio and "TPE1" not in audio and "TALB" not in audio
	
def set_id3_tags(recording_data, file_path):
	audio = ID3(file_path)
	audio["TIT2"] = TIT2(encoding=3, text=recording_data['title'])
	audio["TPE1"] = TPE1(encoding=3, text=recording_data['artist'])
	audio["TALB"] = TALB(encoding=3, text=recording_data['album'])
	audio["TDAT"] = TDAT(encoding=3, text=recording_data['date'])
	audio.save()
	print('Saved!')

def search_and_display_results(file_name, offset = 0):
	results = musicbrainzngs.search_recordings(query=os.path.basename(file_name), limit=12, offset=offset)
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

			print(f'Propozycja #{i+1}: {label_text}')
			data.append({'artist': artist, 'title': title, 'album': album, 'date': release_date if release_date != 'XXXX' else None})
		
		choice = input('\nWybierz propozcyję (wpisz numer) lub 0 aby pominąć: ')
		try:
			choice = int(choice)
		except:
			return
		
		if (choice <= 0):
			return
		
		set_id3_tags(recording_data=data[int(choice)-1], file_path=file_name)