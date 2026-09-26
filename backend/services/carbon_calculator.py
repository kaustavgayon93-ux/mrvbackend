import logging
import math
from typing import List, Dict, Union

logger = logging.getLogger(__name__)

class CarbonCalculator:
    """
    Carbon and Biomass Calculator following IPCC guidelines and scientific literature.
    """

    @staticmethod
    def compute_tree_biomass(dbh_cm: float, height_m: float, wood_density: float, is_conifer: bool = False) -> Dict[str, float]:
        """
        Compute Above Ground Biomass (AGB), Below Ground Biomass (BGB), Carbon, and tCO2e for a single tree.
        Uses Chave et al. (2014) pantropical model for AGB.
        
        Args:
            dbh_cm: Diameter at breast height in cm.
            height_m: Tree height in meters.
            wood_density: Wood specific gravity (g/cm³).
            is_conifer: True if coniferous tree, False for broadleaf/tropical.
            
        Returns:
            Dictionary containing computed metrics in kg and tCO2e.
        """
        # AGB = 0.0673 * (ρ * D² * H)^0.976
        agb_kg = 0.0673 * math.pow((wood_density * (dbh_cm ** 2) * height_m), 0.976)
        
        # BGB using root-to-shoot ratio
        root_to_shoot = 0.26 if is_conifer else 0.205
        bgb_kg = agb_kg * root_to_shoot
        
        total_biomass_kg = agb_kg + bgb_kg
        
        # Carbon fraction
        carbon_fraction = 0.50 if is_conifer else 0.47
        carbon_kg = total_biomass_kg * carbon_fraction
        
        # tCO2e = (carbon_kg / 1000) * (44/12)
        tco2e = (carbon_kg / 1000.0) * (44.0 / 12.0)
        
        return {
            "agb_kg": agb_kg,
            "bgb_kg": bgb_kg,
            "total_biomass_kg": total_biomass_kg,
            "carbon_kg": carbon_kg,
            "tco2e": tco2e
        }

    @staticmethod
    def compute_plot_carbon(trees: List[Dict[str, float]], plot_area_m2: float) -> Dict[str, float]:
        """
        Compute total carbon and per-hectare metrics for a plot.
        
        Args:
            trees: List of tree dictionaries from compute_tree_biomass.
            plot_area_m2: Area of the plot in square meters.
            
        Returns:
            Dictionary with plot-level metrics.
        """
        total_agb_kg = sum(t.get("agb_kg", 0) for t in trees)
        total_carbon_kg = sum(t.get("carbon_kg", 0) for t in trees)
        total_tco2e = sum(t.get("tco2e", 0) for t in trees)
        
        plot_area_ha = plot_area_m2 / 10000.0
        
        # Per hectare values
        agbd_mg_ha = (total_agb_kg / 1000.0) / plot_area_ha if plot_area_ha > 0 else 0
        carbon_density_tc_ha = (total_carbon_kg / 1000.0) / plot_area_ha if plot_area_ha > 0 else 0
        
        return {
            "total_agb_kg": total_agb_kg,
            "total_carbon_kg": total_carbon_kg,
            "total_tco2e": total_tco2e,
            "agbd_mg_ha": agbd_mg_ha,
            "carbon_density_tc_ha": carbon_density_tc_ha
        }

    @staticmethod
    def compute_project_carbon(plot_summaries: List[Dict[str, float]], strata_areas: Dict[str, float]) -> Dict[str, float]:
        """
        Compute project-level carbon via stratified mean estimation with uncertainty and buffer pool deduction.
        
        Args:
            plot_summaries: List of plot summaries (should include strata ID or similar, simplified here).
            strata_areas: Dictionary mapping strata ID to area in hectares.
            
        Returns:
            Dictionary with project-level carbon metrics.
        """
        # Simplified for overall aggregate since stratas are not explicitly mapped in this signature
        # Assuming we just average the densities and multiply by total area for a simple baseline.
        if not plot_summaries:
            return {}
            
        avg_density = sum(p.get("carbon_density_tc_ha", 0) for p in plot_summaries) / len(plot_summaries)
        total_area = sum(strata_areas.values())
        
        total_carbon_tc = avg_density * total_area
        total_tco2e = total_carbon_tc * (44.0 / 12.0)
        
        # Uncertainty placeholders
        u_sampling = 0.05
        u_measurement = 0.02
        u_allometric = 0.10
        u_total = math.sqrt(u_sampling**2 + u_measurement**2 + u_allometric**2)
        
        # Buffer pool 15%
        buffer_deduction = total_tco2e * 0.15
        net_credit_issuance = total_tco2e - buffer_deduction
        
        return {
            "total_tco2e": total_tco2e,
            "uncertainty_percent": u_total * 100,
            "buffer_deduction": buffer_deduction,
            "net_credit_issuance": net_credit_issuance
        }

    @staticmethod
    def compute_uncertainty(plot_values: List[float], confidence: float = 0.95) -> Dict[str, float]:
        """
        Compute statistical uncertainty for a set of plot values.
        
        Args:
            plot_values: List of numerical values (e.g., carbon densities).
            confidence: Confidence level (default 0.95).
            
        Returns:
            Dictionary with statistical metrics.
        """
        n = len(plot_values)
        if n < 2:
            return {"mean": sum(plot_values) if n else 0, "relative_uncertainty_percent": 0.0}
            
        mean_val = sum(plot_values) / n
        variance = sum((x - mean_val) ** 2 for x in plot_values) / (n - 1)
        std_dev = math.sqrt(variance)
        std_err = std_dev / math.sqrt(n)
        
        # Approx t-value for 95% CI is ~1.96 for large N (use 2.0 or proper t-dist table for real use)
        t_val = 1.96
        ci_half_width = t_val * std_err
        
        rel_uncertainty = (ci_half_width / mean_val) * 100 if mean_val > 0 else 0
        
        return {
            "mean": mean_val,
            "std_error": std_err,
            "ci_half_width": ci_half_width,
            "relative_uncertainty_percent": rel_uncertainty
        }
