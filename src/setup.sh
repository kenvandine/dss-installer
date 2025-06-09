#!/bin/bash


usage ()
{
  echo "usage: $0"
  exit 1
}

if [ $# -ne 0 ];
then
  usage
fi

script_dir=$(dirname $0)

echo "Setting up the Data Science Stack"
pkexec $script_dir/bootstrap.sh $USER
if [ $? -ne 0 ]
then
    echo "Failed to bootstrap the Data Science Stack"
    exit 1
else
    echo "The Data Science Stack bootstrap successful"
fi

$script_dir/initialize.sh
if [ $? -ne 0 ]
then
    echo "Failed to initialize the Data Science Stack"
    exit 1
else
    echo "The Data Science Stack initialization successful"
fi

echo "Installing the GPU Operator"
pkexec $script_dir/gpu.sh $USER
if [ $? -ne 0 ]
then
    echo "Failed to install GPU Operator"
    exit 1
else
    echo "The Data Science Stack GPU Operator installed"
fi
