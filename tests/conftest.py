import pytest
import subprocess
import os
import logging
import yaml

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

NAMESPACE = "default-ns"
VALUES_FILE = "values.yaml"
K8S_VERSION = os.getenv("K8S_VERSION", "1.28.0")


@pytest.fixture(scope="session")
def helm_template(chart_path):
    def _helm_template(release_name="test-deploy", values=None):
        command = ['helm', 'template', release_name, chart_path, "--kube-version", K8S_VERSION, "--namespace", NAMESPACE]
        if values:
            command.extend(['--values', values])
        helm_template_output = subprocess.check_output(command)
        return list(yaml.full_load_all(helm_template_output.decode('utf-8')))
    return _helm_template