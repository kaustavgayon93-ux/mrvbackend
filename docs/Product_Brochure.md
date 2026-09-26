# Ashtalakshmi MRV Platform
## Forest Monitoring & Carbon Assessment for North East India

**"Satellite-powered forest intelligence for Assam's green future"**

---

## The Challenge

Forest monitoring and carbon assessment are critical for preserving Assam's rich biodiversity and combating climate change. Traditional manual monitoring methods are often slow, prohibitively expensive, and prone to inconsistency across large, difficult-to-access terrains. As environmental initiatives in North East India accelerate, there is a pressing need for technology-driven, evidence-based monitoring systems that can provide reliable, near real-time data at scale.

## Our Solution

The Ashtalakshmi MRV Platform is an end-to-end Measurement, Reporting, and Verification system designed to fuse satellite imagery, artificial intelligence, and field data. Built specifically for Assam's forest departments under the Ashtalakshmi initiative, this platform bridges the gap between remote sensing analytics and ground-level forestry science, empowering decision-makers with actionable, high-fidelity carbon insights.

---

## Key Features

**🛰️ Satellite Intelligence**
* **Optical & SAR Data:** Integration of Sentinel-2 (optical) and Sentinel-1 (SAR).
* **High Frequency:** 5-day revisit times for near real-time monitoring.
* **Automated Processing:** Built-in automated cloud masking and atmospheric correction.

**🧠 AI-Powered Analytics**
* **Vegetation Indices:** Generates 6 key indices (NDVI, EVI, SAVI, NDRE, NBR, NDWI).
* **Biomass Estimation:** LightGBM-powered modeling with quantifiable uncertainty bounds.
* **Alert System:** Automated forest change detection and disturbance alerts.

**📊 Government Dashboard**
* **Interactive Maps:** WebGL-accelerated mapping via MapLibre GL.
* **Visual Analysis:** Split-screen before/after comparisons.
* **Zonal Statistics:** On-demand calculations via custom polygon drawing.
* **Time-Series:** Playback functionality of monitoring epochs.

**📱 Field Verification**
* **Offline-First PWA:** Designed for remote forest areas with limited connectivity.
* **Comprehensive Data Entry:** GPS plot recording, tree measurements (DBH, height), and photo capture.
* **Auto-Sync:** Seamless data synchronization when network connectivity returns.

**🌳 Carbon Assessment**
* **IPCC-Compliant:** Utilizing Chave et al. (2014) allometric equations.
* **Uncertainty Quantification:** Automated statistical bounds for carbon estimates.
* **Audit Trails:** PDF verification reports backed by SHA-256 cryptographic hashes.

**🏢 Enterprise Ready**
* **Role-Based Access:** Segregated roles for Admin, Analyst, Field Agent, and Auditor.
* **Flexible Deployment:** Docker-containerized for cloud or on-premise government servers.
* **Robust API:** 26 REST API endpoints featuring comprehensive Swagger documentation.

---

## How It Works

1. **INGEST:** Satellite data is automatically harvested from Copernicus & USGS repositories.
2. **ANALYZE:** AI and Machine Learning models process the raw imagery into precise biomass maps and change alerts.
3. **VERIFY:** Field teams conduct ground-truthing missions using the offline-capable mobile application.
4. **REPORT:** The system generates automated, IPCC-compliant carbon assessment reports with full traceability and auditability.

---

## Technical Specifications

| Specification | Detail |
|---|---|
| **Backend** | FastAPI (Python) + PostgreSQL/PostGIS |
| **Frontend** | Next.js 15 + MapLibre GL JS + deck.gl |
| **ML Engine** | LightGBM quantile regression |
| **Satellite Sources** | Sentinel-2, Sentinel-1, Landsat 8/9, GEDI |
| **Vegetation Indices** | NDVI, EVI, SAVI, NDRE, NBR, NDWI |
| **Carbon Model** | Chave et al. (2014) pantropical |
| **Standards** | Verra VM0047, IPCC 2006/2019, ISO 14064-2 |
| **Deployment** | Docker Compose (local/cloud) |
| **API Endpoints** | 26 RESTful endpoints |
| **Auth** | JWT with role-based access control |
| **Audit** | SHA-256 cryptographic hash chain |
| **Offline Support** | PWA with IndexedDB |

---

## Proven Carbon Science

The platform relies on rigorous, peer-reviewed forestry science, including the Chave et al. (2014) pantropical model.

**Sample Calculation:**
* **Input:** Teak tree, DBH = 25 cm, Height = 15 m
* **Above-Ground Biomass (AGB):** 282.65 kg
* **Total Carbon:** 160.08 kg
* **tCO2e (Carbon Dioxide Equivalent):** 0.587

**Plot-Level Aggregation:**
* Example 5-tree plot: AGBD = 42.89 Mg/ha

---

## API Coverage

The platform provides a robust API structured into six key domains:

* **Auth (3):** `register`, `login`, `me`
* **Projects (5):** Full CRUD operations plus `strata`
* **Field Data (5):** `plots`, `trees`, `submissions`, `carbon-summary`
* **Satellite (5):** `ingest`, `scenes`, `tiles`
* **Carbon (5):** `assessments`, `verify`, `report`, `summary`
* **Audit (3):** `ledger`, `verify`, `export`

---

## Deployment Options

* **Local Development:** Run lightweight with SQLite (no Docker needed).
* **On-Premise:** Secure deployment on government servers using Docker Compose.
* **Cloud Infrastructure:** Seamless scaling on AWS, GCP, or Azure with zero code changes required.

---

## Contact & Links

* **API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **System Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
* **Source Code:** `ashtalakshmi-mrv/`
