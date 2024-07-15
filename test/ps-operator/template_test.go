package test

import (
	"testing"

	"github.com/gruntwork-io/terratest/modules/helm"
	"github.com/stretchr/testify/assert"
	appsv1 "k8s.io/api/apps/v1"
)

func TestOperatorDeploymentRendersCorrectName(t *testing.T) {
	// Path to the helm chart we will test
	helmChartPath := "../../charts/ps-operator"

	// Setup the args
	options := &helm.Options{
		SetValues: map[string]string{"nameOverride": "dummy-name"},
	}

	output := helm.RenderTemplate(t, options, helmChartPath, "template-test", []string{}) //We can specify one specific template or leavy empty for all

	// Now we use kubernetes/client-go library to render the template output into the Deployment struct.
	var deployment appsv1.Deployment
	helm.UnmarshalK8SYaml(t, output, &deployment)

	// Finally, we verify the deployment name is set to the expected value
	expectedDeploymentName := "template-test-dummy-name"
	assert.Equal(t, deployment.Name, expectedDeploymentName)
}
