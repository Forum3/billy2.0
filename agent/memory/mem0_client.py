#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mem0 memory client for the NBA Betting Agent.

This module provides a client for interacting with the Mem0 memory system,
which is used to store and retrieve information for the agent.
"""

import logging
import requests
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Mem0Client:
    """
    Client for interacting with the Mem0 memory system.
    
    This class provides methods for storing and retrieving information
    from the Mem0 memory system, which is used by the NBA Betting Agent.
    This custom implementation matches the API of the official Mem0 client
    for consistent integration.
    """
    
    def __init__(self, api_key: str, agent_id: str, base_url: str = "https://api.mem0.ai", cache_ttl: int = 300):
        """
        Initialize the Mem0 memory client.
        
        Args:
            api_key: API key for authenticating with Mem0
            agent_id: Identifier for the agent in Mem0 (used as user_id)
            base_url: Base URL for the Mem0 API
            cache_ttl: Time-to-live for cached items in seconds (default: 300)
        """
        self.api_key = api_key
        self.agent_id = agent_id  # We'll use this as user_id for compatibility
        self.base_url = base_url
        
        # Update headers to match what the official client uses
        self.headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json",
            "Mem0-User-ID": self.agent_id  # Add user ID header
        }
        
        # Initialize cache
        self.cache = {}
        self.cache_ttl = cache_ttl
        
        logger.info(f"Mem0 client initialized for agent {agent_id}")
    
    def _add_to_cache(self, key: str, data: Any) -> None:
        """
        Add an item to the cache.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """
        Get an item from the cache if it exists and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data if available and not expired, None otherwise
        """
        if key in self.cache and time.time() - self.cache[key]['timestamp'] < self.cache_ttl:
            logger.debug(f"Cache hit for key: {key}")
            return self.cache[key]['data']
        return None
    
    def _invalidate_cache(self, key: Optional[str] = None) -> None:
        """
        Invalidate cache entries.
        
        Args:
            key: Specific cache key to invalidate, or None to invalidate all
        """
        if key is None:
            self.cache = {}
            logger.debug("Cache completely invalidated")
        elif key in self.cache:
            del self.cache[key]
            logger.debug(f"Cache invalidated for key: {key}")
    
    def add(self, memory_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a memory item to Mem0.
        
        Args:
            memory_item: Dictionary containing the memory item to add
                Must include 'content' and optional 'metadata'
                
        Returns:
            Dictionary containing the added memory item with its ID
        """
        try:
            # Use the correct endpoint for the official Mem0 API
            url = f"{self.base_url}/v1/memories/"
            
            # Ensure memory item has required fields
            if "content" not in memory_item:
                raise ValueError("Memory item must include 'content'")
            
            # Format content as messages for compatibility with official client
            content = memory_item["content"]
            if isinstance(content, str):
                # Convert string content to messages format
                messages = [
                    {"role": "user", "content": content}
                ]
                memory_item["messages"] = messages
            
            # Add metadata if not present
            if "metadata" not in memory_item:
                memory_item["metadata"] = {}
            
            # Add priority if not present
            if "priority" not in memory_item["metadata"]:
                memory_item["metadata"]["priority"] = 5  # Default priority (1-10)
            else:
                # Ensure priority is within valid range
                priority = memory_item["metadata"]["priority"]
                if not isinstance(priority, int) or priority < 1 or priority > 10:
                    logger.warning(f"Invalid priority value: {priority}. Using default priority 5.")
                    memory_item["metadata"]["priority"] = 5
            
            # Add user_id for compatibility with official client
            memory_item["user_id"] = self.agent_id
            
            response = requests.post(url, headers=self.headers, json=memory_item)
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Added memory item: {result}")
            
            # Handle the response format which might be a list
            memory_id = None
            if isinstance(result, list) and len(result) > 0:
                memory_id = result[0].get('id') if isinstance(result[0], dict) else None
            elif isinstance(result, dict):
                memory_id = result.get('id')
            
            # Format response to match official client
            response_data = {
                "id": memory_id,
                "content": memory_item.get("content", ""),
                "metadata": memory_item.get("metadata", {})
            }
            
            # Invalidate cache for search results since we've added new data
            self._invalidate_cache("search")
            
            # Cache the new memory item if it has an ID
            if memory_id:
                self._add_to_cache(f"memory:{memory_id}", response_data)
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error adding memory item: {str(e)}")
            # Return a minimal result with error information
            return {
                "id": None,
                "error": str(e),
                "content": memory_item.get("content", ""),
                "metadata": memory_item.get("metadata", {})
            }
    
    def search(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for memory items in Mem0.
        
        Args:
            search_params: Dictionary containing search parameters
                May include 'query', 'metadata_filter', 'limit', etc.
                
        Returns:
            List of memory items matching the search criteria
        """
        try:
            # Handle priority-based search
            priority_min = search_params.pop("priority_min", None)
            priority_max = search_params.pop("priority_max", None)
            sort_by_priority = search_params.pop("sort_by_priority", False)
            
            # Create a copy of search_params for cache key generation
            cache_params = {}
            for key, value in search_params.items():
                if isinstance(value, dict):
                    # Convert dict to sorted tuple of items for hashability
                    cache_params[key] = tuple(sorted([(k, str(v)) for k, v in value.items()]))
                else:
                    cache_params[key] = value
            
            # Generate a cache key based on search parameters and priority settings
            cache_key = f"search:{hash(frozenset(cache_params.items()))}"
            if priority_min is not None:
                cache_key += f":pmin{priority_min}"
            if priority_max is not None:
                cache_key += f":pmax{priority_max}"
            if sort_by_priority:
                cache_key += ":sort_priority"
            
            # Check cache first
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Use the v1 endpoint since v2 is returning 400 Bad Request
            url = f"{self.base_url}/v1/memories/search/"
            
            # Set default limit if not provided
            if "limit" not in search_params:
                search_params["limit"] = 10
            
            # Ensure query is not blank (API requirement)
            if "query" not in search_params or not search_params["query"]:
                search_params["query"] = "*"  # Use wildcard for all items
            
            # Add user_id for compatibility with official client
            search_params["user_id"] = self.agent_id
            
            # Convert metadata_filter to filters for compatibility
            if "metadata_filter" in search_params:
                search_params["filters"] = search_params.pop("metadata_filter")
            
            # Add priority filters if specified
            if priority_min is not None or priority_max is not None:
                if "filters" not in search_params:
                    search_params["filters"] = {}
                
                priority_filter = {}
                if priority_min is not None:
                    priority_filter["gte"] = priority_min
                if priority_max is not None:
                    priority_filter["lte"] = priority_max
                
                search_params["filters"]["priority"] = priority_filter
            
            response = requests.post(url, headers=self.headers, json=search_params)
            response.raise_for_status()
            
            result = response.json()
            
            # Handle different response formats
            # The API might return a list directly or a dict with a "memories" key
            if isinstance(result, list):
                memories = result
            else:
                memories = result.get("memories", [])
                
            logger.debug(f"Found {len(memories)} memory items")
            
            # Sort by priority if requested
            if sort_by_priority and memories:
                memories.sort(
                    key=lambda x: x.get("metadata", {}).get("priority", 5),
                    reverse=True  # Higher priority first
                )
            
            # Cache the search results
            self._add_to_cache(cache_key, memories)
            
            # Also cache individual memory items
            for memory in memories:
                if "id" in memory:
                    self._add_to_cache(f"memory:{memory['id']}", memory)
            
            return memories
            
        except Exception as e:
            logger.error(f"Error searching memory: {str(e)}")
            return []
    
    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific memory item by ID.
        
        Args:
            memory_id: ID of the memory item to retrieve
            
        Returns:
            Dictionary containing the memory item, or None if not found
        """
        try:
            # Check cache first
            cache_key = f"memory:{memory_id}"
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Use the correct endpoint for the official Mem0 API
            url = f"{self.base_url}/v1/memories/{memory_id}/"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Retrieved memory item: {memory_id}")
            
            # Cache the result
            self._add_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting memory item {memory_id}: {str(e)}")
            return None
    
    def update(self, memory_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a specific memory item by ID.
        
        Args:
            memory_id: ID of the memory item to update
            updates: Dictionary containing the updates to apply
                May include 'content' and/or 'metadata'
                
        Returns:
            Dictionary containing the updated memory item, or None if failed
        """
        try:
            # Get the current memory item for versioning
            current = self.get(memory_id)
            if not current:
                logger.warning(f"Memory item not found for update: {memory_id}")
                return None
            
            # Add version information
            if 'metadata' not in updates:
                updates['metadata'] = {}
            
            # Get current version or default to 0
            current_version = current.get('metadata', {}).get('version', 0)
            
            # Update version information
            updates['metadata']['version'] = current_version + 1
            updates['metadata']['previous_version'] = current_version
            
            # Store previous content if content is being updated
            if 'content' in updates:
                updates['metadata']['previous_content'] = current.get('content', '')
                
                # Store timestamp of the update
                updates['metadata']['updated_at'] = datetime.now().isoformat()
            
            # Use the correct endpoint for the official Mem0 API
            url = f"{self.base_url}/v1/memories/{memory_id}/"
            
            # Format content as messages for compatibility with official client
            if "content" in updates and isinstance(updates["content"], str):
                updates["messages"] = [
                    {"role": "user", "content": updates["content"]}
                ]
            
            response = requests.patch(url, headers=self.headers, json=updates)
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"Updated memory item: {memory_id} (version {updates['metadata']['version']})")
            
            # Invalidate cache for this memory item and search results
            self._invalidate_cache(f"memory:{memory_id}")
            self._invalidate_cache("search")
            
            # Cache the updated result
            self._add_to_cache(f"memory:{memory_id}", result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error updating memory item {memory_id}: {str(e)}")
            return None
    
    def get_version(self, memory_id: str, version: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific version of a memory item.
        
        This method attempts to retrieve a specific version of a memory item.
        If the exact version is not available, it returns None.
        
        Args:
            memory_id: ID of the memory item to retrieve
            version: Version number to retrieve
            
        Returns:
            Dictionary containing the memory item at the specified version, or None if not found
        """
        try:
            # Get the current memory item
            current = self.get(memory_id)
            if not current:
                logger.warning(f"Memory item not found: {memory_id}")
                return None
            
            # Check if this is the requested version
            current_version = current.get('metadata', {}).get('version', 0)
            if current_version == version:
                return current
            
            # If we're looking for the previous version and it's stored in metadata
            if version == current_version - 1 and 'previous_content' in current.get('metadata', {}):
                # Create a version of the memory item with the previous content
                previous = current.copy()
                previous['content'] = current['metadata']['previous_content']
                previous['metadata'] = current['metadata'].copy()
                previous['metadata']['version'] = version
                
                # Remove previous_content from metadata to avoid confusion
                if 'previous_content' in previous['metadata']:
                    del previous['metadata']['previous_content']
                
                return previous
            
            # If we can't find the requested version
            logger.warning(f"Version {version} not found for memory item {memory_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting version {version} of memory item {memory_id}: {str(e)}")
            return None
    
    def list_versions(self, memory_id: str) -> List[int]:
        """
        List available versions of a memory item.
        
        Args:
            memory_id: ID of the memory item
            
        Returns:
            List of available version numbers, sorted from newest to oldest
        """
        try:
            # Get the current memory item
            current = self.get(memory_id)
            if not current:
                logger.warning(f"Memory item not found: {memory_id}")
                return []
            
            # Get current version or default to 0
            current_version = current.get('metadata', {}).get('version', 0)
            
            # Create a list of versions
            versions = [current_version]
            
            # Add previous version if it exists
            if 'previous_version' in current.get('metadata', {}):
                versions.append(current['metadata']['previous_version'])
            
            return versions
            
        except Exception as e:
            logger.error(f"Error listing versions of memory item {memory_id}: {str(e)}")
            return []
    
    def rollback(self, memory_id: str, version: int) -> Optional[Dict[str, Any]]:
        """
        Roll back a memory item to a previous version.
        
        Args:
            memory_id: ID of the memory item to roll back
            version: Version number to roll back to
            
        Returns:
            Dictionary containing the rolled back memory item, or None if failed
        """
        try:
            # Get the specified version
            previous_version = self.get_version(memory_id, version)
            if not previous_version:
                logger.warning(f"Version {version} not found for memory item {memory_id}")
                return None
            
            # Create updates to roll back
            updates = {
                'content': previous_version['content'],
                'metadata': {
                    'rolled_back_from': previous_version.get('metadata', {}).get('version', 0),
                    'rolled_back_at': datetime.now().isoformat()
                }
            }
            
            # Update the memory item
            result = self.update(memory_id, updates)
            if result:
                logger.info(f"Rolled back memory item {memory_id} to version {version}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error rolling back memory item {memory_id} to version {version}: {str(e)}")
            return None
    
    def delete(self, memory_id: str) -> bool:
        """
        Delete a specific memory item by ID.
        
        Args:
            memory_id: ID of the memory item to delete
            
        Returns:
            Boolean indicating success or failure
        """
        try:
            # Use the correct endpoint for the official Mem0 API
            url = f"{self.base_url}/v1/memories/{memory_id}/"
            
            response = requests.delete(url, headers=self.headers)
            response.raise_for_status()
            
            logger.debug(f"Deleted memory item: {memory_id}")
            
            # Invalidate cache for this memory item and search results
            self._invalidate_cache(f"memory:{memory_id}")
            self._invalidate_cache("search")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting memory item {memory_id}: {str(e)}")
            return False
    
    def delete_all(self, user_id: str = None, memory_id: str = None) -> bool:
        """
        Delete all memory items for the agent or a specific memory.
        
        Args:
            user_id: Optional user ID to filter by (defaults to agent_id)
            memory_id: Optional memory ID to delete a specific memory
            
        Returns:
            Boolean indicating success or failure
        """
        try:
            # For compatibility with the official client
            if memory_id:
                return self.delete(memory_id)
            
            # Use the correct endpoint for the official Mem0 API
            url = f"{self.base_url}/v1/memories/"
            
            # Add user_id filter
            params = {"user_id": user_id or self.agent_id}
            
            response = requests.delete(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            logger.info(f"Cleared all memory items for agent {self.agent_id}")
            
            # Invalidate the entire cache
            self._invalidate_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing memory: {str(e)}")
            return False
    
    # Alias for clear() to match official client
    clear = delete_all
    
    def get_with_cache(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a memory item with caching (convenience method).
        
        This is equivalent to the get() method, which already uses caching,
        but is provided for explicit clarity when caching is desired.
        
        Args:
            memory_id: ID of the memory item to retrieve
            
        Returns:
            Dictionary containing the memory item, or None if not found
        """
        return self.get(memory_id)
    
    def search_with_cache(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search for memory items with caching (convenience method).
        
        This is equivalent to the search() method, which already uses caching,
        but is provided for explicit clarity when caching is desired.
        
        Args:
            search_params: Dictionary containing search parameters
                
        Returns:
            List of memory items matching the search criteria
        """
        return self.search(search_params)
    
    def add_batch(self, memory_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add multiple memory items in a single batch.
        
        This method optimizes performance by processing multiple memory items
        in a single method call, with proper error handling for each item.
        
        Args:
            memory_items: List of dictionaries containing memory items to add
                Each must include 'content' and optional 'metadata'
                
        Returns:
            List of dictionaries containing the added memory items with their IDs
        """
        if not memory_items:
            return []
            
        logger.info(f"Adding {len(memory_items)} memory items in batch")
        
        try:
            # Use the batch endpoint for the official Mem0 API
            url = f"{self.base_url}/v1/batch/"
            
            # Prepare batch request
            batch_request = []
            
            for item in memory_items:
                # Ensure memory item has required fields
                if "content" not in item:
                    raise ValueError("Memory item must include 'content'")
                
                # Format content as messages for compatibility with official client
                content = item["content"]
                if isinstance(content, str):
                    # Convert string content to messages format
                    messages = [
                        {"role": "user", "content": content}
                    ]
                    item["messages"] = messages
                
                # Add metadata if not present
                if "metadata" not in item:
                    item["metadata"] = {}
                
                # Add priority if not present
                if "priority" not in item["metadata"]:
                    item["metadata"]["priority"] = 5  # Default priority (1-10)
                else:
                    # Ensure priority is within valid range
                    priority = item["metadata"]["priority"]
                    if not isinstance(priority, int) or priority < 1 or priority > 10:
                        logger.warning(f"Invalid priority value: {priority}. Using default priority 5.")
                        item["metadata"]["priority"] = 5
                
                # Add user_id for compatibility with official client
                item["user_id"] = self.agent_id
                
                # Add to batch request
                batch_request.append({
                    "method": "POST",
                    "path": "/v1/memories/",
                    "body": item
                })
            
            # Send batch request
            response = requests.post(url, headers=self.headers, json=batch_request)
            response.raise_for_status()
            
            # Process batch response
            batch_response = response.json()
            results = []
            
            for i, resp in enumerate(batch_response):
                if resp.get("status_code", 200) >= 400:
                    # Handle error response
                    logger.error(f"Error adding memory item in batch: {resp.get('body', {}).get('detail', 'Unknown error')}")
                    results.append({
                        "id": None,
                        "error": resp.get("body", {}).get("detail", "Unknown error"),
                        "content": memory_items[i].get("content", ""),
                        "metadata": memory_items[i].get("metadata", {})
                    })
                else:
                    # Handle successful response
                    body = resp.get("body", {})
                    memory_id = body.get("id")
                    
                    result = {
                        "id": memory_id,
                        "content": memory_items[i].get("content", ""),
                        "metadata": memory_items[i].get("metadata", {})
                    }
                    
                    results.append(result)
                    
                    # Cache the new memory item if it has an ID
                    if memory_id:
                        self._add_to_cache(f"memory:{memory_id}", result)
            
            # Invalidate cache for search results since we've added new data
            self._invalidate_cache("search")
            
            logger.info(f"Added {len(results)} memory items in batch")
            return results
            
        except Exception as e:
            logger.error(f"Batch operation failed: {str(e)}")
            
            # Fall back to processing items individually
            logger.info("Falling back to processing items individually")
            results = []
            
            for item in memory_items:
                try:
                    result = self.add(item)
                    results.append(result)
                except Exception as item_e:
                    logger.error(f"Error adding memory item in batch: {str(item_e)}")
                    # Add a placeholder result with error information
                    results.append({
                        "id": None,
                        "error": str(item_e),
                        "content": item.get("content", ""),
                        "metadata": item.get("metadata", {})
                    })
            
            return results
    
    def update_batch(self, updates: List[Dict[str, Any]]) -> List[Optional[Dict[str, Any]]]:
        """
        Update multiple memory items in a single batch.
        
        This method optimizes performance by processing multiple updates
        in a single method call, with proper error handling for each update.
        
        Args:
            updates: List of dictionaries containing updates to apply
                Each must include 'id' and may include 'content' and/or 'metadata'
                
        Returns:
            List of dictionaries containing the updated memory items, or None for failed updates
        """
        if not updates:
            return []
            
        logger.info(f"Updating {len(updates)} memory items in batch")
        
        try:
            # Use the batch endpoint for the official Mem0 API
            url = f"{self.base_url}/v1/batch/"
            
            # Prepare batch request
            batch_request = []
            
            for update in updates:
                # Validate update
                if "id" not in update:
                    raise ValueError("Update must include 'id'")
                
                memory_id = update["id"]
                
                # Get the current memory item for versioning
                current = self.get(memory_id)
                if not current:
                    logger.warning(f"Memory item not found for update: {memory_id}")
                    continue
                
                # Add version information
                if 'metadata' not in update:
                    update['metadata'] = {}
                
                # Get current version or default to 0
                current_version = current.get('metadata', {}).get('version', 0)
                
                # Update version information
                update['metadata']['version'] = current_version + 1
                update['metadata']['previous_version'] = current_version
                
                # Store previous content if content is being updated
                if 'content' in update:
                    update['metadata']['previous_content'] = current.get('content', '')
                    
                    # Store timestamp of the update
                    update['metadata']['updated_at'] = datetime.now().isoformat()
                    
                    # Format content as messages for compatibility with official client
                    if isinstance(update["content"], str):
                        update["messages"] = [
                            {"role": "user", "content": update["content"]}
                        ]
                
                # Add to batch request
                batch_request.append({
                    "method": "PATCH",
                    "path": f"/v1/memories/{memory_id}/",
                    "body": update
                })
            
            # Send batch request
            response = requests.post(url, headers=self.headers, json=batch_request)
            response.raise_for_status()
            
            # Process batch response
            batch_response = response.json()
            results = []
            
            for i, resp in enumerate(batch_response):
                if resp.get("status_code", 200) >= 400:
                    # Handle error response
                    logger.error(f"Error updating memory item in batch: {resp.get('body', {}).get('detail', 'Unknown error')}")
                    results.append(None)
                else:
                    # Handle successful response
                    body = resp.get("body", {})
                    
                    # Invalidate cache for this memory item
                    memory_id = updates[i]["id"]
                    self._invalidate_cache(f"memory:{memory_id}")
                    
                    # Cache the updated result
                    self._add_to_cache(f"memory:{memory_id}", body)
                    
                    results.append(body)
            
            # Invalidate cache for search results since we've updated data
            self._invalidate_cache("search")
            
            logger.info(f"Updated {len(results)} memory items in batch")
            return results
            
        except Exception as e:
            logger.error(f"Batch operation failed: {str(e)}")
            
            # Fall back to processing items individually
            logger.info("Falling back to processing items individually")
            results = []
            
            for update in updates:
                try:
                    if "id" not in update:
                        raise ValueError("Update must include 'id'")
                    
                    result = self.update(update["id"], update)
                    results.append(result)
                except Exception as item_e:
                    logger.error(f"Error updating memory item in batch: {str(item_e)}")
                    results.append(None)
            
            return results
    
    def search_by_priority(self, query: str = "", min_priority: int = None, max_priority: int = None, 
                          limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for memory items with specific priority levels.
        
        This is a convenience method that wraps the search method with priority filtering.
        
        Args:
            query: Search query string
            min_priority: Minimum priority level (inclusive)
            max_priority: Maximum priority level (inclusive)
            limit: Maximum number of results to return
            
        Returns:
            List of memory items matching the criteria
        """
        # First, get all memories matching the query
        search_params = {
            "query": query,
            "limit": 100  # Get more items to filter from
        }
        
        # Get all memories matching the query
        all_memories = self.search(search_params)
        
        # Filter by priority in-memory
        filtered_memories = []
        for memory in all_memories:
            priority = memory.get("metadata", {}).get("priority", 0)
            
            # Apply priority filters
            if min_priority is not None and priority < min_priority:
                continue
            if max_priority is not None and priority > max_priority:
                continue
                
            filtered_memories.append(memory)
        
        # Sort by priority (highest first)
        filtered_memories.sort(
            key=lambda x: x.get("metadata", {}).get("priority", 0),
            reverse=True
        )
        
        # Apply limit
        return filtered_memories[:limit]
    
    def update_priority(self, memory_id: str, priority: int) -> Optional[Dict[str, Any]]:
        """
        Update the priority of a memory item.
        
        Args:
            memory_id: ID of the memory item to update
            priority: New priority value (1-10)
            
        Returns:
            Dictionary containing the updated memory item, or None if failed
        """
        # Validate priority
        if not isinstance(priority, int) or priority < 1 or priority > 10:
            logger.warning(f"Invalid priority value: {priority}. Priority must be an integer between 1 and 10.")
            return None
        
        # Update the memory item
        updates = {
            'metadata': {
                'priority': priority
            }
        }
        
        return self.update(memory_id, updates)
        
    def _summarize_memories(self, memories: List[Dict[str, Any]]) -> str:
        """
        Summarize a list of memories using an LLM.
        
        This method can be customized to use different LLMs or summarization techniques.
        
        Args:
            memories: List of memory items to summarize
            
        Returns:
            String containing the summary
        """
        try:
            # Extract content from memories
            contents = []
            for memory in memories:
                content = memory.get("content", "")
                if content:
                    # Add metadata context if available
                    timestamp = memory.get("metadata", {}).get("timestamp", "")
                    if timestamp:
                        content = f"[{timestamp}] {content}"
                    contents.append(content)
            
            # If no contents, return empty summary
            if not contents:
                return "No content to summarize."
            
            # Prepare the prompt for summarization
            prompt = f"""
            Please summarize the following {len(contents)} memories concisely while preserving key information:
            
            {chr(10).join(contents)}
            
            Summary:
            """
            
            # Here you would call your LLM of choice
            # For now, we'll use a simple placeholder
            # In a real implementation, you would replace this with a call to an LLM API
            
            # Placeholder summary (in a real implementation, this would be generated by an LLM)
            summary = f"Summary of {len(contents)} memories from {memories[0].get('metadata', {}).get('timestamp', 'unknown date')} to {memories[-1].get('metadata', {}).get('timestamp', 'unknown date')}."
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing memories: {str(e)}")
            return f"Error summarizing memories: {str(e)}"
    
    def consolidate_memories(self, query: str, days: int = 30, delete_originals: bool = False) -> Dict[str, Any]:
        """
        Consolidate older memories into a summary.
        
        This method finds memories older than the specified number of days,
        summarizes them, and stores the summary as a new memory item.
        
        Args:
            query: Search query to find memories to consolidate
            days: Age threshold in days (default: 30)
            delete_originals: Whether to delete the original memories after consolidation (default: False)
            
        Returns:
            Dictionary containing the added summary memory item, or None if no memories to consolidate
        """
        try:
            # Calculate the cutoff date
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Find memories older than specified days
            old_memories = self.search({
                "query": query,
                "metadata_filter": {
                    "timestamp": {"$lt": cutoff_date}
                },
                "limit": 100  # Limit to avoid processing too many memories at once
            })
            
            if not old_memories:
                logger.info(f"No memories found older than {days} days matching query '{query}'")
                return None
            
            # Use LLM to summarize these memories
            summary = self._summarize_memories(old_memories)
            
            # Store the summary
            summary_item = {
                "content": summary,
                "metadata": {
                    "type": "consolidation",
                    "original_count": len(old_memories),
                    "consolidation_date": datetime.now().isoformat(),
                    "original_query": query,
                    "days_threshold": days,
                    "oldest_memory_date": min(m.get("metadata", {}).get("timestamp", "") for m in old_memories if m.get("metadata", {}).get("timestamp", "")),
                    "newest_memory_date": max(m.get("metadata", {}).get("timestamp", "") for m in old_memories if m.get("metadata", {}).get("timestamp", "")),
                    "original_memory_ids": [m.get("id") for m in old_memories if m.get("id")]
                }
            }
            
            # Add the summary to memory
            result = self.add(summary_item)
            
            # Optionally delete the original memories to save space
            if delete_originals and result and result.get("id"):
                deleted_count = 0
                for memory in old_memories:
                    memory_id = memory.get("id")
                    if memory_id:
                        if self.delete(memory_id):
                            deleted_count += 1
                
                logger.info(f"Deleted {deleted_count}/{len(old_memories)} original memories after consolidation")
                
                # Update the metadata to reflect the deletion
                if deleted_count > 0:
                    self.update(result["id"], {
                        "metadata": {
                            "deleted_originals": True,
                            "deleted_count": deleted_count
                        }
                    })
            
            logger.info(f"Consolidated {len(old_memories)} memories into a summary with ID {result.get('id')}")
            return result
            
        except Exception as e:
            logger.error(f"Error consolidating memories: {str(e)}")
            return None

# Example usage
if __name__ == "__main__":
    import sys
    import os
    
    # Add the project root to the Python path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
    
    # Import configuration
    from config.settings import get_config
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Get configuration
    config = get_config()
    
    # Initialize memory client
    memory = Mem0Client(
        api_key=config['mem0']['api_key'],
        agent_id=config['mem0']['agent_id'],
        base_url=config['mem0']['base_url']
    )
    
    # Example: Add a memory item
    memory_item = {
        "content": "Example memory item",
        "metadata": {
            "type": "example",
            "timestamp": "2023-01-01T12:00:00Z"
        }
    }
    
    result = memory.add(memory_item)
    print(f"Added memory item: {result}")
    
    # Example: Search for memory items
    search_params = {
        "query": "example",
        "metadata_filter": {
            "type": "example"
        },
        "limit": 5
    }
    
    results = memory.search(search_params)
    print(f"Found {len(results)} memory items")
    
    # Example: Get a specific memory item
    if results:
        memory_id = results[0].get("id")
        memory_item = memory.get(memory_id)
        print(f"Retrieved memory item: {memory_item}")
        
        # Example: Update a memory item
        updates = {
            "metadata": {
                "updated": True,
                "update_time": "2023-01-02T12:00:00Z"
            }
        }
        
        updated_item = memory.update(memory_id, updates)
        print(f"Updated memory item: {updated_item}")
        
        # Example: Delete a memory item
        # Uncomment to test deletion
        # success = memory.delete(memory_id)
        # print(f"Deleted memory item: {success}")
    
    # Example: Clear all memory items
    # Uncomment to test clearing all memory
    # success = memory.clear()
    # print(f"Cleared all memory items: {success}") 