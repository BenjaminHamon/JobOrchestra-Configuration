import re

import pymongo
import sqlalchemy

from bhamon_orchestra_model.database.json_database_administration import JsonDatabaseAdministration
from bhamon_orchestra_model.database.json_database_client import JsonDatabaseClient
from bhamon_orchestra_model.database.mongo_database_administration import MongoDatabaseAdministration
from bhamon_orchestra_model.database.mongo_database_client import MongoDatabaseClient
from bhamon_orchestra_model.database.sql_database_administration import SqlDatabaseAdministration
from bhamon_orchestra_model.database.sql_database_client import SqlDatabaseClient


def create_database_administration_factory(database_uri, database_authentication, database_metadata):
	if database_uri.startswith("json://"):
		return lambda: JsonDatabaseAdministration(re.sub("^json://", "", database_uri))
	if database_uri.startswith("mongodb://"):
		return lambda: MongoDatabaseAdministration(pymongo.MongoClient(database_uri, **database_authentication))
	if database_uri.startswith("postgresql://"):
		database_uri_with_authentication = _add_authentication(database_uri, database_authentication)
		database_engine = sqlalchemy.create_engine(database_uri_with_authentication)
		return lambda: SqlDatabaseAdministration(database_engine.connect(), database_metadata)
	raise ValueError("Unsupported database uri '%s'" % database_uri)


def create_database_client_factory(database_uri, database_authentication, database_metadata):
	if database_uri.startswith("json://"):
		return lambda: JsonDatabaseClient(re.sub("^json://", "", database_uri))
	if database_uri.startswith("mongodb://"):
		return lambda: MongoDatabaseClient(pymongo.MongoClient(database_uri, **database_authentication))
	if database_uri.startswith("postgresql://"):
		database_uri_with_authentication = _add_authentication(database_uri, database_authentication)
		database_engine = sqlalchemy.create_engine(database_uri_with_authentication)
		return lambda: SqlDatabaseClient(database_engine.connect(), database_metadata)
	raise ValueError("Unsupported database uri '%s'" % database_uri)


def _add_authentication(database_uri, database_authentication):
	if database_authentication.get("username", None) is None:
		return database_uri
	if database_authentication.get("password", None) is None:
		return database_uri

	authentication_index = database_uri.index("://") + len("://")
	authentication = database_authentication["username"] + ":" + database_authentication["password"]
	authentication += "@localhost" if database_uri[authentication_index] == "/" else "@"
	return database_uri[:authentication_index] + authentication + database_uri[authentication_index:]
