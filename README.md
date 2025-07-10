# Datamart API <img src="https://snipboard.io/rlh6gz.jpg" width="10%" height="00%" align="right" valign="middle"/>
PowerBI Datamart API for consumption via ChatGPT (Actions) and general clients

<div align="center">

![version](https://img.shields.io/badge/version-1.4-red.svg)
![status](https://img.shields.io/badge/status-stable-006400.svg)
![python](https://img.shields.io/badge/Python-3.10-navy.svg)
![fastapi](https://img.shields.io/badge/FastAPI-0.100.0-pink.svg)
![deploy](https://img.shields.io/badge/deploy-Render-purple.svg)
[![docs](https://img.shields.io/badge/docs-OpenAPI-green.svg)](https://chat-gdatabot.onrender.com/docs)
![secure](https://img.shields.io/badge/security-token-important.svg)
![license](https://img.shields.io/badge/license-MIT-black.svg)
</div>

<details>
  <summary>[Open/Close] Table of Contents</summary>

<!--ts-->
- [Datamart API ](#datamart-api-)
  - [📄 Description](#-description)
    - [💡Technologies](#technologies)
  - [⚙️ General Settings](#️-general-settings)
    - [📊 Set on PowerBI](#-set-on-powerbi)
    - [🔗 Set on Github](#-set-on-github)
    - [🌐 Set on Render](#-set-on-render)
    - [💻 Set on ChatGPT](#-set-on-chatgpt)
  - [🚀 Build and Run](#-build-and-run)
    - [🔧 Image Build:](#-image-build)
    - [▶️ Run with Docker:](#️-run-with-docker)
    - [🌐 Access on Web:](#-access-on-web)
  - [⚙️ Server Settings](#️-server-settings)
    - [✅ Pre Requirements](#-pre-requirements)
    - [⚙️ Architecture](#️-architecture)
  - [🔎 Endpoints](#-endpoints)
  - [🚧 Versions](#-versions)
<!--te-->

</details>


## 📄 Description
API developed for querying data from PowerBI Datamarts, allowing access to the data directly through ChatGPT (model selector 4.0 - custom model with actions) or other applications via REST endpoints.

### 💡Technologies
![Docker](https://img.shields.io/badge/Docker-Debian_enviroment-blue.svg)
![PowerBI](https://img.shields.io/badge/PowerBI-PPU_minimum-yellow.svg)
![Python](https://img.shields.io/badge/Python-3.10-navy.svg)
![Render](https://img.shields.io/badge/Render-Starter_Instance_512_MB/0.5_CPU-purple.svg)
![ChatGPT](https://img.shields.io/badge/ChatGPT-Pro-black.svg)


>---

## ⚙️ General Settings
### 📊 Set on PowerBI
- [x] 1: Create the application registration in Azure Entra ID
- [x] 2: Delegate the permissions: User.Read, Capacity.Read.All, Dataflow.Read.All, Dataset.Read.All, Tenant.Read.All, and Workspace.Read.All to the application
- [x] 3: Add the application's "user" as a member of the Power BI Workspace

### 🔗 Set on Github
- [x] 4: Create a public or private repository with all project files (requirements, yaml, dockerfile, ...)

### 🌐 Set on Render
- [x] 5: Create service with Docker runtime in any region
- [x] 6: Build connecting to the Github repository 
- [x] 7: Deploy the instance 

### 💻 Set on ChatGPT
- [x] 4: Create a public or private repository with all project files (requirements, yaml, dockerfile, ...)

>---

## 🚀 Build and Run

### 🔧 Image Build:
```bash
docker build -t fabric-connector .
```

### ▶️ Run with Docker:
```bash
docker run --rm -p 8000:8000 --env-file secret.env fabric-connector
```

### 🌐 Access on Web:
```web
http://localhost:8000/docs
```


>---

## ⚙️ Server Settings
### ✅ Pre Requirements
- [x] Docker installed
- [x] File <code>secret.env</code> with access credencials

```bash
SQL_CLIENT_ID=
SQL_CLIENT_SECRET=
SQL_TENANT_ID=
WORKSPACE_ID=
DATASET_ID=
TOKEN=
```

### ⚙️ Architecture
<pre><code>/datamart-api
├── dockerfile
├── docker-compose.yml
├── requirements.txt
├── secret.env
├── datamart-api.py (API FastAPI)
├── openapi.yaml (for ChatGPT Actions)
</code></pre>


>---

## 🔎 Endpoints
| Method | Endpoint          | About                                   |
| ------ | ----------------- | ----------------------------------------|
| GET    | `/`               | Health check                            |
| GET    | `/peoplecounting` | Dados da tabela db\_peoplecounting      |
| GET    | `/parkingdata`    | Dados da tabela db\_parking\_summary    |
| GET    | `/hotspotaccess`  | Dados da tabela db\_hotspot\_summary    |
| GET    | `/vendas`         | Dados da tabela db\_vendas              |

>---

## 🚧 Versions
 
 <details>
  <summary>[See/Hide] Version: 1.1 </summary>

![status](https://img.shields.io/badge/status-published-black.svg)
![date](https://img.shields.io/badge/date-2025/05/29-black.svg)

Improvement of initial prompt and API architecture  
</details>

<details>
  <summary>[See/Hide] Version: 1.2 </summary>

![status](https://img.shields.io/badge/status-published-black.svg)
![date](https://img.shields.io/badge/date-2025/05/30-black.svg)

Inclusion of bulk base files and enhancement of the prompt for predictive analysis  
</details>

<details>
  <summary>[See/Hide] Version: 1.3 </summary>

![status](https://img.shields.io/badge/status-published-black.svg)
![date](https://img.shields.io/badge/date-2025/06/03-black.svg)

Replacement of original tables with summary tables for optimization  
</details>

<details>
  <summary>[See/Hide] Version: 1.4 </summary>

![status](https://img.shields.io/badge/status-published-black.svg)
![date](https://img.shields.io/badge/date-2025/06/13-black.svg)

Increase security adding an API secret – Upgrade Render instance type – Added `limit` and `last_date` parameters to the `/parkingdata` endpoint – Changed ChatGPT model selector from `4o` to `4.1`  
</details>

<details>
  <summary>[See/Hide] Version: 1.5 </summary>

![status](https://img.shields.io/badge/status-in%20development-orange.svg)
![date](https://img.shields.io/badge/preview-2025/06/20-black.svg)

Available endpoints expansion and layout change
</details>

---
