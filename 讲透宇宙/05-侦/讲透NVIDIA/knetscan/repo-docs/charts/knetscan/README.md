# KNetScan Helm Chart

## Installation

Before installing the chart, you need to fetch the Elasticsearch dependency:

```bash
# Add the Elastic Helm repository
helm repo add elastic https://helm.elastic.co

# Download the Elasticsearch chart dependency
helm dependency update
```

This will download the Elasticsearch chart (elasticsearch-7.17.3.tgz) into the `charts/` directory.

To install the chart:

```bash
helm install knetscan ./charts/knetscan # add the values file as needed
```