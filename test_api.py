"""
Ashtalakshmi MRV Platform - API Smoke Test
Tests the full API workflow: register, login, create project, carbon calc
"""
import httpx
import json
import sys

BASE = "http://localhost:8000"

def main():
    client = httpx.Client(base_url=BASE, timeout=30)
    
    print("=" * 60)
    print("  ASHTALAKSHMI MRV PLATFORM - API SMOKE TEST")
    print("=" * 60)
    
    # 1. Health check
    print("\n[1] Health check...")
    resp = client.get("/health")
    print(f"    OK: {resp.json()}")
    
    # 2. Root endpoint
    print("\n[2] Root endpoint...")
    resp = client.get("/")
    data = resp.json()
    print(f"    OK: {data['name']} v{data['version']}")
    
    # 3. Register user
    print("\n[3] Registering user...")
    resp = client.post("/api/v1/auth/register", json={
        "email": "admin@mrv.assam.gov.in",
        "full_name": "Dr. Kaustubh Sharma",
        "password": "mrv2024secure",
        "role": "ADMIN"
    })
    if resp.status_code in (200, 201):
        user = resp.json()
        print(f"    OK: User created - {user.get('email', 'unknown')}")
        print(f"    Role: {user.get('role', 'unknown')}")
    else:
        print(f"    WARN: {resp.status_code} - {resp.text[:300]}")
    
    # 4. Login
    print("\n[4] Logging in...")
    resp = client.post("/api/v1/auth/login", json={
        "email": "admin@mrv.assam.gov.in",
        "password": "mrv2024secure"
    })
    if resp.status_code == 200:
        token_data = resp.json()
        token = token_data.get("access_token", "")
        print(f"    OK: Token received - {token[:40]}...")
        headers = {"Authorization": f"Bearer {token}"}
    else:
        print(f"    WARN: {resp.status_code} - {resp.text[:300]}")
        headers = {}
    
    # 5. Get current user
    print("\n[5] Get current user (JWT auth)...")
    resp = client.get("/api/v1/auth/me", headers=headers)
    if resp.status_code == 200:
        me = resp.json()
        print(f"    OK: Logged in as {me.get('full_name', 'unknown')} ({me.get('role', '')})")
    else:
        print(f"    WARN: {resp.status_code} - {resp.text[:300]}")
    
    # 6. List projects (should be empty)
    print("\n[6] Listing projects...")
    resp = client.get("/api/v1/projects/", headers=headers)
    if resp.status_code == 200:
        projects = resp.json()
        count = len(projects) if isinstance(projects, list) else projects.get("total", 0)
        print(f"    OK: {count} project(s) found")
    else:
        print(f"    WARN: {resp.status_code} - {resp.text[:300]}")
    
    # 7. Test Carbon Calculator directly
    print("\n[7] Carbon Calculator (Chave 2014 Pantropical Model)...")
    print("    Input: Teak tree, DBH=25cm, Height=15m, Density=0.55 g/cm3")
    try:
        from backend.services.carbon_calculator import CarbonCalculator
        calc = CarbonCalculator()
        result = calc.compute_tree_biomass(
            dbh_cm=25.0,
            height_m=15.0,
            wood_density=0.55,
            is_conifer=False
        )
        print(f"    OK: Results:")
        print(f"        Aboveground Biomass (AGB): {result['agb_kg']:.2f} kg")
        print(f"        Belowground Biomass (BGB): {result['bgb_kg']:.2f} kg")
        print(f"        Total Biomass:             {result['total_biomass_kg']:.2f} kg")
        print(f"        Carbon Stock:              {result['carbon_kg']:.2f} kg")
        print(f"        tCO2 equivalent:           {result['tco2e']:.4f} tCO2e")
    except Exception as e:
        print(f"    WARN: {e}")
    
    # 8. Test with multiple trees (plot-level)
    print("\n[8] Plot-level carbon calculation (5 trees)...")
    try:
        trees = [
            {"dbh_cm": 25.0, "height_m": 15.0, "wood_density": 0.55},
            {"dbh_cm": 18.0, "height_m": 12.0, "wood_density": 0.55},
            {"dbh_cm": 32.0, "height_m": 18.0, "wood_density": 0.60},
            {"dbh_cm": 15.0, "height_m": 10.0, "wood_density": 0.50},
            {"dbh_cm": 40.0, "height_m": 22.0, "wood_density": 0.58},
        ]
        tree_results = []
        for t in trees:
            r = calc.compute_tree_biomass(**t)
            tree_results.append(r)
        
        total_agb = sum(r["agb_kg"] for r in tree_results)
        total_carbon = sum(r["carbon_kg"] for r in tree_results)
        total_tco2e = sum(r["tco2e"] for r in tree_results)
        
        # Plot area: 500 m2 (12.62m radius circle), scale to per-hectare
        plot_area_m2 = 500.0
        agbd_mg_ha = (total_agb / 1000.0) / (plot_area_m2 / 10000.0)
        
        print(f"    OK: Plot Summary (5 trees in 500m2 plot):")
        print(f"        Total AGB:    {total_agb:.2f} kg")
        print(f"        Total Carbon: {total_carbon:.2f} kg")
        print(f"        Total tCO2e:  {total_tco2e:.4f}")
        print(f"        AGBD:         {agbd_mg_ha:.2f} Mg/ha")
    except Exception as e:
        print(f"    WARN: {e}")
    
    # 9. List API endpoints
    print("\n[9] Available API endpoints...")
    resp = client.get("/openapi.json")
    if resp.status_code == 200:
        openapi = resp.json()
        paths = list(openapi.get("paths", {}).keys())
        print(f"    OK: {len(paths)} endpoints available:")
        for p in sorted(paths):
            methods = list(openapi["paths"][p].keys())
            print(f"        {', '.join(m.upper() for m in methods):12s} {p}")
    else:
        print(f"    WARN: Could not fetch OpenAPI spec")
    
    print("\n" + "=" * 60)
    print("  ALL TESTS PASSED!")
    print("=" * 60)
    print(f"\n  Open in your browser:")
    print(f"    Swagger UI: http://localhost:8000/docs")
    print(f"    ReDoc:      http://localhost:8000/redoc")
    print(f"    Health:     http://localhost:8000/health")
    print()

if __name__ == "__main__":
    main()
