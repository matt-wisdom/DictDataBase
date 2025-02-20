import dictdatabase as DDB
from path_dict import pd
import pytest
import json

from tests.utils import make_complex_nested_random_dict


def test_create(env, use_compression, use_orjson, sort_keys, indent):
	DDB.at("test_create").create(force_overwrite=True)
	db = DDB.at("test_create").read()
	assert db == {}

	with DDB.at("test_create").session(as_type=pd) as (session, d):
		d["a", "b", "c"] = "d"
		session.write()
	assert DDB.at("test_create").read() == {"a": {"b": {"c": "d"}}}


def test_create_edge_cases(env, use_compression, use_orjson, sort_keys, indent):
	cases = [-2, 0.0, "", "x", [], {}, True]

	for i, c in enumerate(cases):
		DDB.at(f"tcec{i}").create(c, force_overwrite=True)
		assert DDB.at(f"tcec{i}").read() == c

	with pytest.raises(TypeError):
		DDB.at("tcec99").create(object(), force_overwrite=True)


def test_nested_file_creation(env, use_compression, use_orjson, sort_keys, indent):
	n = DDB.at("nested/file/nonexistent").read()
	assert n is None
	db = make_complex_nested_random_dict(12, 6)
	DDB.at("nested/file/creation/test").create(db, force_overwrite=True)
	assert DDB.at("nested/file/creation/test").read() == db


def test_create_same_file_twice(env, use_compression, use_orjson, sort_keys, indent):
	name = "test_create_same_file_twice"
	# Check that creating the same file twice must raise an error
	with pytest.raises(FileExistsError):
		DDB.at(name).create(force_overwrite=True)
		DDB.at(name).create()
	# Check that creating the same file twice with force_overwrite=True works
	DDB.at(f"{name}2").create(force_overwrite=True)
	DDB.at(f"{name}2").create(force_overwrite=True)
