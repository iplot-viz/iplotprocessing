# Copyright (c) 2020-2025 ITER Organization,
#               CS 90046
#               13067 St Paul Lez Durance Cedex
#               France
# Author IO
#
# This file is part of iplotprocessing module.
# iplotprocessing python module is free software: you can redistribute it and/or modify it under
# the terms of the MIT license.
#
# This file is part of ITER CODAC software.
# For the terms and conditions of redistribution or use of this software
# refer to the file LICENSE located in the top level directory
# of the distribution package
#


# Description: Construct a hash from an object's attributes
# Author: Abadie Lana
# Changelog:
#   Sept 2021: Refactored hash_code to use hash_tuple. Expose hash_tuple [Jaswant Sai Panchumarti]

import hashlib


def hash_tuple(payload: tuple):
    """Creates a hash code based on given payload"""
    return hashlib.md5(str(payload).encode('utf-8')).hexdigest()


def hash_code(obj, propnames=None):
    """Creates a hash code based on values of an object properties given in second parameter"""
    if propnames is None:
        propnames = []
    payload = tuple([getattr(obj, prop) for prop in sorted(propnames) if hasattr(obj, prop)])
    return hash_tuple(payload)
