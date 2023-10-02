# cri-o snap

## Overview
This is the snap package of CRI-O. CRI-O is an "Open Container Initiative-based implementation of Kubernetes Container Runtime Interface".

For more details about CRI-O, see the [homepage](https://cri-o.io/). For the source of CRI-O, see the [repository](https://github.com/cri-o/cri-o).

The CRI-O snap is built and distributed as a "classic confinement" snap, and integrates into systems like the stock distribution of CRI-O. That means this snap is compatible with all Kubelet compatible Kubernetes solutions, including light-weight solutions such as [Minikube](https://minikube.sigs.k8s.io/docs/) and [Microk8s](https://microk8s.io/).

## Installation
The recommended way to install this snap is from the Snapcraft store.
```
sudo snap install cri-o --classic --channel=1.28/stable
```
Use the `channel` to specify which version of CRI-O to install. See CRI-O [compatibility matrix](https://github.com/cri-o/cri-o#compatibility-matrix-cri-o--kubernetes) for details on which version of CRI-O you need. Generally you want to install the same `1.x` version as the version of Kubernetes you are using.

## Usage
Start the CRI-O service
```
sudo snap start cri-o.daemon-crio
```
Then integrate CRI-O with Kubernetes. See [Integration](#integration).

## Integration
The snapped CRI-O daemon is integrated like stock CRI-O.
* Minikube: See https://minikube.sigs.k8s.io/docs/reference/runtimes/#cri-o
* kubeadm: See https://github.com/cri-o/cri-o/blob/main/tutorials/kubeadm.md
* Kubernetes: See https://github.com/cri-o/cri-o/blob/main/tutorials/kubernetes.md#running-cri-o-on-a-kubernetes-cluster

### Microk8s
Microk8s can be configure to use cri-o as it's container runtime by modifying the `snap.microk8s.daemon-kubelet` service as documented [here](https://microk8s.io/docs/configuring-services).

For example, edit `/var/snap/microk8s/current/args/kubelet` to contain
```
--container-runtime-endpoint=unix:///var/run/crio/crio.sock
--runtime-request-timeout=10m
--cgroup-driver="systemd"
```
And restart microk8s
```
sudo microk8s stop
sudo microk8s start
```

