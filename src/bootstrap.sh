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

echo $USER
echo $HOME
exit

k8s bootstrap
k8s enable local-storage
mkdir -p $HOME/.kube
k8s config |sed -E 's#https://((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)#https://127.0.0.1#g' > $HOME/.kube/config

chown -R $(id -u $USER):$(id -g $USER) $HOME/.kube
