from typing import Any
import aiohttp
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

async def make_nws_request(url: str):
    try:
        # Example: Use aiohttp or another library to make the request
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Error: Received status {response.status} from {url}")
                    return None
    except Exception as e:
        print(f"Exception during request: {e}")
        return None
        
def format_alert(feature: dict) -> str:
    """Format an alert as a readable string"""
    props = feature["properties"]
    return f"""
        Event: {props.get('event', 'Unknown')}
        Area: {props.get('areaDesc', 'Unknown')}
        Severity: {props.get('severity', 'Unknown')}
        Description: {props.get('description', "No description provided")}
        Instructions: {props.get('instruction', 'No instructions provided')}
        """
    
@mcp.tool()
async def get_weather_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state : two-letter US state code (e.g. CA, NY)
    """
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch data"
    
    if not data["features"]:
        return "No active data found for the given state"
    
    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)



    

    
    
