import os
import sys
import uuid
import httpx
import json
import time

# Set encoding as requested
os.environ["PYTHONIOENCODING"] = "utf-8"

BASE_URL = "http://localhost:8000"
TIMEOUT = 30.0

def print_step(msg: str):
    print(f"\n[INFO] {msg}")

def print_ok(msg: str):
    print(f"  [OK] {msg}")

def print_warn(msg: str):
    print(f"  [WARN] {msg}")

def print_err(msg: str):
    print(f"  [ERROR] {msg}")

def main():
    print("=" * 60)
    print("  ASHTALAKSHMI MRV PLATFORM - SEED DEMO DATA")
    print("=" * 60)

    client = httpx.Client(base_url=BASE_URL, timeout=TIMEOUT)
    headers = {}

    # Step 1: Register & Login
    print_step("Step 1: Register & Login")
    user_email = "forest.officer@assam.gov.in"
    user_pwd = "assam2024"
    
    register_payload = {
        "email": user_email,
        "full_name": "Shri Rajesh Borah",
        "password": user_pwd,
        "role": "ADMIN",
        "org_id": None
    }
    
    resp = client.post("/api/v1/auth/register", json=register_payload)
    if resp.status_code in (200, 201):
        print_ok(f"Registered user: {user_email}")
    else:
        print_warn(f"User registration issue (might already exist): {resp.status_code} - {resp.text}")

    # Login
    login_payload = {
        "email": user_email,
        "password": user_pwd
    }
    resp = client.post("/api/v1/auth/login", json=login_payload)
    if resp.status_code == 200:
        token = resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print_ok("Logged in successfully, got JWT token.")
    else:
        print_err(f"Login failed: {resp.status_code} - {resp.text}")
        return

    # Get user to fetch ID (for surveyor_id)
    resp = client.get("/api/v1/auth/me", headers=headers)
    if resp.status_code == 200:
        me = resp.json()
        surveyor_id = me.get("id")
        print_ok(f"Fetched user ID for surveyor: {surveyor_id}")
    else:
        print_err("Failed to get current user ID")
        return

    # Step 2: Create Organization
    print_step("Step 2: Create Organization")
    org_payload = {
        "name": "Assam State Agency for Comprehensive Carbon Management (ASSAC)",
        "country_code": "IN",
        "contact_email": "contact@assac.assam.gov.in"
    }
    resp = client.post("/api/v1/projects/organizations", json=org_payload, headers=headers)
    if resp.status_code in (200, 201):
        org_id = resp.json().get("id")
        print_ok(f"Created organization: ASSAC (ID: {org_id})")
    else:
        print_warn(f"Failed to create organization via API ({resp.status_code}), using generated UUID")
        org_id = str(uuid.uuid4())

    # Step 3: Create MRV Project
    print_step("Step 3: Create MRV Project")
    project_payload = {
        "org_id": org_id,
        "name": "Kaziranga Buffer Zone Agroforestry Restoration",
        "description": "Large-scale agroforestry carbon sequestration project in the buffer zone surrounding Kaziranga National Park, Golaghat and Nagaon districts, Assam. The project restores degraded agricultural land through multi-species agroforestry plantations featuring indigenous species including Teak (Tectona grandis), Sal (Shorea robusta), Hollong (Dipterocarpus macrocarpus), and Nahar (Mesua ferrea).",
        "methodology": "VERRA_VM0047",
        "start_date": "2023-06-01",
        "crediting_period_years": 30,
        "boundary": {
            "type": "MultiPolygon",
            "coordinates": [[[[93.1, 26.55], [93.5, 26.55], [93.5, 26.75], [93.1, 26.75], [93.1, 26.55]]]]
        }
    }
    
    resp = client.post("/api/v1/projects/", json=project_payload, headers=headers)
    if resp.status_code in (200, 201):
        project = resp.json()
        project_id = project["id"]
        print_ok(f"Created project: {project['name']} (ID: {project_id})")
    else:
        print_err(f"Failed to create project: {resp.status_code} - {resp.text}")
        print_warn("Assuming project creation failure is due to SQLite lack of PostGIS; aborting.")
        return

    # Step 4: Create Sample Plots
    print_step("Step 4: Create Sample Plots")
    plots_data = [
        {"plot_code": "KBZ-P01", "latitude": 26.60, "longitude": 93.20, "elevation_m": 78},
        {"plot_code": "KBZ-P02", "latitude": 26.63, "longitude": 93.25, "elevation_m": 82},
        {"plot_code": "KBZ-P03", "latitude": 26.58, "longitude": 93.30, "elevation_m": 75},
        {"plot_code": "KBZ-P04", "latitude": 26.65, "longitude": 93.35, "elevation_m": 85},
        {"plot_code": "KBZ-P05", "latitude": 26.62, "longitude": 93.40, "elevation_m": 80},
        {"plot_code": "KBZ-P06", "latitude": 26.67, "longitude": 93.15, "elevation_m": 90},
    ]

    created_plots = []
    for pd in plots_data:
        pd["project_id"] = project_id
        pd["radius_meters"] = 12.62
        resp = client.post("/api/v1/field/plots", json=pd, headers=headers)
        if resp.status_code in (200, 201):
            plot = resp.json()
            created_plots.append(plot)
            print_ok(f"Created plot {plot['plot_code']} (ID: {plot['id']})")
        else:
            print_err(f"Failed to create plot {pd['plot_code']}: {resp.status_code} - {resp.text}")

    if not created_plots:
        print_err("No plots created. Aborting.")
        return

    # Step 5: Add Trees to Each Plot
    print_step("Step 5: Add Trees to Plots")
    
    # Structure of trees per plot
    trees_map = {
        "KBZ-P01": [
            {"species": "Tectona grandis (Teak)", "dbh": 28.5, "h": 16.2, "d": 0.55, "health": "HEALTHY"},
            {"species": "Tectona grandis (Teak)", "dbh": 22.0, "h": 14.5, "d": 0.55, "health": "HEALTHY"},
            {"species": "Tectona grandis (Teak)", "dbh": 35.0, "h": 19.0, "d": 0.55, "health": "HEALTHY"},
            {"species": "Shorea robusta (Sal)", "dbh": 18.5, "h": 12.0, "d": 0.72, "health": "HEALTHY"},
            {"species": "Gmelina arborea (Gamari)", "dbh": 24.0, "h": 15.0, "d": 0.41, "health": "DAMAGED"}
        ],
        "KBZ-P02": [
            {"species": "Shorea robusta (Sal)", "dbh": 30.0, "h": 18.0, "d": 0.72, "health": "HEALTHY"},
            {"species": "Dipterocarpus macrocarpus (Hollong)", "dbh": 42.0, "h": 25.0, "d": 0.57, "health": "HEALTHY"},
            {"species": "Mesua ferrea (Nahar)", "dbh": 20.0, "h": 13.0, "d": 0.78, "health": "HEALTHY"},
            {"species": "Artocarpus chaplasha (Chaplash)", "dbh": 26.0, "h": 16.0, "d": 0.49, "health": "HEALTHY"},
            {"species": "Lagerstroemia speciosa (Jarul)", "dbh": 19.0, "h": 11.5, "d": 0.52, "health": "DAMAGED"}
        ],
        "KBZ-P03": [
            {"species": "Shorea robusta (Sal)", "dbh": 38.0, "h": 20.0, "d": 0.72, "health": "HEALTHY"},
            {"species": "Shorea robusta (Sal)", "dbh": 25.0, "h": 15.0, "d": 0.72, "health": "HEALTHY"},
            {"species": "Terminalia myriocarpa (Hollock)", "dbh": 32.0, "h": 18.5, "d": 0.53, "health": "HEALTHY"},
            {"species": "Albizia procera (White Siris)", "dbh": 21.0, "h": 13.0, "d": 0.50, "health": "HEALTHY"}
        ],
        "KBZ-P04": [
            {"species": "Tectona grandis (Teak)", "dbh": 12.0, "h": 8.5, "d": 0.55, "health": "HEALTHY"},
            {"species": "Tectona grandis (Teak)", "dbh": 14.0, "h": 9.5, "d": 0.55, "health": "HEALTHY"},
            {"species": "Gmelina arborea (Gamari)", "dbh": 16.0, "h": 10.0, "d": 0.41, "health": "HEALTHY"},
            {"species": "Gmelina arborea (Gamari)", "dbh": 13.0, "h": 9.0, "d": 0.41, "health": "HEALTHY"},
            {"species": "Bombax ceiba (Simul)", "dbh": 18.0, "h": 11.0, "d": 0.34, "health": "HEALTHY"},
            {"species": "Albizia lebbeck (Siris)", "dbh": 15.0, "h": 10.5, "d": 0.55, "health": "DAMAGED"}
        ],
        "KBZ-P05": [
            {"species": "Dipterocarpus macrocarpus (Hollong)", "dbh": 55.0, "h": 30.0, "d": 0.57, "health": "HEALTHY"},
            {"species": "Shorea robusta (Sal)", "dbh": 45.0, "h": 24.0, "d": 0.72, "health": "HEALTHY"},
            {"species": "Mesua ferrea (Nahar)", "dbh": 28.0, "h": 17.0, "d": 0.78, "health": "HEALTHY"},
            {"species": "Terminalia myriocarpa (Hollock)", "dbh": 38.0, "h": 21.0, "d": 0.53, "health": "HEALTHY"}
        ],
        "KBZ-P06": [
            {"species": "Lagerstroemia speciosa (Jarul)", "dbh": 22.0, "h": 13.0, "d": 0.52, "health": "HEALTHY"},
            {"species": "Albizia procera (White Siris)", "dbh": 30.0, "h": 17.0, "d": 0.50, "health": "HEALTHY"},
            {"species": "Artocarpus chaplasha (Chaplash)", "dbh": 35.0, "h": 19.0, "d": 0.49, "health": "HEALTHY"},
            {"species": "Syzygium cumini (Jamun)", "dbh": 20.0, "h": 12.0, "d": 0.64, "health": "HEALTHY"},
            {"species": "Ficus benghalensis (Banyan)", "dbh": 48.0, "h": 18.0, "d": 0.41, "health": "HEALTHY"}
        ]
    }

    total_trees_added = 0
    for p in created_plots:
        code = p["plot_code"]
        plot_id = p["id"]
        if code in trees_map:
            trees_for_plot = trees_map[code]
            for idx, td in enumerate(trees_for_plot, start=1):
                tree_payload = {
                    "plot_id": plot_id,
                    "tag_number": f"{code}-T{idx:02d}",
                    "species_common": td["species"],
                    "species_scientific": td["species"], # Using same for both to simplify
                    "dbh_cm": td["dbh"],
                    "height_m": td["h"],
                    "wood_density_g_cm3": td["d"],
                    "is_conifer": False,
                    "measured_at": "2024-03-15T09:00:00",
                    "surveyor_id": surveyor_id,
                    "health_status": td["health"]
                }
                resp = client.post(f"/api/v1/field/plots/{plot_id}/trees", json=tree_payload, headers=headers)
                if resp.status_code in (200, 201):
                    total_trees_added += 1
                else:
                    print_err(f"Failed to add tree to {code}: {resp.status_code} - {resp.text}")
            print_ok(f"Added {len(trees_for_plot)} trees to {code}")

    # Step 6 & 7: Carbon Calculations and Final Summary
    print_step("Step 6 & 7: Carbon Calculations and Final Summary")
    
    project_agb = 0.0
    project_carbon = 0.0
    project_tco2e = 0.0
    
    print("\n" + "-" * 80)
    print("  PROJECT CARBON ASSESSMENT REPORT")
    print("-" * 80)
    print(f"  Project Name: {project_payload['name']}")
    print(f"  Total Plots:  {len(created_plots)}")
    print(f"  Total Trees:  {total_trees_added}")
    print("-" * 80)
    print(f"  | {'Plot Code':<10} | {'Trees':<6} | {'Mean DBH':<10} | {'AGB (kg)':<10} | {'Carbon (kg)':<12} | {'tCO2e':<10} |")
    print("  " + "-" * 78)

    for p in created_plots:
        code = p["plot_code"]
        plot_id = p["id"]
        
        resp = client.get(f"/api/v1/field/plots/{plot_id}/carbon-summary", headers=headers)
        if resp.status_code == 200:
            cs = resp.json()
            trees_count = cs.get("total_trees", 0)
            mean_dbh = cs.get("mean_dbh_cm", 0.0)
            agb = cs.get("total_agb_kg", 0.0)
            carbon = cs.get("total_carbon_kg", 0.0)
            tco2e = cs.get("total_tco2e", 0.0)
            
            project_agb += agb
            project_carbon += carbon
            project_tco2e += tco2e
            
            print(f"  | {code:<10} | {trees_count:<6} | {mean_dbh:<10.2f} | {agb:<10.2f} | {carbon:<12.2f} | {tco2e:<10.4f} |")
        else:
            print_err(f"Failed to get summary for {code}")

    print("  " + "-" * 78)
    
    # 6 plots * 500m2 (approx 12.62m radius) = 3000m2 = 0.3 ha
    total_sampled_area_ha = len(created_plots) * 0.05
    mean_agbd = (project_agb / 1000.0) / total_sampled_area_ha if total_sampled_area_ha > 0 else 0
    
    project_area_ha = project_payload.get("total_area_ha", 150.0) # Fallback to 150 ha if not in response
    if 'project' in locals() and 'total_area_ha' in project and project['total_area_ha']:
        project_area_ha = float(project['total_area_ha'])

    print(f"  [PROJECT TOTALS VIA API]")
    print(f"  Total AGB:       {project_agb:.2f} kg")
    print(f"  Total Carbon:    {project_carbon:.2f} kg")
    print(f"  Total tCO2e:     {project_tco2e:.4f} tCO2e")
    print(f"  Mean AGBD:       {mean_agbd:.2f} Mg/ha")
    
    estimated_project_tco2e = mean_agbd * 0.47 * (44/12) * project_area_ha
    print(f"  Extrapolated Project tCO2e (Area {project_area_ha:.1f} ha): {estimated_project_tco2e:.2f} tCO2e")
    print("=" * 80)

    print_step("Demonstrating Direct CarbonCalculator Usage")
    try:
        sys.path.append(os.getcwd())
        from backend.services.carbon_calculator import CarbonCalculator
        print_ok("Successfully imported CarbonCalculator.")
        
        calc = CarbonCalculator()
        # Compute for one reference tree directly
        result = calc.compute_tree_biomass(dbh_cm=55.0, height_m=30.0, wood_density=0.57, is_conifer=False)
        print("  [Direct Calculation Result for Hollong: DBH=55cm, H=30m, D=0.57]")
        print(f"  AGB:     {result['agb_kg']:.2f} kg")
        print(f"  BGB:     {result['bgb_kg']:.2f} kg")
        print(f"  Carbon:  {result['carbon_kg']:.2f} kg")
        print(f"  tCO2e:   {result['tco2e']:.4f}")
    except Exception as e:
        print_warn(f"Could not use CarbonCalculator directly: {e}")

    print("=" * 80)
    print("  Data seeding and assessment complete.")
    print("=" * 80)

if __name__ == "__main__":
    main()
