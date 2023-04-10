import os
import taglib
import core
from core import TITLE_KEY, UNKNOWN_DIC

def run(music_lib_path: str, music_lib_dest: str, grouping_order: list[str], fix_filenames: bool):

	if not music_lib_dest:
		music_lib_dest = music_lib_path

	for root, _, files in os.walk(music_lib_path):
		for file_name in files:
			file_absolute_path = os.path.join(root, file_name)

			if not core.file_has_valid_music_extension(file_name):
				continue

			new_destination = generate_new_destination_for_music_file(
				file_absolute_path,
				music_lib_dest,
				grouping_order
			)

			print(new_destination)
			os.makedirs(new_destination, exist_ok=True)

			if fix_filenames:
				file_name = fix_music_file_name_from_tag(file_absolute_path, file_name)

			file_name = file_name.replace('/', ',')
			os.rename(file_absolute_path, os.path.join(new_destination, file_name))

			core.delete_empty_dirs_from_folder(music_lib_path)

def generate_new_destination_for_music_file(music_file_path: str, path_prefix: str, grouping_order: list[str]) -> str:

	new_destination = path_prefix

	with taglib.File(music_file_path, save_on_exit=False) as song:
		for group_type in grouping_order:
			group_value = song.tags.get(group_type, [UNKNOWN_DIC.get(group_type, 'Unknown')])[0]
			new_destination = os.path.join(new_destination, group_value)

	return new_destination

def fix_music_file_name_from_tag(music_file_path: str, original_name: str) -> str:

	with taglib.File(music_file_path, save_on_exit=False) as song:
		name, file_extension = os.path.splitext(original_name)
		return song.tags.get(TITLE_KEY, [name])[0] + file_extension

if __name__ == '__main__':

	arguments = core.define_and_build_program_arguments()

	run(arguments.target, arguments.destination, arguments.group, arguments.fix_filenames)