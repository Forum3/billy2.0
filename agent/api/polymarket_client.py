import logging
import requests
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

class PolymarketClient:
    """Client for interacting with the Polymarket API"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://gamma-api.polymarket.com"):
        """
        Initialize the Polymarket API client.
        
        Args:
            api_key: API key for authenticating with Polymarket (optional for public endpoints)
            base_url: Base URL for the Polymarket API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.logger = logging.getLogger("nba_agent.polymarket")
        self.headers = {}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        self.logger.info("Polymarket API client initialized")
        
        # NBA team initials mapping
        self.nba_team_initials = {
            "Atlanta Hawks": "atl",
            "Boston Celtics": "bos",
            "Brooklyn Nets": "bkn",
            "Charlotte Hornets": "cha",
            "Chicago Bulls": "chi",
            "Cleveland Cavaliers": "cle",
            "Dallas Mavericks": "dal",
            "Denver Nuggets": "den",
            "Detroit Pistons": "det",
            "Golden State Warriors": "gsw",
            "Houston Rockets": "hou",
            "Indiana Pacers": "ind",
            "Los Angeles Clippers": "lac",
            "Los Angeles Lakers": "lal",
            "Memphis Grizzlies": "mem",
            "Miami Heat": "mia",
            "Milwaukee Bucks": "mil",
            "Minnesota Timberwolves": "min",
            "New Orleans Pelicans": "nop",
            "New York Knicks": "nyk",
            "Oklahoma City Thunder": "okc",
            "Orlando Magic": "orl",
            "Philadelphia 76ers": "phi",
            "Phoenix Suns": "phx",
            "Portland Trail Blazers": "por",
            "Sacramento Kings": "sac",
            "San Antonio Spurs": "sas",
            "Toronto Raptors": "tor",
            "Utah Jazz": "uta",
            "Washington Wizards": "was"
        }
    
    def get_market_by_slug(self, slug: str) -> Dict[str, Any]:
        """
        Get market details by slug.
        
        Args:
            slug: Market slug (e.g., "nba-gsw-lal-2023-11-10")
            
        Returns:
            Market details
        """
        try:
            url = f"{self.base_url}/events"
            params = {"slug": slug}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data and isinstance(data, list) and len(data) > 0:
                self.logger.info(f"Retrieved market data for slug: {slug}")
                return data[0]
            else:
                self.logger.warning(f"No market data found for slug: {slug}")
                return {}
            
        except Exception as e:
            self.logger.error(f"Error retrieving market data for {slug}: {str(e)}")
            return {}
    
    def construct_nba_slug(self, home_team: str, away_team: str, game_date: Optional[datetime] = None) -> str:
        """
        Construct a Polymarket slug for an NBA game.
        
        Args:
            home_team: Home team name
            away_team: Away team name
            game_date: Game date (defaults to today or next day if current time is late)
            
        Returns:
            Formatted slug for Polymarket API
        """
        home_initial = self.nba_team_initials.get(away_team, "unk")
        away_initial = self.nba_team_initials.get(home_team, "unk")
        
        if not game_date:
            # Default to today's date or next day if it's late
            pst_now = datetime.utcnow() - timedelta(hours=8)
            next_game_date = pst_now.replace(hour=23, minute=59, second=0, microsecond=0)
            if pst_now >= next_game_date:
                next_game_date += timedelta(days=1)
            game_date = next_game_date
        
        date_str = game_date.strftime("%Y-%m-%d")
        slug = f"nba-{home_initial}-{away_initial}-{date_str}"
        self.logger.debug(f"Constructed slug: {slug}")
        return slug
        
    def extract_start_time(self, description: str) -> Optional[datetime]:
        """
        Extract start time from Polymarket description and return datetime object.
        
        Args:
            description: Market description string from Polymarket
            
        Returns:
            Datetime object or None if parsing fails
        """
        try:
            if not description:
                return None
            
            # Find the date and time in the description
            pattern = r"scheduled for ([A-Za-z]+ \d{1,2}) at (\d{1,2}:\d{2})([AP]M) ET"
            match = re.search(pattern, description)
            
            if match:
                date_str, time_str, meridiem = match.groups()
                # Convert to datetime object
                current_year = datetime.now().year
                full_datetime_str = f"{date_str} {current_year} {time_str}{meridiem}"
                game_time = datetime.strptime(full_datetime_str, "%B %d %Y %I:%M%p")
                # Convert ET to UTC (add 4 hours)
                game_time = game_time + timedelta(hours=4)
                return game_time
            return None
        except Exception as e:
            self.logger.error(f"Error extracting start time: {str(e)}")
            return None
    
    def get_nba_markets(self) -> List[Dict[str, Any]]:
        """
        Get all available NBA markets.
        
        Returns:
            List of NBA markets
        """
        try:
            url = f"{self.base_url}/events"
            params = {"category": "NBA"}
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data and isinstance(data, list):
                self.logger.info(f"Retrieved {len(data)} NBA markets")
                return data
            else:
                self.logger.warning("No NBA markets found")
                return []
            
        except Exception as e:
            self.logger.error(f"Error retrieving NBA markets: {str(e)}")
            return []
    
    def get_market_odds(self, market_id: str) -> Dict[str, float]:
        """
        Get current odds for a market.
        
        Args:
            market_id: Market ID
            
        Returns:
            Dictionary with outcome names as keys and probabilities as values
        """
        try:
            url = f"{self.base_url}/markets/{market_id}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()
            outcomes = {}
            
            if "outcomes" in data:
                for outcome in data["outcomes"]:
                    name = outcome.get("name")
                    probability = outcome.get("probability")
                    if name and probability is not None:
                        outcomes[name] = float(probability)
                
                self.logger.info(f"Retrieved odds for market {market_id}")
                return outcomes
            else:
                self.logger.warning(f"No outcomes found for market {market_id}")
                return {}
            
        except Exception as e:
            self.logger.error(f"Error retrieving odds for market {market_id}: {str(e)}")
            return {} 