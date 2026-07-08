from typing import Any


class ReportService:
    async def generate(self, report_type: str, params: dict) -> dict[str, Any]:
        return {
            "status": "success",
            "message": f"Report '{report_type}' generation endpoint ready",
        }

    async def list_reports(self) -> dict[str, Any]:
        return {"status": "success", "message": "Reports list endpoint ready", "reports": []}
