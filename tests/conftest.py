import os
import yaml
import pytest
import requests
import logging
import subprocess

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

NAMESPACE = "default-ns"
K8S_VERSION = os.getenv("K8S_VERSION", "1.28.0")


@pytest.fixture(scope="class")
def helm_template():
    def _helm_template(chart_path, release_name, values):
        command = [
            "helm",
            "template",
            release_name,
            chart_path,
            "--kube-version",
            K8S_VERSION,
            "--namespace",
            NAMESPACE,
            "--values",
            values,
        ]
        helm_template_output = subprocess.check_output(command)
        return list(yaml.full_load_all(helm_template_output))

    return _helm_template


@pytest.fixture(scope="class")
def get_resources_from_bundle():
    def _get_resources_from_bundle(operator_project_name, version):
        full_url = f"https://raw.githubusercontent.com/percona/{operator_project_name}/v{version}/deploy/bundle.yaml"
        response = requests.get(full_url)
        return list(yaml.safe_load_all(response.text))

    return _get_resources_from_bundle