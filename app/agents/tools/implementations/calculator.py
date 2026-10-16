"""
Calculator tool implementation.

Evaluates mathematical expressions safely using AST parsing.
"""

from __future__ import annotations

import ast
import operator
from typing import Any

from app.agents.tools.base import BaseTool
from app.agents.tools.metadata import ToolMetadata
from app.agents.tools.parameters import ToolParameter, ToolParameterType
from app.agents.tools.schemas import ToolCall, ToolResult


_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_node(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    elif isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        op_type = type(node.op)
        if op_type in _OPERATORS:
            return _OPERATORS[op_type](left, right)
    elif isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        op_type = type(node.op)
        if op_type in _OPERATORS:
            return _OPERATORS[op_type](operand)
    raise ValueError("Invalid arithmetic expression.")


def safe_eval(expr: str) -> str:
    parsed = ast.parse(expr.strip(), mode="eval")
    result = _eval_node(parsed.body)
    return str(result)


class CalculatorTool(BaseTool):
    """
    Tool for performing safe mathematical calculations.
    """

    @property
    def name(self) -> str:
        return "calculator"

    @property
    def description(self) -> str:
        return "Evaluates mathematical expressions safely."

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name=self.name,
            description=self.description,
            parameters=[
                ToolParameter(
                    name="expression",
                    type=ToolParameterType.STRING,
                    description="Mathematical formula to calculate (e.g., '10 + 5 * 2').",
                    required=True,
                ),
            ],
        )

    async def execute(self, call: ToolCall) -> ToolResult:
        expression = call.arguments.get("expression")
        if not expression:
            return ToolResult(
                success=False,
                output="",
                error="Missing required argument 'expression'.",
            )

        try:
            result = safe_eval(str(expression))
            return ToolResult(
                success=True,
                output=result,
            )
        except Exception as exc:
            return ToolResult(
                success=False,
                output="",
                error=f"Calculation error: {exc}",
            )
