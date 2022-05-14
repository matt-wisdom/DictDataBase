import os
import json
import zlib
from typing import Tuple

from .locking import ReadLock, WriteLock
from . import config



def db_paths(db_name: str) -> Tuple[str | None, str | None]:
	"""
	Return a 2-tuple:
		1: json_path: path to the json file if it exists, None otherwise

		2: ddb_path: path to the ddb file if it exists, None otherwise
	"""
	base = f"{config.storage_directory}/{db_name}"
	json_path, ddb_path = f"{base}.json", f"{base}.ddb"

	if not os.path.exists(json_path):
		json_path = None
	if not os.path.exists(ddb_path):
		ddb_path = None

	return json_path, ddb_path




def unprotected_read_json_as_dict(db_name: str) -> dict:
	"""
		Read the file at db_path from the configured storage directory.
		Make sure the file exists!
	"""

	json_path, ddb_path = db_paths(db_name)

	if json_path and ddb_path:
		raise Exception(f"DB Inconsistency: \"{db_name}\" exists as .json and .ddb")

	if not json_path and not ddb_path:
		raise Exception(f"DB \"{db_name}\" does not exist.")

	# Uncompressed json
	if json_path:
		with open(json_path, "r") as f:
			data_str = f.read()
			return json.loads(data_str)

	# Compressed ddb
	if ddb_path:
		with open(ddb_path, "rb") as f:
			data_bytes = f.read()
			data_str = zlib.decompress(data_bytes).decode()
			return json.loads(data_str)



def protected_read_json_as_dict(db_name: str):
	"""
		Ensure that reading only starts when there is no writing,
		and that while reading, no writing will happen.
		Otherwise, wait.
	"""

	json_path, ddb_path = db_paths(db_name)
	if not json_path and not ddb_path:
		return None
	# Wait in any write lock case, "need" or "has".
	lock = ReadLock(db_name)
	res = unprotected_read_json_as_dict(db_name)
	lock.unlock()
	return res



def unprotected_write_dict_as_json(db_name: str, db: dict):
	"""
		Write the dict db dumped as a json string
		to the file of the db_path.
	"""
	json_path, ddb_path = db_paths(db_name)

	# Dump db dict as string
	db_dump = None
	if config.pretty_json_files and not config.use_compression:
		db_dump = json.dumps(db, indent="\t", sort_keys=True)
	else:
		db_dump = json.dumps(db)

	# Compression is used
	if config.use_compression:
		if json_path:
			os.remove(json_path)
		db_dump = zlib.compress(db_dump.encode(), 1)
		with open(ddb_path, "wb") as f:
			f.write(db_dump)

	# No compression is used
	else:
		if ddb_path:
			os.remove(ddb_path)
		with open(json_path, "w") as f:
			f.write(db_dump)



def protected_write_dict_as_json(db_name: str, db: dict):
	"""
		Ensures that writing only starts if there is no reading or writing in progress.
	"""
	dirname = os.path.dirname(f"{config.storage_directory}/{db_name}.any")
	os.makedirs(dirname, exist_ok=True)

	write_lock = WriteLock(db_name)
	unprotected_write_dict_as_json(db_name, db)
	write_lock.unlock()



def protected_delete(db_name: str):
	"""
		Ensures that deleting only starts if there is no reading or writing in progress.
	"""
	json_path, ddb_path = db_paths(db_name)
	if not json_path and not ddb_path:
		return
	write_lock = WriteLock(db_name)
	if json_path:
		os.remove(json_path)
	if ddb_path:
		os.remove(ddb_path)
	write_lock.unlock()
