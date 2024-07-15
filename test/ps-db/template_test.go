package test

import (
	"strings"
	"testing"

	"github.com/gruntwork-io/terratest/modules/helm"
	"github.com/percona/percona-server-mysql-operator/api/v1alpha1"
	"github.com/stretchr/testify/require"
)

func TestOperatorDeploymentRendersContainers(t *testing.T) {
	t.Parallel()

	helmChartPath := "../../charts/ps-db"
	releaseName := "release-test"

	testCases := []struct {
		name string
		repo string
		tag  string
	}{
		{
			"pmm",
			"image-pmm",
			"1.1.1-1",
		},
		{
			"backup",
			"image-backup",
			"2.2.2-2",
		},
	}

	for _, testCase := range testCases {
		testCase := testCase
		t.Run(testCase.name, func(subT *testing.T) {
			//subT.Parallel()

			options := &helm.Options{
				SetValues: map[string]string{
					strings.Join([]string{testCase.name, "enabled"}, "."):             "true",
					strings.Join([]string{testCase.name, "image", "repository"}, "."): testCase.repo,
					strings.Join([]string{testCase.name, "image", "tag"}, "."):        testCase.tag,
				},
			}

			output := helm.RenderTemplate(t, options, helmChartPath, releaseName, []string{"templates/cluster.yaml"})

			var perconaServerMySQL v1alpha1.PerconaServerMySQL
			helm.UnmarshalK8SYaml(t, output, &perconaServerMySQL)

			expectedContainerImage := strings.Join([]string{testCase.repo, testCase.tag}, ":")

			if testCase.name == "pmm" {
				require.Equal(t, perconaServerMySQL.PMMSpec().Enabled, true)
				require.Equal(t, perconaServerMySQL.PMMSpec().Image, expectedContainerImage)
			} else {
				require.Equal(t, perconaServerMySQL.Spec.Backup.Enabled, true)
				require.Equal(t, perconaServerMySQL.Spec.Backup.Image, expectedContainerImage)
			}
		})
	}
}
