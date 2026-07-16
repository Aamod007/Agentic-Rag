# Directory: yt-agentic-rag/app/agents/tools/calendar_tool.py

"""
Calendar Tool - Schedule Meetings via Google Calendar API.

This tool allows the agent to create calendar events with:
- Automatic Google Meet link generation
- Multiple attendees
- Timezone support
- RAG-informed durations (e.g., "standard consultation = 30 min")

Uses Google Calendar API with service account authentication and
domain-wide delegation to create events on behalf of users.
"""

import logging
import httpx
from typing import Dict, Any, List, Optional
import datetime

from .base import BaseTool
from ...config.settings import get_settings

logger = logging.getLogger(__name__)


class CalendarTool(BaseTool):
    """
    Tool for creating Cal.com bookings.
    Uses the Cal.com v2 API to create bookings using an API key.
    """
    
    def __init__(self):
        """Initialize the Calendar tool."""
        pass
    
    @property
    def name(self) -> str:
        """Tool name matching TOOL_DEFINITIONS."""
        return "create_calendar_event"
    
    @property
    def description(self) -> str:
        """Human-readable description."""
        return "Create a calendar event/meeting using Cal.com"
    
    async def execute(
        self,
        summary: str,
        start_datetime: str,
        end_datetime: Optional[str] = None,
        description: str = "",
        attendees: Optional[List[str]] = None,
        timezone: str = "UTC",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a booking on Cal.com.
        """
        # Calculate end_datetime if not provided (default 30 mins)
        if not end_datetime:
            try:
                # Handle Z or basic offset
                clean_start = start_datetime.replace('Z', '+00:00')
                start_dt = datetime.datetime.fromisoformat(clean_start)
                end_dt = start_dt + datetime.timedelta(minutes=30)
                end_datetime = end_dt.isoformat()
            except Exception as e:
                logger.error(f"Failed to calculate end_datetime: {e}")
                return self._error_response("start_datetime must be in ISO 8601 format when end_datetime is not provided")

        # Validate required parameters
        is_valid, missing = self.validate_params(
            required=['summary', 'start_datetime', 'end_datetime'],
            provided={
                'summary': summary,
                'start_datetime': start_datetime,
                'end_datetime': end_datetime
            }
        )
        
        if not is_valid:
            return self._error_response(
                f"Missing required parameters: {', '.join(missing)}"
            )
            
        settings = get_settings()
        
        attendee_email = attendees[0] if attendees else "guest@example.com"
        attendee_name = attendee_email.split("@")[0]
        
        # Cal.com API v2 payload
        payload = {
            "eventTypeSlug": settings.cal_event_type_slug,
            "username": settings.cal_username,
            "start": start_datetime,
            "attendee": {
                "name": attendee_name,
                "email": attendee_email,
                "timeZone": timezone,
                "language": "en"
            }
        }
        
        headers = {
            "Authorization": f"Bearer {settings.cal_api_key}",
            "cal-api-version": "2024-08-13",  # latest version header
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.cal.com/v2/bookings",
                    headers=headers,
                    json=payload,
                    timeout=10.0
                )
                
                if response.status_code not in (200, 201):
                    error_data = response.text
                    logger.error(f"Cal.com API error ({response.status_code}): {error_data}")
                    return self._error_response(
                        f"Cal.com API error: {response.status_code} - {error_data}"
                    )
                
                data = response.json()
                booking_data = data.get("data", {})
                
                # Extract meeting link (varies based on Cal.com setup)
                meet_link = booking_data.get("meetingUrl") or "Link will be sent via email"
                booking_uid = booking_data.get("uid")
                
                logger.info(
                    f"Cal.com booking created successfully: "
                    f"UID={booking_uid}, Summary='{summary}', "
                    f"Meet Link={meet_link}"
                )
                
                return self._success_response({
                    "event_id": booking_uid,
                    "event_link": f"https://cal.com/booking/{booking_uid}",
                    "meet_link": meet_link,
                    "summary": summary,
                    "organizer": "Cal.com Host",
                    "start": start_datetime,
                    "end": end_datetime,
                    "attendees": [attendee_email],
                    "status": booking_data.get("status", "confirmed")
                })
                
        except Exception as e:
            logger.error(f"Failed to create Cal.com booking: {e}", exc_info=True)
            return self._error_response(
                f"Failed to create event via Cal.com: {str(e)}"
            )

# Global tool instance
calendar_tool = CalendarTool()


