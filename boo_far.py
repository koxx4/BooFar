import core
import organizer

if __name__ == '__main__':

	arguments = core.define_and_build_program_arguments()

	if not arguments.destination:
		arguments.destination = arguments.target

	organizer.run(arguments.target, arguments.destination, arguments.group, arguments.fix_filenames)
