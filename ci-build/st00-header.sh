#!/bin/bash
# Bamboo script
# Stage 0 : load modules

get_abs_filename() 
{
  # $1 : relative filename
  if [ -d "$(dirname "$1")" ]; then
    echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
  fi
}

# Set up environment for compilation
source /usr/share/Modules/init/sh
module use /work/imas/etc/modules/all

source environ.sh $*

# ENV name is used in other scripts
export PREFIX_DIR=iplotProcessing_$toolchain
