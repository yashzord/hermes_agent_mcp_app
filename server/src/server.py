from fastmcp import FastMCP

from tools.ping import ping

mcp = FastMCP("Recall")

mcp.tool()(ping)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
