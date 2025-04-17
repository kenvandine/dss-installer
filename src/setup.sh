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

echo "Setting up the Data Science Stack"
pkexec ./bootstrap.sh $USER
if [ $? -ne 0 ]
then
    echo "Failed to bootstrap the Data Science Stack"
    exit 1
else
    echo "The Data Science Stack bootstrap successful"
fi

./initialize.sh
if [ $? -ne 0 ]
then
    echo "Failed to initialize the Data Science Stack"
    exit 1
else
    echo "The Data Science Stack initialization successful"
fi
