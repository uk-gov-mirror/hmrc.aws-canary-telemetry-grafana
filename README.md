# aws-canary-telemetry-grafana

[![Brought to you by Telemetry Team](https://img.shields.io/badge/MDTP-Telemetry-40D9C0?style=flat&labelColor=000000&logo=gov.uk)](https://confluence.tools.tax.service.gov.uk/display/TEL/Telemetry)

This project is responsible for creating the Lambda code used in AWS CloudWatch Synthetics Canaries service which checks
the health of the Grafana UI.

## Table of Contents
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Prerequisites](#prerequisites)
- [License](#license)

<!-- END doctoc -->

## Prerequisites

* [mise](https://mise.jdx.dev/) to manage tool versions and integrates with `uv`.
* [uv](https://docs.astral.sh/uv/) to manage Python virtual environments and dependencies.

## License

This code is open source software licensed under the [Apache 2.0 License]("http://www.apache.org/licenses/LICENSE-2.0.html").
