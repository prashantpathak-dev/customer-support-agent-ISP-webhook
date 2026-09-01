import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from services.config_service import ConfigService
from services.outage_service import OutageService
from services.ticket_service import TicketService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("webhook.main")

app = FastAPI(title="Dialogflow CX ISP Webhook", version="1.1.0")

# Request Validation Models
class FulfillmentInfo(BaseModel):
    tag: str

class SessionInfo(BaseModel):
    session: str
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)

class DialogflowCXRequest(BaseModel):
    fulfillmentInfo: FulfillmentInfo
    sessionInfo: SessionInfo

@app.get("/health")
def health_check():
    return {"status": "HEALTHY"}

@app.post("/webhook")
async def handle_webhook(request: Request):
    """
    Data-Only Dialogflow CX Webhook Handler.
    Processes request tags, executes isolated domain services, and updates 
    session parameters directly without dictating user text in application logic.
    """
    try:
        raw_body = await request.json()
        payload = DialogflowCXRequest(**raw_body)
        
        tag = payload.fulfillmentInfo.tag
        session_path = payload.sessionInfo.session
        session_params = payload.sessionInfo.parameters or {}
        
        updated_parameters: Dict[str, Any] = {"webhook_status": "SUCCESS"}

        # Route 1: Startup Config & Playbook Throttling
        if tag == "get_config":
            config_data = ConfigService.get_playbook_config(session_path)
            updated_parameters.update(config_data)

        # Route 2: Outage Check
        elif tag == "check_outage":
            zip_code = str(session_params.get("zip_code", "")).strip()
            if not zip_code:
                updated_parameters.update({
                    "webhook_status": "MISSING_INPUT",
                    "outage_exists": False
                })
            else:
                outage_data = OutageService.check_outage(zip_code)
                updated_parameters.update(outage_data)

        # Route 3: Ticket Status Query
        elif tag == "check_ticket":
            ticket_id = str(session_params.get("ticket_id", "")).strip()
            if not ticket_id:
                updated_parameters.update({
                    "webhook_status": "MISSING_INPUT",
                    "ticket_valid": False
                })
            else:
                ticket_data = TicketService.get_ticket_status(ticket_id)
                updated_parameters.update(ticket_data)

        else:
            logger.warning(f"Unrecognized fulfillment tag received: '{tag}'")
            updated_parameters["webhook_status"] = "UNKNOWN_TAG"

        # Return session parameter state update to Dialogflow CX
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "sessionInfo": {
                    "parameters": updated_parameters
                }
            }
        )

    except Exception as exc:
        logger.error(f"Webhook execution failure: {str(exc)}", exc_info=True)
        # HTTP 500 triggers Dialogflow CX `sys.webhook-error` event path
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "sessionInfo": {
                    "parameters": {
                        "webhook_status": "FAILED",
                        "error_message": "Backend service processing error"
                    }
                }
            }
        )