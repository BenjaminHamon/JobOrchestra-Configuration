import logging

import pymongo


logger = logging.getLogger("Database")


def register_commands(subparsers):
	command_parser = subparsers.add_parser("initialize-database", help = "initialize the database")
	command_parser.set_defaults(handler = initialize_database)


def initialize_database(application, arguments): # pylint: disable = unused-argument
	if application.database_uri.startswith("json://"):
		initialize_json_database()
	elif application.database_uri.startswith("mongodb://"):
		initialize_mongo_database(application.database_uri, application.database_authentication)
	else:
		raise ValueError("Unsupported database uri '%s'" % application.database_uri)


def initialize_json_database():
	pass


def initialize_mongo_database(database_uri, database_authentication):
	logger.info("Initializing Mongo database (Uri: '%s')", database_uri)
	database = pymongo.MongoClient(database_uri, **database_authentication).get_database()

	print("")

	logger.info("Creating run index")
	database["run"].create_index("identifier", name = "identifier_unique", unique = True)
	logger.info("Creating job index")
	database["job"].create_index("identifier", name = "identifier_unique", unique = True)
	logger.info("Creating task index")
	database["task"].create_index("identifier", name = "identifier_unique", unique = True)
	logger.info("Creating user index")
	database["user"].create_index("identifier", name = "identifier_unique", unique = True)
	logger.info("Creating worker index")
	database["worker"].create_index("identifier", name = "identifier_unique", unique = True)
