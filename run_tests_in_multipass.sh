#! /bin/bash
set -ex

scriptdir=$(dirname "$0")
vm_name=cri-o-snap-test
multipass launch \
    --name ${vm_name} \
    --mount ${scriptdir}:/home/ubuntu/cri-o-snap \
    --cpus 2 --memory 6G --disk 20G \
    jammy || true

multipass exec ${vm_name} --working-directory "/home/ubuntu/cri-o-snap" -- bash ./multipass_setup.sh
multipass exec ${vm_name} --working-directory "/home/ubuntu/cri-o-snap" -- pytest -s tests/test-crio-runtime.py
multipass stop ${vm_name}
