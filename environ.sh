#!/bin/bash

# 3-fingered-claw 
function yell () 
{ 
  echo "$0: $*" >&2
}

function die () 
{ 
  yell "$*"; exit 1
}

function try () 
{ 
  "$@" || die "cannot $*" 
}


# Default to foss toolchain
if [[ "$1" == "foss" || -z $1 ]];
then
    toolchain=foss
elif [[ "$1" == "intel" ]];
then
    toolchain=intel
fi
echo "Toolchain: $toolchain"

# Clean slate
try module purge

# Other IDV components
try module load iplotLogging

# Testing/Coverage requirements
try module load coverage/7.4.4-GCCcore-13.2.0

case $toolchain in

  "foss")
    # Array processing
    try module load SciPy-bundle/2023.11-gfbf-2023b
    ;;
  "intel")
    # Array processing
    try module load SciPy-bundle/2023.12-iimkl-2023b
    ;;
   *)
    echo "Unknown toolchain $toolchain"
    ;;
esac

try module -t list 2>&1 | sort

export HOME=$PWD
echo "HOME was set to $HOME"
