import os
import taglib
import threading
import core
from threading import Thread
from core import TITLE_KEY, UNKNOWN_DIC


thread_mkdir_lock = threading.Lock()
file_moving_lock = threading.Lock()

def get_music_files_paths(music_lib_path: str) -> list[str]:

	music_files = []

	for root, _, files in os.walk(music_lib_path):
		for file_name in files:

			if not core.file_has_valid_music_extension(file_name):
				continue

			file_absolute_path = os.path.join(root, file_name)

			music_files.append(file_absolute_path)

	return music_files


def process_music_file(music_file_absolute_path: str, music_lib_dest: str, grouping_order: list[str], fix_filenames: bool):

	new_destination = generate_new_destination_for_music_file(
		music_file_absolute_path,
		music_lib_dest,
		grouping_order
	)

	thread_mkdir_lock.acquire(blocking=True)
	os.makedirs(new_destination, exist_ok=True)
	thread_mkdir_lock.release()

	if fix_filenames:
		file_name = fix_music_file_name_from_tag(music_file_absolute_path)

	file_name = file_name.replace('/', ',')
	
	file_moving_lock.acquire()
	os.rename(music_file_absolute_path, os.path.join(new_destination, file_name))
	file_moving_lock.release()

def run(music_lib_path: str, music_lib_dest: str, grouping_order: list[str], fix_filenames: bool):
	'''Organizes library specifed at music_lib_path arg using specified grouping_order.

	Arguments:
		music_lib_path -- Source of current music library that should be organized
		music_lib_dest -- Location of new organized library
		grouping_order -- Order in which directories will be created and nested
		fix_filenames -- Should program attempt to fix music filename using information
		present in tags
	'''
	music_files = get_music_files_paths(music_lib_path)

	thread_count = core.estimate_number_of_threads()

	thread_list = []

	for chunk in core.split_into_chunks(music_files, thread_count):
		for file in chunk:
			args = (file, music_lib_dest, grouping_order, fix_filenames)
			thread_list.append(Thread(target=process_music_file, args=args))
	_ = [t.start() for t in thread_list]
	_ = [t.join() for t in thread_list]
	thread_list.clear()


	core.delete_empty_dirs_from_folder(music_lib_path)

def generate_new_destination_for_music_file(music_file_path: str, path_prefix: str, grouping_order: list[str]) -> str:

	new_destination = path_prefix

	with taglib.File(music_file_path, save_on_exit=False) as song:
		for group_type in grouping_order:
			group_value = song.tags.get(group_type, [UNKNOWN_DIC.get(group_type, 'Unknown')])[0]
			new_destination = os.path.join(new_destination, group_value)

	return new_destination

def fix_music_file_name_from_tag(music_file_path: str) -> str:

	with taglib.File(music_file_path, save_on_exit=False) as song:
		name, file_extension = os.path.splitext(os.path.basename(music_file_path))
		return song.tags.get(TITLE_KEY, [name])[0] + file_extension
