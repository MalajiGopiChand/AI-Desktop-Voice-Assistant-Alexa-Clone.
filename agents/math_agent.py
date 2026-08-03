"""Mathematical engine — arithmetic, algebra, calculus, graphs."""
import os
import re
from agents.base_agent import BaseAgent


class MathAgent(BaseAgent):
    def __init__(self):
        super().__init__("math_agent")

    def execute(self, action, params):
        try:
            handlers = {
                "calculate": self._calculate,
                "solve_equation": self._solve_equation,
                "differentiate": self._differentiate,
                "integrate": self._integrate,
                "plot_function": self._plot_function,
                "statistics": self._statistics,
            }
            handler = handlers.get(action)
            if not handler:
                return {"success": False, "message": f"Unknown action: {action}", "data": {}}
            return handler(params)
        except Exception as e:
            return {"success": False, "message": str(e), "data": {}}

    def _calculate(self, params):
        expr = params.get("expression", "")
        # Normalize spoken math operators
        expr = expr.replace("^", "**").replace("×", "*").replace("÷", "/")
        expr = re.sub(r'\bmultiplied by\b', '*', expr, flags=re.I)
        expr = re.sub(r'\btimes\b', '*', expr, flags=re.I)
        expr = re.sub(r'\binto\b', '*', expr, flags=re.I)
        expr = re.sub(r'\bdivided by\b', '/', expr, flags=re.I)
        expr = re.sub(r'(\d+)\s*[xX]\s*(\d+)', r'\1 * \2', expr)

        try:
            import sympy as sp
            result = sp.sympify(expr)
            if result.is_number:
                val = float(result.evalf())
                return {"success": True, "message": f"The result is {val:g}", "data": {"result": val}}
        except Exception:
            pass

        import math
        safe = {"sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "log": math.log, "pi": math.pi, "e": math.e, "abs": abs, "pow": pow}
        val = eval(expr, {"__builtins__": {}}, safe)
        return {"success": True, "message": f"The result is {val}", "data": {"result": val}}

    def _solve_equation(self, params):
        import sympy as sp
        eq = params.get("equation", "x**2 - 4")
        x = sp.Symbol("x")
        solutions = sp.solve(sp.sympify(eq), x)
        msg = f"Solutions: {solutions}"
        return {"success": True, "message": msg, "data": {"solutions": [str(s) for s in solutions]}}

    def _differentiate(self, params):
        import sympy as sp
        expr = params.get("expression", "x**2")
        var = params.get("variable", "x")
        x = sp.Symbol(var)
        result = sp.diff(sp.sympify(expr), x)
        return {"success": True, "message": f"Derivative: {result}", "data": {"result": str(result)}}

    def _integrate(self, params):
        import sympy as sp
        expr = params.get("expression", "x**2")
        var = params.get("variable", "x")
        x = sp.Symbol(var)
        result = sp.integrate(sp.sympify(expr), x)
        return {"success": True, "message": f"Integral: {result}", "data": {"result": str(result)}}

    def _plot_function(self, params):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        expr = params.get("expression", "sin(x)")
        x = np.linspace(-10, 10, 400)
        y = eval(expr, {"__builtins__": {}}, {"x": x, "sin": np.sin, "cos": np.cos, "tan": np.tan, "exp": np.exp, "log": np.log, "sqrt": np.sqrt, "pi": np.pi})

        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.grid(True)
        ax.set_title(expr)
        from config import CHARTS_DIR
        out = os.path.join(CHARTS_DIR, f"plot_{int(__import__('time').time())}.png")
        plt.savefig(out)
        plt.close()
        return {"success": True, "message": f"Plot saved to {out}", "data": {"path": out}}

    def _statistics(self, params):
        import numpy as np
        data = params.get("data", [])
        if isinstance(data, str):
            data = [float(x) for x in data.split(",")]
        arr = np.array(data, dtype=float)
        msg = f"Mean: {arr.mean():.4f}, Std: {arr.std():.4f}, Min: {arr.min():.4f}, Max: {arr.max():.4f}"
        return {"success": True, "message": msg, "data": {"mean": float(arr.mean()), "std": float(arr.std())}}
