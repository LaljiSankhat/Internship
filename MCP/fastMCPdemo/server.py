# from fastmcp import FastMCP

# mcp = FastMCP("My MCP Server")

# @mcp.tool
# def greet(name: str) -> str:
#     return f"Hello, {name}!"

# if __name__ == "__main__":
#     mcp.run()


from fastmcp import FastMCP
import subprocess
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

mcp = FastMCP("Grep MCP Server")

@mcp.tool
def grep(
    pattern: str,
    path: str = ".",
    recursive: bool = True,
    ignore_case: bool = False
) -> str:
    """
    Search for a pattern in files using grep.
    """

    cmd = [
        "grep",
        "-I",                      # ignore binary files
        "--exclude-dir=__pycache__"
    ]

    if recursive:
        cmd.append("-R")

    if ignore_case:
        cmd.append("-i")

    # show line number + filename
    cmd.extend(["-n", pattern, path])

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        if result.returncode == 1:
            return "No matches found."

        if result.stderr:
            return f"Error:\n{result.stderr}"

        return result.stdout.strip()

    except Exception as e:
        return f"Exception occurred: {str(e)}"



GITHUB_SEARCH_API = "https://api.github.com/search/code"

# 🔒 Controlled repos (important)
REPOS = [
    "fastapi/fastapi",
    "pallets/flask",
    "django/django",
]

@mcp.tool
def search_github_files(
    topic: str,
    language: str = "python",
    max_results: int = 10,
) -> str:
    """
    Search files on GitHub using GitHub Search API.
    """

    results = []

    for repo in REPOS:
        query = f"{topic} in:file language:{language} repo:{repo}"

        response = requests.get(
            GITHUB_SEARCH_API,
            params={"q": query, "per_page": max_results},
            headers={
                "Accept": "application/vnd.github+json",
                # Optional (recommended)
                # "Authorization": "Bearer YOUR_GITHUB_TOKEN",
            },
            timeout=10,
        )

        if response.status_code != 200:
            continue

        for item in response.json().get("items", []):
            results.append(
                f"{repo}/{item['path']}\n{item['html_url']}"
            )

    if not results:
        return "No matching files found on GitHub."

    return "\n\n".join(results[:max_results])

@mcp.tool
def search_github_repositories(query: str):
    """
    Search for GitHub repositories related to a specific research topic.
    Returns a list of repositories with their descriptions and star counts.
    """
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"

    items = response.json().get('items', [])[:5]  # Get top 5 results
    results = []
    for item in items:
        results.append({
            "name": item['full_name'],
            "description": item['description'],
            "url": item['html_url'],
            "stars": item['stargazers_count']
        })
    return results

if __name__ == "__main__":
    mcp.run()
