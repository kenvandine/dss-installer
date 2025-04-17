#!/bin/bash


usage ()
{
  echo "usage: $0 USER"
  exit 1
}

if [ $# -ne 1 ];
then
  usage
fi

export USER=$1
export HOME=$(getent passwd $USER | cut -d: -f6)

echo "Bootstrap k8s for use with the Data Science Stack"

output=$(k8s bootstrap 2>&1)
if [[ $? -ne 0 ]] && ! [[ "${output}" =~ "node is already part of a cluster" ]];
then
    echo $output
    echo "Bootstrap failed"
    exit 1
fi

k8s enable local-storage
if [ $? -ne 0 ]
then
    echo "Enabling k8s local-storage failed"
    exit 1
fi

mkdir -p $HOME/.kube
k8s config |sed -E 's#https://((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)#https://127.0.0.1#g' > $HOME/.kube/config
if [ $? -ne 0 ]
then
    echo "Saving k8s config for use with the Data Science Stack"
    exit 1
fi

chown -R $(id -u $USER):$(id -g $USER) $HOME/.kube
