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

echo "Initializing the Data Science Stack"
echo "This could take several minutes or even longer depending on your network"

dss initialize --kubeconfig="$(cat $HOME/.kube/config)"
if [ $? -ne 0 ]
then
    echo "Failed to initialize the Data Science Stack"
    exit 1
else
    echo "The Data Science Stack is ready for use"
fi
