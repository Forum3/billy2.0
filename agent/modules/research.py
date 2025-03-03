"""
Research module for the NBA Betting Agent.
This module handles gathering and analyzing NBA data.
"""

import logging
import time
import os
import json
from typing import Dict, List, Any, Optional
import requests
from datetime import datetime, timedelta
from agent.api.betstamp_client import BetstampClient
from agent.modules.base import BaseModule
from agent.utils.response_formatter import BillyResponseFormatter
from agent.utils.firecrawl_utils import FirecrawlUtils

class ResearchModule:
    """
    Research module for the NBA betting agent.
    
    This class handles gathering and analyzing NBA data,
    including team statistics, player performance, and betting odds.
    """
    
    def __init__(self, memory, config: Dict[str, Any]):
        """
        Initialize the research module.
        
        Args:
            memory: Memory client instance
            config: Configuration settings for the agent
        """
        self.logger = logging.getLogger("nba_agent.research")
        self.memory = memory
        self.config = config
        self.research_config = config.get('research', {})
        
        # Store reference to controller for accessing persona
        self.controller = None
        
        self.logger.info("Research module initialized")
    
    def set_controller(self, controller):
        """
        Set the controller reference for accessing persona.
        
        Args:
            controller: The agent controller instance
        """
        self.controller = controller
    
    def generate_research_summary(self, research_results: List[Dict[str, Any]]) -> str:
        """
        Generate a research summary in Billy's style.
        
        Args:
            research_results: List of research results
            
        Returns:
            Formatted research summary
        """
        if self.controller and hasattr(self.controller, 'persona'):
            formatter = BillyResponseFormatter(self.controller.persona)
            return formatter.format_research_summary(research_results)
        else:
            # Fallback if controller or persona not available
            count = len(research_results)
            return f"analyzed {count} games for today's slate."
    
    def get_last_research_time(self) -> float:
        """
        Get the timestamp of the last research operation.
        
        Returns:
            Timestamp as a float
        """
        # Get the last research time from memory context
        last_time = self.memory.get_context("last_research_time")
        
        # If not available, return current time
        if last_time is None:
            return time.time()
            
        return last_time
    
    def initialize_research_queue(self) -> None:
        """Initialize the research queue with upcoming games"""
        self.logger.info("Initializing research queue")
        
        try:
            # Fetch upcoming games from Betstamp API
            upcoming_games = self._fetch_upcoming_games()
            
            # Store in memory context
            pending_games = []
            
            # Create a structured format for each game
            for game in upcoming_games:
                pending_games.append({
                    "content": f"Upcoming game: {game['away_team']} @ {game['home_team']} on {game['game_date']}",
                    "metadata": {
                        "type": "upcoming_game",
                        "game_id": game["game_id"],
                        "home_team": game["home_team"],
                        "away_team": game["away_team"],
                        "game_date": game["game_date"],
                        "research_status": "pending"
                    }
                })
            
            # Store the pending games in memory context
            self.memory.update_context("pending_games", pending_games)
            
            # Also store in traditional memory for backward compatibility
            self.memory.add({
                "content": f"Initialized research queue with {len(upcoming_games)} upcoming games",
                "metadata": {
                    "type": "research_queue",
                    "games_count": len(upcoming_games),
                    "timestamp": datetime.now().isoformat()
                }
            })
                
            self.logger.info(f"Research queue initialized with {len(upcoming_games)} games")
            
        except Exception as e:
            self.logger.error(f"Error initializing research queue: {str(e)}")
            raise
    
    def execute_research_tasks(self) -> List[Dict[str, Any]]:
        """Execute research tasks for upcoming NBA games."""
        try:
            # Get pending games from memory
            pending_games = self.memory.get_pending_games()
            if not pending_games:
                self.logger.info("No pending games found for research")
                return []
            
            # Fetch NBA odds data
            odds_data = {}
            
            # Step 1: Initialize the Betstamp client
            betstamp_client = BetstampClient(
                api_key=self.config.get("betstamp", {}).get("api_key"),
                base_url=self.config.get("betstamp", {}).get("base_url")
            )
            
            # Step 2: Get fixtures (upcoming games)
            fixtures = betstamp_client.get_fixtures(league="NBA")
            if not fixtures:
                self.logger.warning("No fixtures found from Betstamp API")
            
            # Step 3: Get markets (odds) for each fixture
            for fixture_id, fixture_data in fixtures.items():
                markets = betstamp_client.get_markets(
                    league="NBA",
                    book_ids=self.config.get("betstamp", {}).get("book_ids"),
                    bet_types=self.config.get("betstamp", {}).get("bet_types"),
                    periods=self.config.get("betstamp", {}).get("periods"),
                    fixture_id=fixture_id
                )
                
                if markets:
                    # Process and store the odds data
                    home_team = fixture_data.get("home_team")
                    away_team = fixture_data.get("away_team")
                    
                    odds_data[fixture_id] = {
                        "fixture_id": fixture_id,
                        "home_team": home_team,
                        "away_team": away_team,
                        "start_time": fixture_data.get("start_time"),
                        "markets": markets
                    }
            
            self.logger.info(f"Fetched odds data for {len(odds_data)} games")
            
            # Process each pending game
            research_results = []
            
            for game in pending_games:
                game_metadata = game.get("metadata", {})
                game_id = game_metadata.get("game_id")
                home_team = game_metadata.get("home_team")
                away_team = game_metadata.get("away_team")
                
                # Perform various research tasks for this game
                injury_data = self.fetch_injury_reports(home_team, away_team)
                team_stats = self.fetch_team_stats(home_team, away_team)
                recent_news = self.fetch_recent_news(home_team, away_team)
                
                # Get odds for this specific game
                game_odds = {}
                for fixture_id, fixture_data in odds_data.items():
                    if (fixture_data["home_team"] == home_team and 
                        fixture_data["away_team"] == away_team):
                        game_odds = fixture_data
                        break
                
                # Combine research results
                game_research = {
                    "game_id": game_id,
                    "home_team": home_team,
                    "away_team": away_team,
                    "injury_data": injury_data,
                    "team_stats": team_stats,
                    "recent_news": recent_news,
                    "odds_data": game_odds,
                    "timestamp": datetime.now().isoformat(),
                    "summary": f"Completed research for {away_team} @ {home_team}",
                    "source": "research_module"
                }
                
                research_results.append(game_research)
                
                # Update game research status in memory
                self.memory.update_game_research_status(
                    game_id=game_id,
                    status="completed",
                    timestamp=datetime.now().isoformat(),
                    message=f"Research completed for {away_team} @ {home_team}"
                )
                
                self.logger.info(f"Completed research for game: {away_team} @ {home_team}")
            
            # Store the current time as the last research time
            current_time = time.time()
            self.memory.update_context("last_research_time", current_time)
            self.logger.info(f"Updated last research time: {datetime.fromtimestamp(current_time).isoformat()}")
            
            # Generate and log a research summary in Billy's style
            if research_results:
                summary = self.generate_research_summary(research_results)
                self.logger.info(f"Research summary: {summary}")
                
                # Store the summary in memory
                self.memory.add({
                    "content": summary,
                    "metadata": {
                        "type": "research_summary",
                        "games_count": len(research_results),
                        "timestamp": datetime.now().isoformat(),
                        "persona": "billy"
                    }
                })
            
            return research_results
            
        except Exception as e:
            self.logger.error(f"Error executing research tasks: {str(e)}")
            return []
    
    def fetch_injury_reports(self, home_team: str = None, away_team: str = None) -> Dict[str, Any]:
        """
        Fetch injury reports for NBA teams using Firecrawl.
        
        Args:
            home_team: Optional home team name to limit report to specific teams
            away_team: Optional away team name to limit report to specific teams
            
        Returns:
            Dictionary containing structured injury data
        """
        self.logger.info(f"Fetching injury reports for {away_team} @ {home_team}")
        
        # Check if Firecrawl is enabled in configuration
        if not self.config.get("firecrawl", {}).get("enabled", False):
            self.logger.warning("Firecrawl is disabled in configuration, using fallback injury data")
            return self._get_fallback_injury_data(home_team, away_team)
        
        try:
            # Use the FirecrawlUtils to get injury data
            injury_crawler = FirecrawlUtils(self.config)
            all_injury_data = injury_crawler.fetch_injury_reports()
            
            # If specific teams are requested, filter the data
            if home_team or away_team:
                filtered_data = {}
                
                if home_team and home_team in all_injury_data:
                    filtered_data[home_team] = all_injury_data[home_team]
                    
                if away_team and away_team in all_injury_data:
                    filtered_data[away_team] = all_injury_data[away_team]
                    
                # If we couldn't find exact team name matches, try partial matching
                if not filtered_data:
                    for team_name, team_data in all_injury_data.items():
                        if home_team and home_team.lower() in team_name.lower():
                            filtered_data[team_name] = team_data
                        elif away_team and away_team.lower() in team_name.lower():
                            filtered_data[team_name] = team_data
                
                injury_data = filtered_data
            else:
                injury_data = all_injury_data
            
            # Store in memory for future reference
            if injury_data:
                self._store_injury_data_in_memory(injury_data)
                
            self.logger.info(f"Fetched injury data for {len(injury_data)} teams")
            return injury_data
            
        except Exception as e:
            self.logger.error(f"Error fetching injury reports with Firecrawl: {str(e)}")
            # Fall back to basic injury data if Firecrawl fails
            return self._get_fallback_injury_data(home_team, away_team)

    def _store_injury_data_in_memory(self, injury_data: Dict[str, Any]) -> None:
        """
        Store injury data in memory for future reference.
        
        Args:
            injury_data: Dictionary containing structured injury data
        """
        try:
            # Store the entire injury dataset
            self.memory.add({
                "content": f"NBA Injury Report - {len(injury_data)} teams affected",
                "metadata": {
                    "type": "injury_report",
                    "timestamp": datetime.now().isoformat(),
                    "data": injury_data
                }
            })
            
            # Also store individual team reports for easier retrieval
            for team_name, players in injury_data.items():
                player_count = len(players)
                if player_count > 0:
                    key_players = [p["name"] for p in players][:3]  # List first 3 players
                    
                    content = f"Injury report for {team_name}: {player_count} players affected"
                    if key_players:
                        content += f" including {', '.join(key_players)}"
                    
                    self.memory.add({
                        "content": content,
                        "metadata": {
                            "type": "team_injury_report",
                            "team": team_name,
                            "player_count": player_count,
                            "timestamp": datetime.now().isoformat(),
                            "data": players
                        }
                    })
            
        except Exception as e:
            self.logger.error(f"Error storing injury data in memory: {str(e)}")

    def _get_fallback_injury_data(self, home_team: str = None, away_team: str = None) -> Dict[str, Any]:
        """
        Get fallback injury data when Firecrawl is not available.
        
        Args:
            home_team: Optional home team name
            away_team: Optional away team name
            
        Returns:
            Dictionary containing basic injury data
        """
        # First try to retrieve from memory if recently fetched
        try:
            recent_reports = self.memory.search({
                "query": "recent NBA injury reports",
                "metadata_filter": {
                    "type": "injury_report"
                },
                "limit": 1
            })
            
            if recent_reports and len(recent_reports) > 0:
                report = recent_reports[0]
                metadata = report.get("metadata", {})
                
                # Check if report is recent (last 24 hours)
                timestamp = metadata.get("timestamp")
                if timestamp:
                    report_time = datetime.fromisoformat(timestamp)
                    if (datetime.now() - report_time).total_seconds() < 86400:  # 24 hours
                        injury_data = metadata.get("data", {})
                        
                        # Filter for specific teams if requested
                        if home_team or away_team:
                            filtered_data = {}
                            
                            if home_team:
                                for team_name, team_data in injury_data.items():
                                    if home_team.lower() in team_name.lower():
                                        filtered_data[team_name] = team_data
                                        
                            if away_team:
                                for team_name, team_data in injury_data.items():
                                    if away_team.lower() in team_name.lower():
                                        filtered_data[team_name] = team_data
                                        
                            return filtered_data
                        
                        return injury_data
        
        except Exception as e:
            self.logger.error(f"Error retrieving injury data from memory: {str(e)}")
        
        # If we couldn't get anything from memory, return placeholder data
        placeholder_data = {}
        
        if home_team:
            placeholder_data[home_team] = [
                {
                    "name": "Generic Player",
                    "status": "Unknown",
                    "injury": "No recent data available",
                    "details": "Fallback injury data - could not fetch current information",
                    "return_date": None
                }
            ]
            
        if away_team:
            placeholder_data[away_team] = [
                {
                    "name": "Generic Player",
                    "status": "Unknown",
                    "injury": "No recent data available",
                    "details": "Fallback injury data - could not fetch current information",
                    "return_date": None
                }
            ]
        
        return placeholder_data
    
    def fetch_team_stats(self, home_team: str, away_team: str) -> Dict[str, Any]:
        """Fetch team statistics for both teams"""
        self.logger.info(f"Fetching team stats for {away_team} @ {home_team}")
        
        # Placeholder - would fetch from sports data API
        return {
            "home_team_stats": {
                "wins": 15,
                "losses": 10,
                "points_per_game": 110.5,
                "rebounds_per_game": 42.3,
                "assists_per_game": 25.1
            },
            "away_team_stats": {
                "wins": 12,
                "losses": 13,
                "points_per_game": 108.2,
                "rebounds_per_game": 44.1,
                "assists_per_game": 23.8
            }
        }
    
    def fetch_recent_news(self, home_team: str, away_team: str) -> List[Dict[str, Any]]:
        """Fetch recent news for both teams"""
        self.logger.info(f"Fetching recent news for {away_team} @ {home_team}")
        
        # Placeholder - would use a news API or web scraping
        return [
            {
                "headline": f"{home_team} star player returns to practice",
                "content": "...",
                "source": "ESPN",
                "timestamp": "2023-05-01T15:30:00"
            },
            {
                "headline": f"{away_team} coach discusses strategy for upcoming game",
                "content": "...",
                "source": "NBA.com",
                "timestamp": "2023-05-01T12:15:00"
            }
        ]
    
    def track_line_movements(self, game_id: str) -> List[Dict[str, Any]]:
        """
        Track line movements for the specified game.
        
        Args:
            game_id: Unique identifier for the game
            
        Returns:
            List of line movement dictionaries
        """
        self.logger.info(f"Tracking line movements for game {game_id}")
        
        try:
            # Initialize the Betstamp client
            betstamp_client = BetstampClient(
                api_key=self.config.get("betstamp", {}).get("api_key"),
                base_url=self.config.get("betstamp", {}).get("base_url")
            )
            
            # Get markets for this specific game
            markets = betstamp_client.get_markets(
                league="NBA",
                book_ids=self.config.get("betstamp", {}).get("book_ids", [200, 999]),
                bet_types=self.config.get("betstamp", {}).get("bet_types", ["moneyline", "spread", "total"]),
                periods=self.config.get("betstamp", {}).get("periods", ["FT"]),
                fixture_id=game_id
            )
            
            if not markets:
                self.logger.warning(f"No markets found for game {game_id}")
                return self._get_placeholder_line_movements()
            
            # Process the markets into line movements
            line_movements = []
            current_time = datetime.now().isoformat()
            
            # Group markets by book and bet type
            for book_id in [200, 999]:  # DraftKings and True Line
                book_name = "DraftKings" if book_id == 200 else "True Line"
                
                # Process moneyline
                home_ml = next((m for m in markets if m.get("bet_type") == "moneyline" and 
                               m.get("side") == "home" and m.get("odd_provider_id") == book_id), None)
                away_ml = next((m for m in markets if m.get("bet_type") == "moneyline" and 
                               m.get("side") == "away" and m.get("odd_provider_id") == book_id), None)
                
                if home_ml and away_ml:
                    line_movements.append({
                        "timestamp": current_time,
                        "book": book_name,
                        "home_team_odds": home_ml.get("odds"),
                        "away_team_odds": away_ml.get("odds"),
                        "bet_type": "moneyline"
                    })
                
                # Process spread
                home_spread = next((m for m in markets if m.get("bet_type") == "spread" and 
                                  m.get("side_type") == "home" and m.get("odd_provider_id") == book_id), None)
                away_spread = next((m for m in markets if m.get("bet_type") == "spread" and 
                                  m.get("side_type") == "away" and m.get("odd_provider_id") == book_id), None)
                
                if home_spread and away_spread:
                    line_movements.append({
                        "timestamp": current_time,
                        "book": book_name,
                        "home_team_spread": home_spread.get("number"),
                        "home_team_odds": home_spread.get("odds"),
                        "away_team_spread": away_spread.get("number"),
                        "away_team_odds": away_spread.get("odds"),
                        "bet_type": "spread"
                    })
                
                # Process total
                over_total = next((m for m in markets if m.get("bet_type") == "total" and 
                                 m.get("side_type") == "over" and m.get("odd_provider_id") == book_id), None)
                under_total = next((m for m in markets if m.get("bet_type") == "total" and 
                                  m.get("side_type") == "under" and m.get("odd_provider_id") == book_id), None)
                
                if over_total and under_total:
                    line_movements.append({
                        "timestamp": current_time,
                        "book": book_name,
                        "total": over_total.get("number"),
                        "over_odds": over_total.get("odds"),
                        "under_odds": under_total.get("odds"),
                        "bet_type": "total"
                    })
            
            if not line_movements:
                self.logger.warning(f"No line movements processed for game {game_id}")
                return self._get_placeholder_line_movements()
                
            return line_movements
            
        except Exception as e:
            self.logger.error(f"Error tracking line movements for game {game_id}: {str(e)}")
            return self._get_placeholder_line_movements()
    
    def _get_placeholder_line_movements(self) -> List[Dict[str, Any]]:
        """Get placeholder line movements when actual data is unavailable"""
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "book": "Placeholder",
                "home_team_odds": -110,
                "away_team_odds": -110,
                "bet_type": "moneyline"
            }
        ]
        
    def _fetch_upcoming_games(self) -> List[Dict[str, Any]]:
        """Fetch upcoming NBA games from Betstamp API"""
        self.logger.info("Fetching upcoming NBA games from Betstamp")
        
        try:
            # Initialize the Betstamp client
            betstamp_client = BetstampClient(
                api_key=self.config.get("betstamp", {}).get("api_key"),
                base_url=self.config.get("betstamp", {}).get("base_url")
            )
            
            # Get fixtures (games) from Betstamp
            fixtures = betstamp_client.get_fixtures(league="NBA")
            
            # Get teams for reference
            teams = betstamp_client.get_teams(league="NBA")
            
            # Convert to our internal format
            upcoming_games = []
            
            for fixture_id, fixture in fixtures.items():
                home_team = fixture.get("home_team")
                away_team = fixture.get("away_team")
                
                # Only include games that haven't started yet
                status = fixture.get("status", "").lower()
                if status not in ["final", "in progress", "cancelled"]:
                    game_date = fixture.get("date")
                    
                    upcoming_games.append({
                        "game_id": fixture_id,
                        "home_team": home_team,
                        "away_team": away_team,
                        "game_date": game_date,
                        "source": "betstamp"
                    })
            
            self.logger.info(f"Found {len(upcoming_games)} upcoming NBA games")
            return upcoming_games
            
        except Exception as e:
            self.logger.error(f"Error fetching upcoming games from Betstamp: {str(e)}")
            
            # Fallback to placeholder data if API fails
            self.logger.info("Using placeholder data for upcoming games")
            return [
                {
                    "game_id": "placeholder_1",
                    "home_team": "Golden State Warriors",
                    "away_team": "Los Angeles Lakers",
                    "game_date": datetime.now().isoformat(),
                    "source": "placeholder"
                },
                {
                    "game_id": "placeholder_2",
                    "home_team": "Philadelphia 76ers",
                    "away_team": "Boston Celtics",
                    "game_date": datetime.now().isoformat(),
                    "source": "placeholder"
                }
            ]
    
    # Legacy method for backward compatibility
    def run(self):
        """
        Run the research module (legacy method).
        
        Returns:
            Dictionary containing research results
        """
        self.logger.info("Running research module (legacy method)")
        
        # Initialize research queue if not already done
        if not self.memory.get_context("pending_games"):
            self.initialize_research_queue()
        
        # Execute research tasks
        results = self.execute_research_tasks()
        
        # Format results for backward compatibility
        legacy_results = {
            "team_stats": next((r for r in results if r.get("team_stats")), {}),
            "player_stats": next((r for r in results if r.get("recent_news")), {}),
            "injury_reports": next((r for r in results if r.get("injury_data")), {}),
            "betting_odds": next((r for r in results if r.get("odds_data")), {})
        }
        
        return legacy_results
        
    def fetch_nba_odds(self) -> Dict[str, Any]:
        """Fetch NBA odds from Betstamp"""
        self.logger.info("Fetching NBA odds from Betstamp")
        
        try:
            # Initialize the Betstamp client
            betstamp_client = BetstampClient(
                api_key=self.config.get("betstamp", {}).get("api_key"),
                base_url=self.config.get("betstamp", {}).get("base_url")
            )
            
            # Get fixtures (games)
            fixtures_data = betstamp_client.get_fixtures(league="NBA")
            fixtures = fixtures_data
            
            # Get teams for reference
            teams_data = betstamp_client.get_teams(league="NBA")
            teams = teams_data
            
            # Process each fixture to get markets
            organized_odds = {}
            
            for fixture_id, fixture_data in fixtures.items():
                # Get odds for this specific fixture
                markets = betstamp_client.get_markets(
                    league="NBA",
                    book_ids=self.config.get("betstamp", {}).get("book_ids", [200, 999]),
                    bet_types=self.config.get("betstamp", {}).get("bet_types", ["moneyline", "spread", "total"]),
                    periods=self.config.get("betstamp", {}).get("periods", ["FT"]),
                    fixture_id=fixture_id
                )
                
                if markets:
                    # Create entry for this game
                    home_team = fixture_data.get("home_team")
                    away_team = fixture_data.get("away_team")
                    
                    organized_odds[fixture_id] = {
                        "game_id": fixture_id,
                        "home_team": home_team,
                        "away_team": away_team,
                        "date": fixture_data.get("date"),
                        "status": fixture_data.get("status"),
                        "markets": markets,
                        # Include the old format for backward compatibility
                        "odds": {
                            "moneyline": {
                                "home": {"dk": None, "true_line": None},
                                "away": {"dk": None, "true_line": None}
                            },
                            "spread": {
                                "home": {"dk": None, "true_line": None},
                                "away": {"dk": None, "true_line": None}
                            },
                            "total": {
                                "over": {"dk": None, "true_line": None},
                                "under": {"dk": None, "true_line": None}
                            }
                        }
                    }
                    
                    # Process markets for this fixture
                    for market in markets:
                        bet_type = market.get("bet_type", "").lower()
                        side = market.get("side", "").lower()
                        side_type = market.get("side_type", "").lower()
                        odds = market.get("odds")
                        number = market.get("number")
                        book_id = str(market.get("odd_provider_id"))
                        
                        book_key = "dk" if book_id == "200" else "true_line" if book_id == "999" else None
                        
                        if not book_key:
                            continue
                            
                        if bet_type == "moneyline":
                            if side in ["home", "away"]:
                                organized_odds[fixture_id]["odds"]["moneyline"][side][book_key] = odds
                        elif bet_type == "spread":
                            if side_type in ["home", "away"]:
                                organized_odds[fixture_id]["odds"]["spread"][side_type][book_key] = {
                                    "odds": odds,
                                    "points": number
                                }
                        elif bet_type == "total":
                            if side_type in ["over", "under"]:
                                organized_odds[fixture_id]["odds"]["total"][side_type][book_key] = {
                                    "odds": odds,
                                    "points": number
                                }
            
            # Store in memory
            self.memory.add({
                "content": f"Fetched NBA odds for {len(organized_odds)} games",
                "metadata": {
                    "type": "odds_data",
                    "source": "Betstamp",
                    "timestamp": datetime.now().isoformat(),
                    "games_count": len(organized_odds)
                }
            })
            
            self.logger.info(f"Fetched odds data for {len(organized_odds)} games")
            return organized_odds
            
        except Exception as e:
            self.logger.error(f"Error fetching NBA odds: {str(e)}")
            return {}
    
    def _convert_betstamp_to_line_movements(self, game_odds: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert Betstamp odds data to line movements format.
        
        Args:
            game_odds: Dictionary containing game odds from Betstamp
            
        Returns:
            List of line movement dictionaries
        """
        line_movements = []
        current_time = datetime.now().isoformat()
        
        # If we have the new format with markets, process it
        if game_odds.get("markets") is not None:
            markets = game_odds.get("markets", [])
            
            # Process each market
            for market in markets:
                book_id = market.get("odd_provider_id")
                book_name = "DraftKings" if book_id == 200 else "True Line" if book_id == 999 else f"Book {book_id}"
                bet_type = market.get("bet_type", "").lower()
                side = market.get("side", "").lower()
                side_type = market.get("side_type", "").lower()
                odds = market.get("odds")
                number = market.get("number")
                
                if bet_type == "moneyline":
                    # Collect moneyline odds for home and away
                    if side == "home":
                        home_odds = odds
                        # Look for matching away odds
                        away_odds = next((m.get("odds") for m in markets 
                                         if m.get("bet_type") == "moneyline" and 
                                         m.get("side") == "away" and
                                         m.get("odd_provider_id") == book_id), None)
                        
                        if away_odds is not None:
                            line_movements.append({
                                "timestamp": current_time,
                                "book": book_name,
                                "home_team_odds": home_odds,
                                "away_team_odds": away_odds,
                                "bet_type": "moneyline"
                            })
                
                elif bet_type == "spread":
                    # Collect spread odds for home and away
                    if side_type == "home":
                        home_spread = number
                        home_odds = odds
                        # Look for matching away odds
                        away_market = next((m for m in markets 
                                          if m.get("bet_type") == "spread" and 
                                          m.get("side_type") == "away" and
                                          m.get("odd_provider_id") == book_id), None)
                        
                        if away_market is not None:
                            away_spread = away_market.get("number")
                            away_odds = away_market.get("odds")
                            
                            line_movements.append({
                                "timestamp": current_time,
                                "book": book_name,
                                "home_team_spread": home_spread,
                                "home_team_odds": home_odds,
                                "away_team_spread": away_spread,
                                "away_team_odds": away_odds,
                                "bet_type": "spread"
                            })
                
                elif bet_type == "total":
                    # Collect total odds for over and under
                    if side_type == "over":
                        over_odds = odds
                        total = number
                        # Look for matching under odds
                        under_market = next((m for m in markets 
                                           if m.get("bet_type") == "total" and 
                                           m.get("side_type") == "under" and
                                           m.get("odd_provider_id") == book_id), None)
                        
                        if under_market is not None:
                            under_odds = under_market.get("odds")
                            
                            line_movements.append({
                                "timestamp": current_time,
                                "book": book_name,
                                "total": total,
                                "over_odds": over_odds,
                                "under_odds": under_odds,
                                "bet_type": "total"
                            })
        
        # If we have the old format, use it directly
        else:
            # Add DraftKings moneyline odds if available
            if game_odds.get("odds", {}).get("moneyline", {}).get("home", {}).get("dk") is not None:
                line_movements.append({
                    "timestamp": current_time,
                    "book": "DraftKings",
                    "home_team_odds": game_odds["odds"]["moneyline"]["home"]["dk"],
                    "away_team_odds": game_odds["odds"]["moneyline"]["away"]["dk"],
                    "bet_type": "moneyline"
                })
            
            # Add True Line moneyline odds if available
            if game_odds.get("odds", {}).get("moneyline", {}).get("home", {}).get("true_line") is not None:
                line_movements.append({
                    "timestamp": current_time,
                    "book": "True Line",
                    "home_team_odds": game_odds["odds"]["moneyline"]["home"]["true_line"],
                    "away_team_odds": game_odds["odds"]["moneyline"]["away"]["true_line"],
                    "bet_type": "moneyline"
                })
            
            # Add DraftKings spread odds if available
            home_spread_dk = game_odds.get("odds", {}).get("spread", {}).get("home", {}).get("dk")
            away_spread_dk = game_odds.get("odds", {}).get("spread", {}).get("away", {}).get("dk")
            if home_spread_dk is not None and away_spread_dk is not None:
                line_movements.append({
                    "timestamp": current_time,
                    "book": "DraftKings",
                    "home_team_spread": home_spread_dk.get("points"),
                    "home_team_odds": home_spread_dk.get("odds"),
                    "away_team_spread": away_spread_dk.get("points"),
                    "away_team_odds": away_spread_dk.get("odds"),
                    "bet_type": "spread"
                })
            
            # Add True Line spread odds if available
            home_spread_tl = game_odds.get("odds", {}).get("spread", {}).get("home", {}).get("true_line")
            away_spread_tl = game_odds.get("odds", {}).get("spread", {}).get("away", {}).get("true_line")
            if home_spread_tl is not None and away_spread_tl is not None:
                line_movements.append({
                    "timestamp": current_time,
                    "book": "True Line",
                    "home_team_spread": home_spread_tl.get("points"),
                    "home_team_odds": home_spread_tl.get("odds"),
                    "away_team_spread": away_spread_tl.get("points"),
                    "away_team_odds": away_spread_tl.get("odds"),
                    "bet_type": "spread"
                })
            
            # Add DraftKings total odds if available
            over_dk = game_odds.get("odds", {}).get("total", {}).get("over", {}).get("dk")
            under_dk = game_odds.get("odds", {}).get("total", {}).get("under", {}).get("dk")
            if over_dk is not None and under_dk is not None:
                line_movements.append({
                    "timestamp": current_time,
                    "book": "DraftKings",
                    "total": over_dk.get("points"),
                    "over_odds": over_dk.get("odds"),
                    "under_odds": under_dk.get("odds"),
                    "bet_type": "total"
                })
            
            # Add True Line total odds if available
            over_tl = game_odds.get("odds", {}).get("total", {}).get("over", {}).get("true_line")
            under_tl = game_odds.get("odds", {}).get("total", {}).get("under", {}).get("true_line")
            if over_tl is not None and under_tl is not None:
                line_movements.append({
                    "timestamp": current_time,
                    "book": "True Line",
                    "total": over_tl.get("points"),
                    "over_odds": over_tl.get("odds"),
                    "under_odds": under_tl.get("odds"),
                    "bet_type": "total"
                })
        
        return line_movements 