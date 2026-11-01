
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


@mcp.tool()
def multiple(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract b from a"""
    return a - b


@mcp.tool()
def divide(a: float, b: float) -> str:
    """Divide a by b"""
    if b == 0:
        return "Cannot divide by zero"
    return str(a / b)


if __name__ == "__main__":
    mcp.run(transport="stdio")