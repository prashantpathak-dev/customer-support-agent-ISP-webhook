import logging
from typing import Dict, Any

logger = logging.getLogger("webhook.outage")

class OutageService:
    @staticmethod
    def check_outage(zip_code: str) -> Dict[str, Any]:
        """
        Queries outage backend database for given postal/ZIP code.
        """
        logger.info(f"Querying outage database for ZIP code: {zip_code}")
        
        # Simulated backend timeout / 5xx failure scenario for testing
        if zip_code == "999999":
            logger.error("Database connection timeout simulated for ZIP 999999")
            raise RuntimeError("Backend Outage Database Service Unavailable")
            
        # Active outage scenario
        if zip_code == "560001":
            return {
                "outage_exists": True,
                "outage_area": "560001",
                "outage_eta": "18:30"
            }
        
        # Normal operation scenario (No outage)
        return {
            "outage_exists": False,
            "outage_area": zip_code,
            "outage_eta": None
        }