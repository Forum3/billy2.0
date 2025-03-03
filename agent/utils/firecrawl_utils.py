import json
import logging
import time
from typing import Dict, List, Any, Optional
from firecrawl import FirecrawlApp
import anthropic

logger = logging.getLogger(__name__)

class FirecrawlUtils:
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the injury report crawler.
        
        Args:
            config: Configuration dictionary containing API keys and settings
        """
        self.config = config
        self.firecrawl_config = config.get('firecrawl', {})
        self.firecrawl_api_key = self.firecrawl_config.get('api_key')
        
        # Initialize Firecrawl client
        if not self.firecrawl_api_key:
            logger.warning("Firecrawl API key not provided, injury report crawling will be disabled")
            self.client = None
        else:
            self.client = FirecrawlApp(api_key=self.firecrawl_api_key)
            logger.info("Firecrawl client initialized successfully")
        
        # Initialize Anthropic client for content parsing if available
        self.claude_api_key = config.get('anthropic', {}).get('api_key')
        if self.claude_api_key:
            self.claude_client = anthropic.Anthropic(api_key=self.claude_api_key)
            logger.info("Anthropic client initialized for enhanced content parsing")
        else:
            self.claude_client = None
            logger.warning("Anthropic API key not provided, using basic parsing for injury reports")
        
        # Default injury report sources
        self.injury_sources = self.firecrawl_config.get('injury_sources', [
            "https://www.rotowire.com/basketball/nba-injuries.php",
            "https://www.cbssports.com/nba/injuries/",
            "https://www.espn.com/nba/injuries"
        ])

    def fetch_injury_reports(self) -> Dict[str, Any]:
        """
        Fetch and parse NBA injury reports from configured sources.
        
        Returns:
            Dictionary containing structured injury data by team
        """
        if not self.client:
            logger.error("Firecrawl client not initialized, cannot fetch injury reports")
            return {}
        
        try:
            logger.info(f"Fetching injury reports from {len(self.injury_sources)} sources")
            injury_data = {}
            
            for source in self.injury_sources:
                try:
                    # Get the base domain for logging
                    domain = source.split('//')[1].split('/')[0]
                    logger.info(f"Fetching injury data from {domain}")
                    
                    # Scrape the page
                    scrape_result = self.client.scrape_url(source, params={'formats': ['markdown']})
                    
                    if not scrape_result or 'markdown' not in scrape_result:
                        logger.warning(f"No valid data returned from {domain}")
                        continue
                    
                    # Parse the scraped content
                    parsed_data = self._parse_injury_data(scrape_result['markdown'], source)
                    
                    # Merge with existing data
                    for team, players in parsed_data.items():
                        if team not in injury_data:
                            injury_data[team] = []
                        
                        # Add source information and merge
                        for player in players:
                            player['source'] = domain
                            
                            # Check if player already exists in the data
                            existing_entries = [p for p in injury_data[team] if p['name'] == player['name']]
                            if not existing_entries:
                                injury_data[team].append(player)
                            else:
                                # Update with newer information if applicable
                                for existing in existing_entries:
                                    # Only update if this source has more detail or is more recent
                                    if len(player.get('details', '')) > len(existing.get('details', '')):
                                        existing.update(player)
                        
                    logger.info(f"Successfully parsed injury data from {domain}")
                    
                    # Small delay to avoid overloading the API
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error fetching injury data from {source}: {str(e)}")
                    continue
            
            logger.info(f"Completed injury report collection: found data for {len(injury_data)} teams")
            return injury_data
            
        except Exception as e:
            logger.error(f"Error in fetch_injury_reports: {str(e)}")
            return {}
    
    def _parse_injury_data(self, content: str, source: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse injury report content into structured data.
        
        Args:
            content: Markdown content from scraped page
            source: URL of the source website
            
        Returns:
            Dictionary with team names as keys and lists of player injury data as values
        """
        # Use Claude if available, otherwise use basic parsing
        if self.claude_client:
            return self._parse_with_claude(content, source)
        else:
            return self._basic_parse(content, source)
    
    def _parse_with_claude(self, content: str, source: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse injury report content using Claude for enhanced understanding.
        
        Args:
            content: Markdown content from scraped page
            source: URL of the source website
            
        Returns:
            Dictionary with team names as keys and lists of player injury data as values
        """
        try:
            # Create a prompt for Claude to parse the injury data
            prompt = f"""
            Parse the following NBA injury report content into a structured JSON format.
            Extract and categorize injuries by team, including player names, injury details, status, and expected return dates when available.
            
            The JSON should have team names as keys (use full team names, not abbreviations), with each team having an array of player objects.
            Each player object should contain:
            - name: player's full name
            - status: injury status (e.g., Out, Questionable, Day-to-Day)
            - injury: type of injury
            - details: any additional details provided
            - return_date: expected return date if available, otherwise null
            
            Only include players who are actually injured or have a listed status - do not include healthy players.
            If you cannot determine certain fields, use null for those values.
            
            Source: {source}
            
            Content to parse:
            {content[:25000]}  # Limiting content to avoid token limits
            
            Respond with valid JSON only, without any explanation or markdown formatting.
            """
            
            # Call Claude to parse the content
            completion = self.claude_client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Get and clean the response
            response_text = completion.content[0].text.strip()
            
            # Clean up the response if it contains markdown formatting
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].strip()
            
            # Parse the JSON response
            parsed_data = json.loads(response_text)
            
            logger.info(f"Successfully parsed injury data with Claude: found data for {len(parsed_data)} teams")
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing with Claude: {str(e)}")
            # Fall back to basic parsing if Claude fails
            return self._basic_parse(content, source)
    
    def _basic_parse(self, content: str, source: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Basic parsing of injury report content without using Claude.
        
        Args:
            content: Markdown content from scraped page
            source: URL of the source website
            
        Returns:
            Dictionary with team names as keys and lists of player injury data as values
        """
        # This is a fallback parser that uses basic string matching
        # It's not as accurate as Claude but can work as a backup
        
        result = {}
        
        try:
            # Simple detection of patterns for different sources
            if "rotowire.com" in source:
                return self._parse_rotowire(content)
            elif "cbssports.com" in source:
                return self._parse_cbssports(content)
            elif "espn.com" in source:
                return self._parse_espn(content)
            else:
                logger.warning(f"No specific parser available for {source}, using generic parser")
                return self._parse_generic(content)
                
        except Exception as e:
            logger.error(f"Error in basic parsing: {str(e)}")
            return {}
    
    def _parse_rotowire(self, content: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse Rotowire injury format"""
        # Simplified implementation
        result = {}
        
        # Split content by team sections
        team_sections = content.split("## ")
        
        for section in team_sections:
            if not section.strip():
                continue
                
            lines = section.strip().split("\n")
            if not lines:
                continue
                
            team_name = lines[0].strip()
            if not team_name or team_name.lower() == "player":
                continue
                
            result[team_name] = []
            
            for i in range(1, len(lines)):
                line = lines[i].strip()
                if not line or line.startswith('|') or line.startswith('Player'):
                    continue
                    
                parts = line.split('|')
                if len(parts) >= 3:
                    player_name = parts[0].strip()
                    injury_status = parts[1].strip() if len(parts) > 1 else ""
                    injury_type = parts[2].strip() if len(parts) > 2 else ""
                    
                    result[team_name].append({
                        "name": player_name,
                        "status": injury_status,
                        "injury": injury_type,
                        "details": "",
                        "return_date": None
                    })
        
        return result
    
    def _parse_cbssports(self, content: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse CBS Sports injury format"""
        # Simplified implementation
        result = {}
        
        # CBS Sports typically organizes by team
        team_sections = content.split("###")
        
        for section in team_sections:
            if not section.strip():
                continue
                
            lines = section.strip().split("\n")
            if not lines:
                continue
                
            team_name = lines[0].strip()
            if not team_name or "injury" in team_name.lower():
                continue
                
            result[team_name] = []
            
            current_player = {}
            for line in lines[1:]:
                line = line.strip()
                
                if not line:
                    if current_player and 'name' in current_player:
                        result[team_name].append(current_player)
                        current_player = {}
                    continue
                
                if "**" in line:  # Player name is often in bold
                    if current_player and 'name' in current_player:
                        result[team_name].append(current_player)
                    
                    player_name = line.replace("**", "").strip()
                    current_player = {"name": player_name, "status": "", "injury": "", "details": "", "return_date": None}
                    
                elif "Status:" in line:
                    current_player["status"] = line.replace("Status:", "").strip()
                    
                elif "Injury:" in line:
                    current_player["injury"] = line.replace("Injury:", "").strip()
                    
                elif "Expected Return:" in line:
                    current_player["return_date"] = line.replace("Expected Return:", "").strip()
                    
                elif current_player:  # Additional details
                    if "details" in current_player:
                        current_player["details"] += " " + line
                    else:
                        current_player["details"] = line
                        
            # Add the last player if any
            if current_player and 'name' in current_player:
                result[team_name].append(current_player)
        
        return result

    def _parse_espn(self, content: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse ESPN injury format"""
        # Simplified implementation
        result = {}
        
        # ESPN often has a table format
        if "NAME" in content and "STATUS" in content:
            lines = content.strip().split("\n")
            team_name = None
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    continue
                    
                if "TEAM" in line:
                    continue  # Header line
                    
                if line.isupper() and "NAME" not in line and "STATUS" not in line:
                    team_name = line.title()  # Team names are often in all caps
                    result[team_name] = []
                    continue
                    
                if team_name and "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        player_name = parts[0].strip()
                        position = parts[1].strip() if len(parts) > 1 else ""
                        status = parts[2].strip() if len(parts) > 2 else ""
                        injury = parts[3].strip() if len(parts) > 3 else ""
                        
                        if player_name and status:
                            result[team_name].append({
                                "name": player_name,
                                "status": status,
                                "injury": injury,
                                "details": f"Position: {position}" if position else "",
                                "return_date": None
                            })
        
        return result
    
    def _parse_generic(self, content: str) -> Dict[str, List[Dict[str, Any]]]:
        """Generic parser for unknown formats"""
        # Very basic implementation that tries to identify team and player patterns
        result = {}
        current_team = "Unknown Team"
        result[current_team] = []
        
        # List of NBA team names to recognize
        nba_teams = [
            "Atlanta Hawks", "Boston Celtics", "Brooklyn Nets", "Charlotte Hornets",
            "Chicago Bulls", "Cleveland Cavaliers", "Dallas Mavericks", "Denver Nuggets",
            "Detroit Pistons", "Golden State Warriors", "Houston Rockets", "Indiana Pacers",
            "Los Angeles Clippers", "Los Angeles Lakers", "Memphis Grizzlies", "Miami Heat",
            "Milwaukee Bucks", "Minnesota Timberwolves", "New Orleans Pelicans", "New York Knicks",
            "Oklahoma City Thunder", "Orlando Magic", "Philadelphia 76ers", "Phoenix Suns",
            "Portland Trail Blazers", "Sacramento Kings", "San Antonio Spurs", "Toronto Raptors",
            "Utah Jazz", "Washington Wizards"
        ]
        
        # Keywords that likely indicate injury status
        status_keywords = ["out", "questionable", "doubtful", "day-to-day", "probable", "injured"]
        
        lines = content.strip().split("\n")
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
                
            # Check if line contains a team name
            for team in nba_teams:
                if team.lower() in line.lower():
                    current_team = team
                    if current_team not in result:
                        result[current_team] = []
                    break
                    
            # Check if line might contain player and injury info
            has_status_keyword = any(keyword in line.lower() for keyword in status_keywords)
            
            if has_status_keyword and len(line.split()) >= 3:
                # Simple heuristic: first part is player name, look for status keywords
                parts = line.split()
                player_name = ""
                status = ""
                injury = ""
                
                # Try to identify the player name (usually at the beginning)
                name_end = min(3, len(parts))
                player_name = " ".join(parts[:name_end])
                
                # Look for status keywords
                for i, word in enumerate(parts):
                    if any(keyword in word.lower() for keyword in status_keywords):
                        status = word
                        # Assume injury type might follow the status
                        if i < len(parts) - 1:
                            injury = " ".join(parts[i+1:])
                        break
                
                if player_name and (status or injury):
                    result[current_team].append({
                        "name": player_name,
                        "status": status,
                        "injury": injury,
                        "details": line,  # Store the full line as details for reference
                        "return_date": None
                    })
        
        # Remove empty teams
        result = {team: players for team, players in result.items() if players}
        
        return result

    def fetch_player_injury_details(self, player_name: str, team_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch detailed injury information for a specific player.
        
        Args:
            player_name: Name of the player to search for
            team_name: Optional team name to narrow search
            
        Returns:
            Dictionary containing detailed injury information for the player
        """
        if not self.client:
            logger.error("Firecrawl client not initialized, cannot fetch player details")
            return {}
        
        try:
            # Create a search query
            search_query = f"{player_name} injury nba"
            if team_name:
                search_query = f"{player_name} {team_name} injury nba"
            
            logger.info(f"Searching for detailed injury information on {player_name}")
            
            # Use Firecrawl to search for player injury information
            search_urls = [
                f"https://www.google.com/search?q={search_query.replace(' ', '+')}",
                f"https://www.bing.com/search?q={search_query.replace(' ', '+')}"
            ]
            
            results = []
            
            for search_url in search_urls:
                try:
                    # Map the search results
                    map_result = self.client.map_url(search_url)
                    
                    # Get the top 3 relevant links
                    relevant_links = []
                    if isinstance(map_result, dict) and 'urls' in map_result:
                        relevant_links = map_result['urls'][:3]
                    elif isinstance(map_result, list):
                        relevant_links = map_result[:3]
                    
                    # Scrape each relevant link
                    for link in relevant_links:
                        scrape_result = self.client.scrape_url(link, params={'formats': ['markdown']})
                        if scrape_result and 'markdown' in scrape_result:
                            results.append({
                                "source": link,
                                "content": scrape_result['markdown']
                            })
                    
                except Exception as e:
                    logger.error(f"Error searching {search_url}: {str(e)}")
                    continue
            
            # Parse the results with Claude if available
            if results and self.claude_client:
                return self._extract_player_injury_details(player_name, team_name, results)
            else:
                logger.warning(f"No detailed information found for {player_name}")
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching player injury details: {str(e)}")
            return {}
    
    def _extract_player_injury_details(self, player_name: str, team_name: Optional[str], 
                                      results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract detailed player injury information using Claude.
        
        Args:
            player_name: Name of the player
            team_name: Optional team name
            results: List of scraped content
            
        Returns:
            Dictionary containing detailed injury information
        """
        try:
            # Combine scraped content (limiting to avoid token limits)
            combined_content = "\n\n".join(
                f"Source: {r['source']}\n{r['content'][:5000]}" for r in results
            )
            
            # Create a prompt for Claude
            prompt = f"""
            Analyze the following information about NBA player {player_name}'s injury.
            
            Extract and synthesize the most accurate and up-to-date information about:
            1. The specific injury
            2. When it occurred
            3. Current status (Out, Questionable, Day-to-Day, etc.)
            4. Expected return timeline
            5. How it might impact their performance
            6. Any relevant team context or lineup changes resulting from this injury
            
            Scraped content:
            {combined_content}
            
            Respond with a JSON object containing these fields:
            - player_name: Full name of the player
            - team: Team name if available
            - injury_type: Specific injury description
            - date_occurred: When the injury happened (if known)
            - current_status: Current injury status 
            - expected_return: Expected return timeline
            - performance_impact: Likely impact on performance
            - lineup_changes: How the team is adjusting
            - sources: List of sources used
            - last_updated: Current timestamp
            
            Only include information that is explicitly mentioned in the sources. If information about any field is not available, use null for that field.
            Respond with valid JSON only, without any explanation or markdown formatting.
            """
            
            # Call Claude to analyze the content
            completion = self.claude_client.messages.create(
                model="claude-3-7-sonnet-20250219",
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Get and clean the response
            response_text = completion.content[0].text.strip()
            
            # Clean up the response if it contains markdown formatting
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].strip()
            
            # Parse the JSON response
            parsed_data = json.loads(response_text)
            
            logger.info(f"Successfully extracted detailed injury information for {player_name}")
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error extracting player injury details: {str(e)}")
            return {
                "player_name": player_name,
                "team": team_name,
                "injury_type": None,
                "current_status": None,
                "error": f"Failed to extract details: {str(e)}"
            } 