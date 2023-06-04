import os
import threading
import core
import time
import taglib
import random
from threading import Thread
from core import TITLE_KEY, UNKNOWN_DIC


NEW_EVENT_TIMEOUT = 5 # in seconds
thread_mkdir_lock = threading.Lock()
new_event_condition = threading.Condition()
events = []
should_stop_events = False

def process_music_file(music_file_absolute_path: str, music_lib_dest: str, grouping_order: list[str], fix_filenames: bool):

	time.sleep(random.random() * 3)

	send_event(f'Zaczynam procesować "{music_file_absolute_path}"')

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

	send_event(f'Zmieniono "{music_file_absolute_path}" ===> "{new_path}"')


def run(music_lib_path: str, music_lib_dest: str, grouping_order: list[str], fix_filenames: bool):

	global should_stop_events

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

	should_stop_events = True
	event_processing_thread.join()

	core.delete_empty_dirs_from_folder(music_lib_path)


def generate_new_destination_for_music_file(music_file_path: str, path_prefix: str, grouping_order: list[str]) -> str:

	new_destination = path_prefix

	with taglib.File(music_file_path, save_on_exit=False) as song:
		for group_type in grouping_order:
			group_value = song.tags.get(
				group_type, [UNKNOWN_DIC.get(group_type, 'Unknown')])[0]
			new_destination = os.path.join(new_destination, group_value)

	return new_destination


def fix_music_file_name_from_tag(music_file_path: str) -> str:

	with taglib.File(music_file_path, save_on_exit=False) as song:
		name, file_extension = os.path.splitext(
			os.path.basename(music_file_path))
		return song.tags.get(TITLE_KEY, [name])[0] + file_extension


def send_event(msg: str):
	# Próbujemy dostać się do listy eventów
	with new_event_condition:

		events.append(msg)
		new_event_condition.notify()


def proccess_event_list():
	global should_stop_events
	event_counter = 1
	while not should_stop_events or events:
		with new_event_condition:
			while not events and not should_stop_events:
				new_event_condition.wait(NEW_EVENT_TIMEOUT)

			if events:
				print(f'#EVENT{event_counter}: {events.pop(0)}')
				event_counter += 1
