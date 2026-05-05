import logging
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from docs_tool import append_to_doc
from gmail_tool import send_email

# Re-create credentials.json from environment variable for Google libraries
if os.environ.get("GOOGLE_CREDENTIALS_JSON"):
    with open("credentials.json", "w") as f:
        f.write(os.environ.get("GOOGLE_CREDENTIALS_JSON"))

logging.basicConfig(level=logging.INFO)
# ---------------- LOGGING SETUP ---------------- #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# ---------------- APP INIT ---------------- #
app = FastAPI(title="Google MCP Server")


# ---------------- REQUEST SCHEMAS ---------------- #
class AppendDocInput(BaseModel):
    doc_id: str
    content: str


class EmailInput(BaseModel):
    to: str 
    subject: str
    body: str


# ---------------- APPROVAL LAYER ---------------- #
def approve(action: str, payload: dict) -> bool:
    """
    Approval system:
    - Local → manual approval
    - Deployment → auto-approved
    """

    # ✅ Auto-approve in deployment (Render sets RENDER=true automatically)
    if os.getenv("AUTO_APPROVE", "false").lower() == "true" or os.getenv("RENDER"):
        logger.info(f"{action} auto-approved (deployment env)")
        return True

    # 🧪 Local CLI approval
    try:
        print("\n-----------------------------")
        print(f"ACTION: {action}")
        print(f"PAYLOAD: {payload}")
        print("-----------------------------")

        decision = input("Approve? (y/n): ").strip().lower()

        if decision == "y":
            logger.info(f"{action} approved")
            return True
        else:
            logger.warning(f"{action} rejected")
            return False

    except Exception as e:
        logger.error(f"Approval error: {e}")
        return False


# ---------------- MCP TOOL LIST ---------------- #
@app.get("/tools")
def list_tools():
    return [
        {
            "name": "append_to_doc",
            "description": "Append content to Google Doc"
        },
        {
            "name": "send_email",
            "description": "Send Gmail directly"
        }
    ]


# ---------------- DOC TOOL ---------------- #
@app.post("/append_to_doc")
def run_append(data: AppendDocInput):
    try:
        logger.info("Received request for append_to_doc")

        if not approve("append_to_doc", data.dict()):
            return {
                "status": "rejected",
                "message": "User rejected the action"
            }

        result = append_to_doc(
            doc_id=data.doc_id,
            content=data.content
        )

        logger.info("append_to_doc executed successfully")

        return result

    except Exception as e:
        logger.error(f"Error in append_to_doc: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------- EMAIL TOOL ---------------- #
@app.post("/send_email")
def run_email(data: EmailInput):
    try:
        logger.info("Received request for send_email")

        if not approve("send_email", data.dict()):
            return {
                "status": "rejected",
                "message": "User rejected the action"
            }

        result = send_email(
            to=data.to,
            subject=data.subject,
            body=data.body
        )

        logger.info("send_email executed successfully")

        return result

    except Exception as e:
        logger.error(f"Error in send_email: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ---------------- HEALTH CHECK ---------------- #
@app.get("/")
def root():
    return {
        "message": "Google MCP Server is running 🚀"
    }