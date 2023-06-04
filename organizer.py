'''
This module is responsible for orginzing music files in provided target folder.
'''
import os
import threading
from threading import Thread
import taglib
import core
from core import TITLE_KEY, UNKNOWN_DIC


NEW_EVENT_TIMEOUT = 5 # in seconds
SHOULD_STOP_EVENTS = False
thread_mkdir_lock = threading.Lock()
new_event_condition = threading.Condition()
events = []

def process_music_file(music_file_absolute_path: str, music_lib_dest: str, grouping_order: list[str], fix_filenames: bool):
	"""
	Processes a music file by generating a new destination, renaming the file, and sending events.

	:param music_file_absolute_path: The absolute path of the music file.
	:type music_file_absolute_path: str
	:param music_lib_dest: The destination path for the music library.
	:type music_lib_dest: str
	:param grouping_order: The order of grouping tags for organizing the music files.
	:type grouping_order: list[str]
	:param fix_filenames: A flag indicating whether to fix filenames based on tags.
	:type fix_filenames: bool
	"""

	send_event(f'Starting to process "{music_file_absolute_path}"')

	new_destination = generate_new_destination_for_music_file(
		music_file_absolute_path,
		music_lib_dest,
		grouping_order
	)

	thread_mkdir_lock.acquire(blocking=True)
	os.makedirs(new_destination, exist_ok=True)
	thread_mkdir_lock.release()

	file_name = os.path.basename(music_file_absolute_path)

	if fix_filenames:
		file_name = fix_music_file_name_from_tag(music_file_absolute_path)
		file_name = file_name.replace('/', ',')

	new_path = os.path.join(new_destination, file_name)
	os.rename(music_file_absolute_path, new_path)

	send_event(f'Changed "{music_file_absolute_path}" ===> "{new_path}"')


def run(music_lib_path: str, music_lib_dest: str, grouping_order: list[str], fix_filenames: bool):
	"""
	Runs the music processing flow by processing music files, generating new destinations, and organizing the music library.
	This function spawns multiple threads processing files in order to achieve maximal throughput .

	:param music_lib_path: The path to the music library.
	:type music_lib_path: str
	:param music_lib_dest: The destination path for the music library.
	:type music_lib_dest: str
	:param grouping_order: The order of grouping tags for organizing the music files.
	:type grouping_order: list[str]
	:param fix_filenames: A flag indicating whether to fix filenames based on tags.
	:type fix_filenames: bool
	"""

	global SHOULD_STOP_EVENTS

	if not music_lib_dest:
		music_lib_dest = music_lib_path

	music_files = core.get_music_files_paths(music_lib_path)

	thread_count = core.estimate_number_of_threads()

	thread_list = []

	event_processing_thread = Thread(target=proccess_event_list)
	event_processing_thread.start()

	for chunk in core.split_into_chunks(music_files, thread_count):
		for file in chunk:
			args = (file, music_lib_dest, grouping_order, fix_filenames)
			thread_list.append(Thread(target=process_music_file, args=args))
		_ = [t.start() for t in thread_list]
		_ = [t.join() for t in thread_list]
		thread_list.clear()

	SHOULD_STOP_EVENTS = True
	event_processing_thread.join()

	core.delete_empty_dirs_from_folder(music_lib_path)


def generate_new_destination_for_music_file(music_file_path: str, path_prefix: str, grouping_order: list[str]) -> str:
	"""
	Generates a new destination path for a music file based on the provided grouping order.

	:param music_file_path: The path of the music file.
	:type music_file_path: str
	:param path_prefix: The prefix path for the new destination.
	:type path_prefix: str
	:param grouping_order: The order of grouping tags for organizing the music files.
	:type grouping_order: list[str]
	:return: The new destination path.
	:rtype: str
	"""
	new_destination = path_prefix

	with taglib.File(music_file_path, save_on_exit=False) as song:
		for group_type in grouping_order:
			group_value = song.tags.get(
				group_type, [UNKNOWN_DIC.get(group_type, 'Unknown')])[0]
			new_destination = os.path.join(new_destination, group_value)

	return new_destination


def fix_music_file_name_from_tag(music_file_path: str) -> str:
	"""
	Fixes the music file name based on the tags that are present in a music file.

	:param music_file_path: The path of the music file.
	:type music_file_path: str
	:return: The fixed music file name.
	:rtype: str
	"""

	with taglib.File(music_file_path, save_on_exit=False) as song:
		name, file_extension = os.path.splitext(
			os.path.basename(music_file_path))
		return song.tags.get(TITLE_KEY, [name])[0] + file_extension


def send_event(msg: str):
	"""
	Sends an event message.

	:param msg: The event message.
	:type msg: str
	"""
	with new_event_condition:

		events.append(msg)
		new_event_condition.notify()


def proccess_event_list():
	"""
	Processes the event list by printing the events.
	"""
	event_counter = 1

	while not SHOULD_STOP_EVENTS or events:
		with new_event_condition:
			while not events and not SHOULD_STOP_EVENTS:
				new_event_condition.wait(NEW_EVENT_TIMEOUT)

			if events:
				print(f'#EVENT{event_counter}: {events.pop(0)}')
				event_counter += 1
