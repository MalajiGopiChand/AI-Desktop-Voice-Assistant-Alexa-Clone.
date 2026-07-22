class BaseAgent:
    def __init__(self, name):
        self.name = name

    def execute(self, action, params):
        """
        Executes a given action with parameters.
        Must be implemented by subclasses.
        Returns a dict: {"success": bool, "message": str, "data": dict}
        """
        raise NotImplementedError("Subclasses must implement execute()")
