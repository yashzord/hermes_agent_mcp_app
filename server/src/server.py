import os
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.apps import AppConfig

from tools.add_card import add_card
from tools.grade_card import grade_card
from tools.ping import ping
from tools.review_next import review_next
from tools.stats import stats

mcp = FastMCP("Recall")

_UI_HTML = Path(__file__).parent / "ui" / "flashcard.html"


def flashcard_resource() -> str:
    """Return the flashcard UI HTML content."""
    return _UI_HTML.read_text(encoding="utf-8")


# The resource IS the UI: mime type marks it as an MCP App, no resource_uri here.
mcp.resource(
    uri="ui://recall/flashcard",
    name="Recall Flashcard UI",
    mime_type="text/html;profile=mcp-app",
    description="Interactive flashcard review interface",
)(flashcard_resource)

mcp.tool()(ping)
mcp.tool()(add_card)
# review_next points at the UI resource so hosts render the flashcard widget.
mcp.tool(app=AppConfig(resource_uri="ui://recall/flashcard"))(review_next)
mcp.tool()(grade_card)
mcp.tool()(stats)


def main():
    # stdio for local dev / MCP Inspector; http (Streamable HTTP) for deploy.
    transport = os.environ.get("RECALL_TRANSPORT", "stdio")
    if transport == "http":
        # Standard (stateful) Streamable HTTP - the reference mode MCP Apps
        # hosts like Claude.ai connect to.
        mcp.run(
            transport="http",
            host="0.0.0.0",  # noqa: S104 - container needs to bind all interfaces
            port=int(os.environ.get("PORT", "8000")),
        )
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
