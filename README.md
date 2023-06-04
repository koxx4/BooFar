# BooFar
BooFar is a command line utility that assists in organizing a local music collection/library. The program is capable of arranging files into folders corresponding to artists/genres/albums. It can also retrieve missing album covers and has the ability to interactively populate ID3 tags using Musicbrainz data. BooFar is written in python.
# Features
- Organize music files by albums and artists ✔️
- Fetch missing album cover arts ✔️
- Fetch missing metadata ✔️
- Fix weird artifacts in filenames (for example when music file was download from internet using YoutubeDL) ✔️
- Convert between various formats using ffmpeg ❌ (or you can use ffmpeg directly???)

# Terminal output
The output format consists of event messages that provide information about the program's progress. Each event follows the format:

- `{n}` represents the unique event number.
- `{Event message}` describes the event, such as "Starting to process" or "Changed", along with the relevant file path.

Here are three fictional lines representing the program's output:

1. `#EVENT1: Starting to process "/home/user/Music/song1.mp3"`
2. `#EVENT2: Changed "/home/user/Music/song2.mp3" ===> "/home/user/Music/NewLocation/song2.mp3"`
3. `#EVENT3: Starting to process "/home/user/Music/song3.mp3"`

These lines demonstrate the event numbers, event messages, and the associated file paths in the output.

# Threading
## Threads and Critical Sections

This module utilizes threads to process music files in parallel, improving the overall throughput. The following sections describe the critical sections used in the code to ensure thread safety.

### `thread_mkdir_lock` (Mutex)

The `thread_mkdir_lock` is a mutex (mutual exclusion) lock used to ensure thread-safe creation of directories. It is acquired before creating directories and released after the operation is completed. This lock prevents multiple threads from concurrently creating the same directory, avoiding conflicts and race conditions.

### `new_event_condition` (Condition)

The `new_event_condition` is a condition variable used to synchronize the access to the `events` list, which stores event messages. The condition variable allows threads to wait for new events and to be notified when new events are available. It ensures that the event list is accessed in a controlled and synchronized manner, preventing race conditions and allowing efficient event processing.

To access the `events` list, the thread acquires the `new_event_condition` lock and waits until there are events to process. When new events are added to the list, the thread is notified and proceeds to process the events, ensuring that events are processed in the order they were added.

### `SHOULD_STOP_EVENTS` (Flag)

The `SHOULD_STOP_EVENTS` flag is a shared variable used to control the event processing loop. It is set to `True` when the event processing should be stopped. The flag is accessed by multiple threads, and its value is checked in the event processing loop condition. By setting the flag to `True`, the threads can gracefully stop event processing and exit the loop.

The critical sections and synchronization mechanisms mentioned above ensure proper coordination and thread safety during the execution of the code. They prevent race conditions, conflicts, and ensure that shared resources are accessed and modified safely by multiple threads.
