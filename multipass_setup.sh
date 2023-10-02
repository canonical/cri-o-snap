#! /bin/bash
set -e
sudo apt-get update
sudo apt-get install --yes python3-pip python3-setuptools containernetworking-plugins wget
sudo pip3 install --upgrade pip
sudo pip3 install -U pytest sh requests
sudo snap install cri-o_latest_amd64.snap --classic --dangerous
sudo snap install microk8s --classic --channel=1.28/stable
sudo microk8s status --wait-ready --timeout 60
sudo wget https://raw.githubusercontent.com/cri-o/cri-o/main/contrib/cni/11-crio-ipv4-bridge.conflist -O /etc/cni/net.d/11-crio-ipv4-bridge.conflist
sudo mkdir -p /etc/containers
sudo wget https://raw.githubusercontent.com/cri-o/cri-o/main/test/policy.json -O /etc/containers/policy.json
sudo wget https://raw.githubusercontent.com/cri-o/cri-o/main/test/registries.conf -O /etc/containers/registries.conf
sudo tee /var/snap/microk8s/current/args/kubelet << 'EOF'
--resolv-conf=/run/systemd/resolve/resolv.conf
--kubeconfig=${SNAP_DATA}/credentials/kubelet.config
--cert-dir=${SNAP_DATA}/certs
--client-ca-file=${SNAP_DATA}/certs/ca.crt
--anonymous-auth=false
--root-dir=${SNAP_COMMON}/var/lib/kubelet
--fail-swap-on=false
--feature-gates=DevicePlugins=true
--eviction-hard="memory.available<100Mi,nodefs.available<1Gi,imagefs.available<1Gi"
--container-runtime-endpoint=unix:///var/run/crio/crio.sock
--containerd=${SNAP_COMMON}/run/containerd.sock
--node-labels="microk8s.io/cluster=true,node.kubernetes.io/microk8s-controlplane=microk8s-controlplane"
--authentication-token-webhook=true
--read-only-port=0
--cluster-domain=cluster.local
--cluster-dns=10.152.183.10
--runtime-request-timeout=10m
--cgroup-driver="systemd"
EOF
sudo microk8s stop
sudo microk8s start
sudo microk8s status --wait-ready --timeout 60
