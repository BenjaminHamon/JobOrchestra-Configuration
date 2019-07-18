import logging

import pymongo


logger = logging.getLogger("Database")


def register_commands(subparsers):
	command_parser = subparsers.add_parser("initialize-database", help = "initialize the build database")
	command_parser.set_defaults(handler = initialize_database)


def initialize_database(application, arguments): # pylint: disable = unused-argument
	if arguments.database == "json":
		initialize_json_database()
	elif arguments.database.startswith("mongodb://"):
		initialize_mongo_database(arguments.database)
	else:
		raise ValueError("Unsupported database uri '%s'" % arguments.database)


def initialize_json_database():
	pass


def initialize_mongo_database(database_uri):
	logger.info("Initializing Mongo database (Uri: '%s')", database_uri)
	database = pymongo.MongoClient(database_uri).get_database()

	print("")

	logger.info("Creating build index")
	database["build"].create_index("identifier", name = "identifier_unique", unique = True)
	logger.info("Creating job index")
	database["job"].create_index("identifier", name = "identifier_unique", unique = True)
	logger.info("Creating task index")
	database["task"].create_index("identifier", name = "identifier_unique", unique = True)
	logger.info("Creating user index")
	database["user"].create_index("identifier", name = "identifier_unique", unique = True)
	logger.info("Creating worker index")
	database["worker"].create_index("identifier", name = "identifier_unique", unique = True)
