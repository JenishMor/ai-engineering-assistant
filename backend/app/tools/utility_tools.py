
import ast
import operator
from datetime import datetime, timezone

from langchain.tools import tool

_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def _evaluate(node):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value

    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_evaluate(node.operand))

    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)

        if isinstance(node.op, ast.Pow) and abs(right) > 10:
            raise ValueError("Exponent is too large")

        result = _ALLOWED_OPERATORS[type(node.op)](left, right)

        if isinstance(result, (int, float)) and abs(result) > 1e100:
            raise ValueError("Result is too large")

        return result

    raise ValueError("Unsupported arithmetic expression")

@tool
def calculate(expression: str) -> str:
    """Calculate a basic arithmetic expression, such as (25 * 4) + 10."""
    try:
        tree = ast.parse(expression, mode="eval")
        result = _evaluate(tree.body)
        return str(result)
    except (ValueError, TypeError, ZeroDivisionError, OverflowError) as exc:
        return f"Calculation error: {exc}"

@tool
def get_current_utc_time() -> str:
    """Get the current date and time in UTC."""
    return datetime.now(timezone.utc).isoformat()
