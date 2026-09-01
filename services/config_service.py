import logging
import random
from typing import Dict, Any

logger = logging.getLogger("webhook.config")

class ConfigService:
    @staticmethod
    def get_playbook_config(session_id: str) -> Dict[str, Any]:
        """
        Fetches dynamic operational parameters to manage Playbook traffic 
        and feature flags at the start of a session.
        """
        logger.info(f"Retrieving session startup configuration for session: {session_id}")

        # Assign user a random number from 1 to 10
        cohort = random.randint(1, 10)

        # Pull config from backend service (simulated here)
        outage_service_enabled = True  # Simulated backend response
        troubleshooting_playbook_enabled = True  # Simulated backend response
        
        return {
            "config_fetched": True,
            "user_cohort": cohort,
            "outage_service_active": outage_service_enabled,
            "troubleshooting_playbook_enabled": troubleshooting_playbook_enabled
        }
