import sys
import os
import mutagen
import mutagen.wave

def run(music_lib_path: str):
	print(f'You defined your music lib at {music_lib_path}')

	music_files = os.listdir(music_lib_path)

	for file in music_files:
		file = f'{music_lib_path}/{file}'
		music_file: mutagen.FileType | None = mutagen.File(file)

		if not music_file:
			print(f'Failed to load {file}')
			music_file = mutagen.wave.WAVE(file)
			if not music_file:
				print('Even parsing as WAV failed!')
				continue

		print(music_file.pprint())



if __name__ == '__main__':
	
	if len(sys.argv) <= 1:
		print("Wrong arguments count")
		exit(1)

	run(sys.argv[1])