"""Starter deck loaded into an empty database (PROJECT.md §3).

~20 cards about MCP / MCP Apps / Hermes, so studying Recall teaches the
stack it is built on.
"""

SEED_DECK = "mcp-basics"

SEED_CARDS = [
    ("What does MCP stand for?", "Model Context Protocol."),
    (
        "What are the three MCP primitives a server can expose?",
        "Tools, resources, and prompts.",
    ),
    (
        "What transport does a local MCP server usually use?",
        "stdio (standard input/output).",
    ),
    (
        "What transport does a remote MCP server use?",
        "Streamable HTTP.",
    ),
    (
        "What is FastMCP?",
        "A Python framework for building MCP servers (the fastmcp package).",
    ),
    (
        "What does the MCP Apps extension add?",
        "Interactive UIs rendered inline by the host, alongside tools.",
    ),
    (
        "What URI scheme identifies an MCP App UI resource?",
        "ui:// (e.g. ui://recall/flashcard).",
    ),
    (
        "What mime type marks an HTML resource as an MCP App?",
        "text/html;profile=mcp-app",
    ),
    (
        "How is a UI resource linked to a tool in FastMCP?",
        "The tool's AppConfig sets resource_uri to the ui:// resource.",
    ),
    (
        "Where does an MCP App UI run in the host?",
        "In a sandboxed iframe.",
    ),
    (
        "What messaging protocol do MCP App iframes use with the host?",
        "JSON-RPC 2.0 over postMessage.",
    ),
    (
        "What method does an MCP App iframe use to call a tool?",
        "tools/call",
    ),
    (
        "How does the host give an MCP App its opening data?",
        "Via the ui/notifications/tool-result notification.",
    ),
    (
        "What is Hermes Agent?",
        "NousResearch's open-source coding agent.",
    ),
    (
        "What is the Hermes WebUI?",
        "A browser interface for Hermes with full CLI parity (no TUI).",
    ),
    (
        "What algorithm does Recall use to schedule reviews?",
        "SM-2, the classic Anki-style spaced-repetition algorithm.",
    ),
    (
        "In SM-2, what happens to the interval when you grade a card 'again'?",
        "It resets to 1 day.",
    ),
    (
        "What is a card's ease factor in SM-2?",
        "A multiplier (min 1.3) that grows the interval on good reviews.",
    ),
    (
        "What are Recall's four tools?",
        "add_card, review_next, grade_card, stats.",
    ),
    (
        "What are the four grade ratings in Recall?",
        "again, hard, good, easy.",
    ),
]
