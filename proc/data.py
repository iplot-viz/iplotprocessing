import hashlib


def hash_code(obj, propnames=[]):
    """Creates a hash code based on values of an object properties given in second parameter"""
    payload = tuple([getattr(obj, prop) for prop in sorted(propnames) if hasattr(obj, prop)])
    return hashlib.md5(str(payload).encode('utf-8')).hexdigest()
