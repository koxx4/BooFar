import core
import organizer
import tagger
import cover_finder

if __name__ == '__main__':

	arguments = core.define_and_build_program_arguments()

	if not arguments.destination:
		arguments.destiantion = arguments.target

	if arguments.organize:
		organizer.run(arguments.target, arguments.destination,
					arguments.group, arguments.fix_filenames)

	if arguments.id3_tags:
		tagger.run(arguments.target)

	if arguments.album_artworks:
		cover_finder.run(arguments.target)