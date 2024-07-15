#!/bin/bash

set -e

export K8S_VERSIONS=("1.27.0" "1.30.0")
export PROJECT_PREFIX="ps"

clean () {
    rm -rf schemas
}

# Converts CRD OpenApi to json schema supported by kubeconform
mkdir -p schemas
trap clean EXIT
cd schemas
curl -O "https://raw.githubusercontent.com/yannh/kubeconform/347cd5e4c96dc9e69bc9a5e72ad800c91b6fc8db/scripts/openapi2jsonschema.py"
python3 openapi2jsonschema.py $(realpath ../charts/${PROJECT_PREFIX}-operator/crds/crd.yaml)
cd ..

# Validates operator and db charts for the specifies K8s versions using the default values.yaml file

for k8s_version in ${K8S_VERSIONS[@]}; do
    echo "Validating resources against K8s ${k8s_version} version"
    helm template operator-test charts/${PROJECT_PREFIX}-operator | kubeconform --exit-on-error --kubernetes-version ${k8s_version} --schema-location default 
    helm template db-test charts/${PROJECT_PREFIX}-db | kubeconform --exit-on-error --kubernetes-version ${k8s_version} --schema-location default --schema-location 'schemas/{{.ResourceKind}}_{{.ResourceAPIVersion}}.json'
done