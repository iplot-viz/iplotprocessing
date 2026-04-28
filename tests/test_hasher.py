# Description: Unit tests for the hasher utilities used for object caching.

import hashlib

from iplotProcessing.tools.hasher import hash_code, hash_tuple


class TestHashTuple:

    def test_returns_md5_of_string_repr(self):
        payload = (1, 2, "three")
        expected = hashlib.md5(str(payload).encode("utf-8")).hexdigest()
        assert hash_tuple(payload) == expected

    def test_is_deterministic(self):
        payload = (42, "x")
        assert hash_tuple(payload) == hash_tuple(payload)

    def test_different_payloads_give_different_hashes(self):
        assert hash_tuple((1, 2)) != hash_tuple((1, 3))

    def test_empty_tuple_yields_consistent_hash(self):
        assert hash_tuple(()) == hashlib.md5("()".encode("utf-8")).hexdigest()


class _DummyObj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class TestHashCode:

    def test_default_propnames_yields_empty_tuple_hash(self):
        obj = _DummyObj(a=1, b=2)
        assert hash_code(obj) == hash_tuple(())

    def test_uses_only_listed_props(self):
        obj = _DummyObj(a=1, b=2, c=3)
        assert hash_code(obj, propnames=["a"]) == hash_tuple((1,))

    def test_props_are_sorted_alphabetically(self):
        obj = _DummyObj(a=1, b=2)
        assert hash_code(obj, propnames=["b", "a"]) == hash_tuple((1, 2))

    def test_missing_attribute_is_silently_skipped(self):
        obj = _DummyObj(a=1)
        assert hash_code(obj, propnames=["a", "missing"]) == hash_tuple((1,))

    def test_distinct_objects_with_same_props_share_hash(self):
        a = _DummyObj(x=1, y=2)
        b = _DummyObj(x=1, y=2)
        assert hash_code(a, ["x", "y"]) == hash_code(b, ["x", "y"])
