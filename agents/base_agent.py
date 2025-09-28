"""Base agent class that all specialized agents will inherit from."""

class BaseAgent:
    def __init__(self):
        """Initialize the base agent."""
        self.name = self.__class__.__name__
    
    def process(self, data, **kwargs):
        """
        Process data according to the agent's specialty.
        
        Args:
            data: The data to process
            **kwargs: Additional arguments specific to each agent
            
        Returns:
            Processed data
        """
        raise NotImplementedError("Each agent must implement its own process method.")
    
    def __str__(self):
        return f"{self.name} Agent"