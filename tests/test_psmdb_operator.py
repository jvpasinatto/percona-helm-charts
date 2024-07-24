import pytest
import yaml


CHART_PATH = "../charts/psmdb-operator/"
VALUES_PATH = f"{CHART_PATH}values.yaml"

@pytest.fixture(scope="session")
def chart_path():
    return CHART_PATH

@pytest.fixture(scope="class")
def k8s_resources(helm_template):
    return helm_template(values=VALUES_PATH)

@pytest.fixture
def values_file():
    with open(VALUES_PATH, 'r') as file:
        return yaml.safe_load(file.read())

class TestDefaultValues:

    @pytest.fixture(autouse=True)
    def setup_class(self, k8s_resources):
        self.deployments = [doc for doc in k8s_resources if doc['kind'] == 'Deployment']
        self.roles = [doc for doc in k8s_resources if doc['kind'] == 'Role']
        self.role_bindings = [doc for doc in k8s_resources if doc['kind'] == 'RoleBinding']
        self.service_accounts = [doc for doc in k8s_resources if doc['kind'] == 'ServiceAccount']

    def test_correct_number_of_resources(self):
        assert len(self.deployments) == 1
        assert len(self.roles) == 1
        assert len(self.role_bindings) == 1
        assert len(self.service_accounts) == 1

    def test_deployment_container_spec(self, values_file):
        envs = self.deployments[0]['spec']['template']['spec']['containers'][0]["env"]
        image = self.deployments[0]['spec']['template']['spec']['containers'][0]["image"]
        liveness_probe = self.deployments[0]['spec']['template']['spec']['containers'][0]["livenessProbe"]
        readiness_probe = self.deployments[0]['spec']['template']['spec']['containers'][0]["readinessProbe"]

        expected_image = f"{values_file["image"]["repository"]}:{values_file["image"]["tag"]}"
        expected_probe = {'httpGet': {'path': '/healthz', 'port': 'health'}}
        expected_envs = [
            {"name": "LOG_STRUCTURED", "value": "false"},
            {"name": "LOG_LEVEL", "value": "INFO"},
            {"name": "WATCH_NAMESPACE", "value": "default-ns"},
            {"name": "POD_NAME", "valueFrom": {"fieldRef": {"fieldPath": "metadata.name"}}},
            {"name": "OPERATOR_NAME", "value": "percona-server-mongodb-operator"},
            {"name": "RESYNC_PERIOD", "value": "5s"},
            {"name": "DISABLE_TELEMETRY", "value": "false"}
        ]

        assert image == expected_image
        assert envs == expected_envs
        assert liveness_probe == expected_probe
        assert readiness_probe == expected_probe
        assert self.deployments[0]['spec']['replicas'] == 1