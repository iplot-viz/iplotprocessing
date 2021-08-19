import hashlib

def hash_tuple(payload: tuple):
    """Creates a hash code based on given payload"""
    return hashlib.md5(str(payload).encode('utf-8')).hexdigest()

def hash_code(obj, propnames=[]):
    """Creates a hash code based on values of an object properties given in second parameter"""
    payload = tuple([getattr(obj, prop) for prop in sorted(propnames) if hasattr(obj, prop)])
    return hash_tuple(payload)
