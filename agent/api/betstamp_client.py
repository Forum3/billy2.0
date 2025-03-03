import logging
import requests
from typing import Dict, List, Any, Optional

class BetstampClient:
    """Client for interacting with the Betstamp API"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.pro.betstamp.com/api"):
        """
        Initialize the Betstamp API client.
        
        Args:
            api_key: API key for authenticating with Betstamp
            base_url: Base URL for the Betstamp API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-KEY": api_key
        }
        self.logger = logging.getLogger("nba_agent.betstamp_client")
        self.logger.info("Betstamp API client initialized")
    
    def get_markets(self, 
                   league: str = "NBA", 
                   book_ids: List[int] = [200, 999], 
                   bet_types: List[str] = ["moneyline", "spread", "total"],
                   periods: List[str] = ["FT"],
                   is_live: bool = False,
                   timedelta: int = 24) -> Dict[str, Any]:
        """
        Get available markets according to parameters.
        
        Args:
            league: League to get markets for (NBA, NFL, etc.)
            book_ids: List of book IDs to include
            bet_types: List of bet types to include
            periods: List of periods to include (FT = full time)
            is_live: Whether to include live markets
            timedelta: Hours window for games
            
        Returns:
            Dictionary containing market data
        """
        self.logger.info(f"Fetching {league} markets for {bet_types} from books {book_ids}")
        
        try:
            # Convert lists to comma-separated strings for query params
            book_ids_str = ",".join(map(str, book_ids))
            bet_types_str = ",".join(bet_types)
            periods_str = ",".join(periods)
            
            # Build query parameters
            params = {
                "league": league,
                "book_ids": book_ids_str,
                "bet_types": bet_types_str,
                "periods": periods_str,
                "is_live": str(is_live).lower(),
                "timedelta": timedelta
            }
            
            # Make request
            url = f"{self.base_url}/markets"
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Log success
            market_count = len(data.get("markets", []))
            self.logger.info(f"Successfully retrieved {market_count} markets")
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching markets: {str(e)}")
            return {"markets": []}
    
    def get_fixtures(self, league: str = "NBA", timedelta: int = 24) -> Dict[str, Any]:
        """
        Get upcoming fixtures (games).
        
        Args:
            league: League to get fixtures for
            timedelta: Hours window for games
            
        Returns:
            Dictionary containing fixture data
        """
        self.logger.info(f"Fetching {league} fixtures")
        
        try:
            # Build query parameters
            params = {
                "league": league,
                "timedelta": timedelta
            }
            
            # Make request
            url = f"{self.base_url}/fixtures"
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Log success
            fixture_count = len(data.get("fixtures", []))
            self.logger.info(f"Successfully retrieved {fixture_count} fixtures")
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching fixtures: {str(e)}")
            return {"fixtures": []}
    
    def get_teams(self, league: str = "NBA") -> Dict[str, Any]:
        """
        Get teams for a league.
        
        Args:
            league: League to get teams for
            
        Returns:
            Dictionary containing team data
        """
        self.logger.info(f"Fetching {league} teams")
        
        try:
            # Build query parameters
            params = {
                "league": league,
                "return_map": "true"  # Get teams as a map for easier lookup
            }
            
            # Make request
            url = f"{self.base_url}/teams"
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Log success
            team_count = len(data.get("teams", {}))
            self.logger.info(f"Successfully retrieved {team_count} teams")
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching teams: {str(e)}")
            return {"teams": {}}
    
    def get_players(self, league: str = "NBA") -> Dict[str, Any]:
        """
        Get players for a league.
        
        Args:
            league: League to get players for
            
        Returns:
            Dictionary containing player data
        """
        self.logger.info(f"Fetching {league} players")
        
        try:
            # Build query parameters
            params = {
                "league": league,
                "return_map": "true"  # Get players as a map for easier lookup
            }
            
            # Make request
            url = f"{self.base_url}/players"
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Log success
            player_count = len(data.get("players", {}))
            self.logger.info(f"Successfully retrieved {player_count} players")
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error fetching players: {str(e)}")
            return {"players": {}} 