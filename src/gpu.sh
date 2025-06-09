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

curl -fsSL -o /tmp/get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 \
    && chmod 700 /tmp/get_helm.sh \
    && /tmp/get_helm.sh

helm repo add nvidia https://helm.ngc.nvidia.com/nvidia \
&& helm repo update

KUBECONFIG=$HOME/.kube/config helm install --wait --generate-name -n gpu-operator --create-namespace nvidia/gpu-operator

while ! kubectl logs -n gpu-operator -l app=nvidia-operator-validator | grep "all validations are successful"; do
  echo "Waiting for GPU operator validations to pass..."
  sleep 5
done
