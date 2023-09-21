import logging
import re
import subprocess
import json
from typing import Dict, List

import pytest

logger = logging.getLogger(__name__)
SNAP_NAME = "cri-o"
SERVICE_NAME = "daemon-crio"


def log_cmd(cmd: List[str], check: bool = False) -> str:
    output = subprocess.run(cmd, capture_output=True, check=check)
    logger.info(
        ("\n" + " ".join(cmd))
        + ("\n" + output.stderr.decode() if output.stderr else "")
        + ("\n" + output.stdout.decode() if output.stdout else "")
    )
    return output.stdout.decode()


def json_cmd(cmd: List[str]) -> Dict:
    output = subprocess.check_output(cmd)
    return json.loads(output.decode())


@pytest.fixture(scope="class")
def crio_service():
    subprocess.check_call(["sudo", "snap", "start", f"{SNAP_NAME}.{SERVICE_NAME}"])
    yield
    subprocess.check_call(["sudo", "snap", "stop", f"{SNAP_NAME}.{SERVICE_NAME}"])


@pytest.fixture
def nginx_deployment(crio_service):
    subprocess.check_call(["sudo", "microk8s", "kubectl", "create", "deployment", "nginx", "--image=nginx"])
    subprocess.check_call(["sudo", "microk8s", "kubectl", "rollout", "status", "deployment", "nginx"])
    yield
    subprocess.check_call(["sudo", "microk8s", "kubectl", "delete", "deployment", "nginx"])


class TestCrio:
    """
    Preconditions:
        - cri-o snap is installed
        - microk8s snap is installed
        - microk8s kubelet args configured to use crio socket
        - CNI plugins installed
        - /etc/containers policy and registries configured
    Verify:
        - cri-o service can pull and run test container
        - container ID indicates cri-o used as runtime
    Postconditions:
        - cri-o service is stopped
        - microk8s deployment is removed
    """

    def test_crio_starts(self, crio_service):
        """
        Verify: cri-o service daemon was started and is "active"
        """
        output = log_cmd(["sudo", "snap", "services"])
        # verify cri-o service is running
        m = re.search(rf"^{SNAP_NAME}\.{SERVICE_NAME}\s+\w+\s+active", output, re.MULTILINE)
        assert m is not None

    def test_crio_integration_with_microk8s(self, nginx_deployment):
        """
        Verify: Creating a new microk8s deployment starts the container successfully with cri-o runtime
        """
        log_cmd(["sudo", "microk8s", "kubectl", "describe", "nodes"])
        log_cmd(["sudo", "microk8s", "kubectl", "get", "pods"])
        log_cmd(["sudo", "microk8s", "kubectl", "logs", "deployment/nginx"])
        log_cmd(["sudo", "microk8s", "kubectl", "get", "deployment", "nginx"])
        # verify deployment is ready
        data = json_cmd(["sudo", "microk8s", "kubectl", "get", "--output=json", "deployment", "nginx"])
        assert data["status"]["readyReplicas"] >= 1
        data = json_cmd(["sudo", "microk8s", "kubectl", "get", "pods", "--selector=app=nginx", "--output=json"])
        pod_name = data["items"][0]["metadata"]["name"]
        logger.info(f"nginx pod: {pod_name}")
        # verify container id starts with 'cri-o' to indicate cri-o was used
        log_cmd(["sudo", "microk8s", "kubectl", "describe", "pod", pod_name])
        data = json_cmd(["sudo", "microk8s", "kubectl", "get", "--output=json", "pod", pod_name])
        container_id: str = data["status"]["containerStatuses"][0]["containerID"]
        logger.info(f"Container ID: {container_id}")
        assert container_id.startswith("cri-o")
