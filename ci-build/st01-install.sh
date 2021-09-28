#!/bin/bash
# Bamboo script
# Stage 1 : Pip install

# Set up environment
source ci-build/st00-header.sh $* || exit 1

# Create a virtualized environment for installing iplotlib
if [ -d "${PREFIX_DIR}" ];
then
    try rm -r ${PREFIX_DIR}
fi

try mkdir ${PREFIX_DIR}

# Test install command
try python3 -m pip --disable-pip-version-check install --no-deps . --prefix=${PREFIX_DIR}

export PYTHONPATH=${PYTHONPATH}:$(get_abs_filename "./${PREFIX_DIR}")
try python3 -c "import iplotProcessing"

# Stash
tar -cvzf ${PREFIX_DIR}.tar.gz ./${PREFIX_DIR}

# Clean up
try rm -r ${PREFIX_DIR}