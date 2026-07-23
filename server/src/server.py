from fastmcp import FastMCP

from tools.add_card import add_card
from tools.grade_card import grade_card
from tools.ping import ping
from tools.review_next import review_next
from tools.stats import stats

mcp = FastMCP("Recall")

mcp.tool()(ping)
mcp.tool()(add_card)
mcp.tool()(review_next)
mcp.tool()(grade_card)
mcp.tool()(stats)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
