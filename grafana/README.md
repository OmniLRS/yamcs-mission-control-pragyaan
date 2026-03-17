# JAOPS Yamcs Datasource for Grafana

This document explains how to create and configure a `jaops-yamcs-datasource` in Grafana using the [grafana-yamcs-jaops
](https://github.com/jaops-space/grafana-yamcs-jaops/) plugin.  
The plugin connects Grafana directly to a Yamcs server so you can visualise telemetry and send commands from interactive dashboards.

The examples below match the workshop setup where:

- The Grafana datasource is named `jaops-yamcs-datasource`
- A single Yamcs host is called **Workshop Server**
- One endpoint is configured for **satellite 1** using the `workshop` instance and the `realtime` processor

---

## 1. Prerequisites

Before you start, make sure you have:

- A running **Grafana** server with administrator access
- A running **Yamcs** deployment reachable from Grafana (for example via Docker or the Yamcs quickstart) 
- The **JAOPS Grafana Yamcs plugin** installed on the Grafana server
    - See the project repository [grafana-yamcs-jaops](https://github.com/jaops-space/grafana-yamcs-jaops/) for build and installation instructions.

This README focuses on creating and configuring the datasource inside Grafana, assuming the plugin is already installed and loaded.

---

## 2. Create the JAOPS Yamcs datasource in Grafana

This section walks through the exact steps to reproduce the configuration shown in the screenshot, with:

- Datasource name: `jaops-yamcs-datasource`
- Host: **Server 1** pointing to `host.docker.internal:8090` with no TLS and no authentication
- Endpoint: **Satellite 1** using the `workshop` instance and `realtime` processor on **Server 1**

### 2.1 Open the datasource editor and select the plugin

1. From the left sidebar, go to  
   **Home → Connections → Data sources**.
2. Click **Add data source**.
3. Search for **jaops-yamcs-datasource** and select the datasource plugin.
4. You are now on the datasource settings page.


