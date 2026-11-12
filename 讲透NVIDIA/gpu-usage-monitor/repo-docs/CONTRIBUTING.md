# Contributing to GPU Usage Monitor

Thank you for your interest in contributing to the GPU Usage Monitor! This project welcomes contributions of new panels and dashboards for GPU monitoring in Kubernetes clusters.

## What You Can Contribute

- **New Panels** - Add visualization panels for GPU metrics (utilization, memory, allocation, etc.)
- **New Dashboards** - Create dashboard layouts combining multiple panels for specific use cases

## Available Metrics

When building panels, you can use metrics from:

- **DCGM Exporter** - GPU metrics like `DCGM_FI_DEV_GPU_UTIL`, `DCGM_FI_DEV_FB_FREE`, `DCGM_FI_DEV_FB_USED`
- **kube-state-metrics** - Kubernetes pod and resource metrics

## How to Contribute

1. **Fork and Clone** - Fork the repository and clone it locally
2. **Create a Branch** - Use a descriptive name like `panel/gpu-temperature` or `dashboard/multi-node-overview`
3. **Develop Your Panel/Dashboard**
   - Create your Grafana dashboard JSON and add it to the `dashboards/` directory
   - Register your dashboard in `templates/grafana/configmap.yaml` by adding an entry:
     ```yaml
     your-dashboard-name.json: |
     {{ .Files.Get "dashboards/your-dashboard-name.json" | indent 4 }}
     ```
4. **Test Locally** - Install the Helm chart and verify your contribution works:
   ```bash
   helm install gpu-usage-monitor . --namespace gpu-usage-monitor --create-namespace
   kubectl port-forward -n gpu-usage-monitor svc/gpu-usage-monitor-grafana 3000:80
   ```
5. **Submit a PR** - Open a pull request with a clear description

## Pull Request Guidelines

- Provide a clear title describing your panel or dashboard
- Include a screenshot showing the visualization
- Describe what metrics are displayed and the use case
- Ensure the dashboard loads correctly with the default Prometheus data source

## Sign your work

The sign-off is a simple line at the end of the explanation for the patch. Your
signature certifies that you wrote the patch or otherwise have the right to pass
it on as an open-source patch. The rules are pretty simple: if you can certify
the below (from [developercertificate.org](http://developercertificate.org/)):

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
1 Letterman Drive
Suite D4700
San Francisco, CA, 94129

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.

Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

Then you just add a line to every git commit message:

    Signed-off-by: Joe Smith <joe.smith@email.com>

Use your real name (sorry, no pseudonyms or anonymous contributions.)

If you set your `user.name` and `user.email` git configs, you can sign your
commit automatically with `git commit -s`.


## Getting Help

If you have questions, open an issue on GitHub.

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
