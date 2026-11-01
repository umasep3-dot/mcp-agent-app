
import sys
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")


@mcp.tool()
async def get_weather(location: str) -> str:
    """Get the current weather for a city, e.g. 'Chennai' or 'London'."""
    async with httpx.AsyncClient(timeout=10) as client:
        geo = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": location, "count": 1},
        )
        results = geo.json().get("results")
        if not results:
            return f"Could not find a place called '{location}'."
        place = results[0]

        wx = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
            },
        )
        cur = wx.json()["current"]

    return (
        f"{place['name']}, {place.get('country', '')}: "
        f"{cur['temperature_2m']}°C, humidity {cur['relative_humidity_2m']}%, "
        f"wind {cur['wind_speed_10m']} km/h"
    )


if __name__ == "__main__":
    transport = sys.argv[1] if len(sys.argv) > 1 else "streamable-http"
    mcp.run(transport=transport)