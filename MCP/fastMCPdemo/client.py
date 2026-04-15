from fastmcp import Client

# client = Client("https://api.githubcopilot.com/mcp/")


# client.py
import asyncio
from fastmcp.client.transports import StdioTransport

async def main():
    weather_server = StdioTransport(
        command="npx",
        args=["-y", "@dangahagan/weather-mcp@latest"]
    )

    async with Client(weather_server) as client:
        tools = await client.list_tools()
        print("Available tools:", tools)

        result = await client.call_tool(
            "get_current_conditions",
            {
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        )
        print("Weather:", result)

asyncio.run(main())



# import asyncio
# from fastmcp import Client

# client = Client("http://localhost:8000/mcp")

# async def call_tool():
#     async with client:
#         result = await client.call_tool(
#             "search_github_repositories",
#             {"query": "fastapi"}
#         )
#         print(result.content[0])

# asyncio.run(call_tool())


# import asyncio
# from fastmcp import Client

# async def list_tools():
#     async with Client("http://localhost:8000/mcp") as client:
#         tools = await client.list_tools()
#         print(tools)

# asyncio.run(list_tools())
