import logging
import requests
from typing import Dict, Any, List, Optional

class SportsTensorClient:
    """Client for interacting with the SportsTensor API"""
    
    def __init__(self, api_key: str = "hPW29W7OuyU3-qt5qdW6JIOi09PVB3THV7lSkwKhghQ", 
                base_url: str = "https://mm-api.sportstensor.com"):
        """
        Initialize the SportsTensor API client.
        
        Args:
            api_key: API key for authenticating with SportsTensor
            base_url: Base URL for the SportsTensor API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.logger = logging.getLogger("nba_agent.sportstensor")
        self.headers = {"ST_API_KEY": api_key}
        self.logger.info("SportsTensor API client initialized")
    
    def get_nba_predictions(self) -> List[Dict[str, Any]]:
        """
        Get NBA game predictions from SportsTensor.
        
        Returns:
            List of game predictions with win probabilities
        """
        try:
            url = f"{self.base_url}/predictions/nba"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            predictions = data.get("predictions", [])
            
            self.logger.info(f"Retrieved {len(predictions)} NBA predictions from SportsTensor")
            return predictions
            
        except Exception as e:
            self.logger.error(f"Error retrieving NBA predictions: {str(e)}")
            return []
    
    def get_game_prediction(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Get prediction for a specific NBA game.
        
        Args:
            game_id: Unique identifier for the game
            
        Returns:
            Dictionary containing game prediction or None if not found
        """
        try:
            url = f"{self.base_url}/predictions/nba/{game_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            prediction = data.get("prediction")
            
            if prediction:
                self.logger.info(f"Retrieved prediction for game {game_id}")
                return prediction
            else:
                self.logger.warning(f"No prediction found for game {game_id}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving prediction for game {game_id}: {str(e)}")
            return None
    
    def get_model_performance(self) -> Dict[str, Any]:
        """
        Get performance metrics for the SportsTensor NBA model.
        
        Returns:
            Dictionary containing model performance metrics
        """
        try:
            url = f"{self.base_url}/performance/nba"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            performance = data.get("performance", {})
            
            self.logger.info("Retrieved NBA model performance metrics")
            return performance
            
        except Exception as e:
            self.logger.error(f"Error retrieving model performance: {str(e)}")
            return {} 