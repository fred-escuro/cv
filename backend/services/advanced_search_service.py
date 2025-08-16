#!/usr/bin/env python3
"""
Advanced search service supporting boolean operators and parentheses
"""

import re
from typing import Dict, Any, List, Optional
from services.prisma_database_service import PrismaDatabaseService

class AdvancedSearchService:
    """
    Service for advanced search with boolean operators (AND, OR) and parentheses
    """
    
    def __init__(self):
        self.database_service = PrismaDatabaseService()
    
    async def initialize(self):
        """Initialize the database service"""
        await self.database_service.initialize()
    
    async def close(self):
        """Close the database service"""
        await self.database_service.close()
    
    def parse_advanced_query(self, query: str) -> Dict[str, Any]:
        """
        Parse advanced search query with boolean operators and parentheses
        
        Examples:
        - "CLARITY AND (PLDT OR MERCADO)"
        - "(Systems OR Analyst) AND (Business OR IT)"
        - "Rene AND Philippines"
        """
        try:
            # Clean and normalize the query
            query = query.strip()
            if not query:
                return {"type": "simple", "query": "", "parsed": None}
            
            # Check if it's a simple query (no operators)
            # Remove quotes and extra whitespace for operator detection
            clean_query = query.strip().strip('"').strip("'")
            print(f"🔍 Original query: '{query}'")
            print(f"🔍 Cleaned query: '{clean_query}'")
            if not re.search(r'\b(AND|OR)\b', clean_query, re.IGNORECASE):
                print(f"🔍 No operators found, treating as simple query")
                return {"type": "simple", "query": query, "parsed": None}
            else:
                print(f"🔍 Operators found, treating as advanced query")
            
            # Parse advanced query
            parsed = self._parse_boolean_expression(query)
            return {
                "type": "advanced",
                "query": query,
                "parsed": parsed
            }
            
        except Exception as e:
            print(f"❌ Query parsing failed: {e}")
            # Fallback to simple search
            return {"type": "simple", "query": query, "parsed": None}
    
    def _parse_boolean_expression(self, expression: str) -> Dict[str, Any]:
        """
        Parse boolean expression with parentheses
        """
        # Remove quotes and extra whitespace, then normalize operators
        expression = expression.strip().strip('"').strip("'")
        expression = re.sub(r'\s+', ' ', expression)
        expression = re.sub(r'\b(AND|OR)\b', lambda m: m.group(1).upper(), expression, flags=re.IGNORECASE)
        
        # Parse the expression
        return self._parse_expression(expression)
    
    def _parse_expression(self, expression: str) -> Dict[str, Any]:
        """
        Recursively parse boolean expression
        """
        # Handle parentheses first
        if '(' in expression:
            return self._parse_parentheses(expression)
        
        # Handle AND/OR operators
        if ' AND ' in expression:
            parts = expression.split(' AND ', 1)
            return {
                "operator": "AND",
                "left": self._parse_expression(parts[0].strip()),
                "right": self._parse_expression(parts[1].strip())
            }
        elif ' OR ' in expression:
            parts = expression.split(' OR ', 1)
            return {
                "operator": "OR",
                "left": self._parse_expression(parts[0].strip()),
                "right": self._parse_expression(parts[1].strip())
            }
        else:
            # Single term
            return {"type": "term", "value": expression.strip()}
    
    def _parse_parentheses(self, expression: str) -> Dict[str, Any]:
        """
        Parse expression with parentheses
        """
        # Find matching parentheses
        stack = []
        start = -1
        
        for i, char in enumerate(expression):
            if char == '(':
                if not stack:
                    start = i
                stack.append(char)
            elif char == ')':
                if stack:
                    stack.pop()
                    if not stack and start != -1:
                        # Found complete parentheses group
                        inner_expr = expression[start + 1:i]
                        before = expression[:start].strip()
                        after = expression[i + 1:].strip()
                        
                        # Parse the inner expression
                        inner_parsed = self._parse_expression(inner_expr)
                        
                        # Handle what comes before and after
                        if before and after:
                            # Something before AND something after: (before) AND (inner) AND (after)
                            if ' AND ' in before or ' OR ' in before:
                                before_parsed = self._parse_expression(before)
                                after_parsed = self._parse_expression(after)
                                return {
                                    "operator": "AND",
                                    "left": before_parsed,
                                    "right": {
                                        "operator": "AND",
                                        "left": inner_parsed,
                                        "right": after_parsed
                                    }
                                }
                            else:
                                # Simple: (before) AND (inner) AND (after)
                                return {
                                    "operator": "AND",
                                    "left": {"type": "term", "value": before},
                                    "right": {
                                        "operator": "AND",
                                        "left": inner_parsed,
                                        "right": {"type": "term", "value": after}
                                    }
                                }
                        elif before:
                            # Something before: (before) AND (inner)
                            if ' AND ' in before or ' OR ' in before:
                                before_parsed = self._parse_expression(before)
                                return {
                                    "operator": "AND",
                                    "left": before_parsed,
                                    "right": inner_parsed
                                }
                            else:
                                return {
                                    "operator": "AND",
                                    "left": {"type": "term", "value": before},
                                    "right": inner_parsed
                                }
                        elif after:
                            # Something after: (inner) AND (after)
                            if ' AND ' in after or ' OR ' in after:
                                after_parsed = self._parse_expression(after)
                                return {
                                    "operator": "AND",
                                    "left": inner_parsed,
                                    "right": after_parsed
                                }
                            else:
                                return {
                                    "operator": "AND",
                                    "left": inner_parsed,
                                    "right": {"type": "term", "value": after}
                                }
                        else:
                            # Just parentheses: (inner)
                            return inner_parsed
        
        # If we get here, parentheses weren't properly matched
        raise ValueError("Unmatched parentheses in expression")
    
    async def advanced_search(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Perform advanced search with boolean operators
        """
        try:
            print(f"🔍 Starting advanced search for query: '{query}'")
            
            # Parse the query
            parsed_query = self.parse_advanced_query(query)
            print(f"🔍 Parsed query: {parsed_query}")
            
            if parsed_query["type"] == "simple":
                print(f"🔍 Query is simple, falling back to simple search")
                # Fall back to simple search
                return await self.database_service.search_cv_text(query, limit)
            
            print(f"🔍 Executing advanced search with parsed query")
            # Execute advanced search
            results = await self._execute_advanced_search(parsed_query["parsed"], limit)
            print(f"🔍 Advanced search returned {len(results)} results")
            return results
            
        except Exception as e:
            print(f"❌ Advanced search failed: {e}")
            # Fall back to simple search
            return await self.database_service.search_cv_text(query, limit)
    
    async def advanced_search_with_debug(self, query: str, limit: int = 50) -> Dict[str, Any]:
        """
        Perform advanced search with debug information returned in response
        """
        try:
            debug_info = {
                "query": query,
                "steps": []
            }
            
            # Parse the query
            parsed_query = self.parse_advanced_query(query)
            debug_info["steps"].append(f"Parsed query: {parsed_query}")
            
            if parsed_query["type"] == "simple":
                debug_info["steps"].append("Query is simple, falling back to simple search")
                results = await self.database_service.search_cv_text(query, limit)
                debug_info["steps"].append(f"Simple search returned {len(results)} results")
                return {"results": results, "debug": debug_info}
            
            # Execute advanced search
            debug_info["steps"].append(f"🔍 Parsed query structure: {parsed_query['parsed']}")
            results = await self._execute_advanced_search_with_debug(parsed_query["parsed"], limit, debug_info)
            debug_info["steps"].append(f"Advanced search returned {len(results)} results")
            
            return {"results": results, "debug": debug_info}
            
        except Exception as e:
            debug_info["steps"].append(f"Advanced search failed: {e}")
            # Fall back to simple search
            results = await self.database_service.search_cv_text(query, limit)
            return {"results": results, "debug": debug_info}
    
    async def _execute_advanced_search_with_debug(self, parsed: Dict[str, Any], limit: int, debug_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute parsed boolean expression with debug info
        """
        try:
            debug_info["steps"].append(f"🔍 Executing parsed expression: {parsed}")
            
            # Check if it's a single term
            if "type" in parsed and parsed["type"] == "term":
                # Single term search
                debug_info["steps"].append(f"🔍 Searching for term: '{parsed['value']}'")
                results = await self.database_service.search_cv_text(parsed["value"], limit)
                debug_info["steps"].append(f"Term '{parsed['value']}' search returned {len(results)} results")
                
                # Debug: Show the structure of the first result
                if results:
                    first_result = results[0]
                    debug_info["steps"].append(f"First result keys: {list(first_result.keys())}")
                    debug_info["steps"].append(f"First result file_id: {first_result.get('file_id', 'NOT_FOUND')}")
                    debug_info["steps"].append(f"First result sample: {first_result}")
                else:
                    debug_info["steps"].append(f"⚠️ No results found for term '{parsed['value']}'")
                
                return results
            
            # Boolean operation
            if "operator" in parsed and parsed["operator"] == "AND":
                # Intersection of results
                left_results = await self._execute_advanced_search_with_debug(parsed["left"], limit * 2, debug_info)
                right_results = await self._execute_advanced_search_with_debug(parsed["right"], limit * 2, debug_info)
                
                debug_info["steps"].append(f"AND operation - Left results: {len(left_results)}, Right results: {len(right_results)}")
                
                # Debug: Check the structure of results
                if left_results:
                    debug_info["steps"].append(f"Left first result keys: {list(left_results[0].keys())}")
                    debug_info["steps"].append(f"Left first result file_id: {left_results[0].get('file_id', 'NOT_FOUND')}")
                if right_results:
                    debug_info["steps"].append(f"Right first result keys: {list(right_results[0].keys())}")
                    debug_info["steps"].append(f"Right first result file_id: {right_results[0].get('file_id', 'NOT_FOUND')}")
                
                # Get unique file IDs from both results
                left_file_ids = {r["file_id"] for r in left_results}
                right_file_ids = {r["file_id"] for r in right_results}
                
                debug_info["steps"].append(f"Left file IDs: {left_file_ids}")
                debug_info["steps"].append(f"Right file IDs: {right_file_ids}")
                
                # Find intersection
                intersection_ids = left_file_ids.intersection(right_file_ids)
                debug_info["steps"].append(f"Intersection IDs: {intersection_ids}")
                
                # Combine results for intersection files
                combined_results = []
                for result in left_results + right_results:
                    if result["file_id"] in intersection_ids:
                        combined_results.append(result)
                
                # Remove duplicates and limit
                unique_results = []
                seen_file_ids = set()
                for result in combined_results:
                    if result["file_id"] not in seen_file_ids:
                        unique_results.append(result)
                        seen_file_ids.add(result["file_id"])
                        if len(unique_results) >= limit:
                            break
                
                debug_info["steps"].append(f"Final unique results: {len(unique_results)}")
                return unique_results
                
            elif "operator" in parsed and parsed["operator"] == "OR":
                # Union of results
                left_results = await self._execute_advanced_search_with_debug(parsed["left"], limit, debug_info)
                right_results = await self._execute_advanced_search_with_debug(parsed["right"], limit, debug_info)
                
                # Combine and deduplicate
                combined_results = left_results + right_results
                unique_results = []
                seen_file_ids = set()
                
                for result in combined_results:
                    if result["file_id"] not in seen_file_ids:
                        unique_results.append(result)
                        seen_file_ids.add(result["file_id"])
                        if len(unique_results) >= limit:
                            break
                
                return unique_results
            
            else:
                debug_info["steps"].append(f"⚠️ Unknown operator or expression type: {parsed}")
                return []
                
        except Exception as e:
            debug_info["steps"].append(f"❌ Error in _execute_advanced_search_with_debug: {e}")
            import traceback
            debug_info["steps"].append(f"❌ Traceback: {traceback.format_exc()}")
            return []
    
    async def _execute_advanced_search(self, parsed: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """
        Execute parsed boolean expression
        """
        if parsed["type"] == "term":
            # Single term search
            return await self.database_service.search_cv_text(parsed["value"], limit)
        
        # Boolean operation
        if parsed["operator"] == "AND":
            # Intersection of results
            left_results = await self._execute_advanced_search(parsed["left"], limit * 2)
            right_results = await self._execute_advanced_search(parsed["right"], limit * 2)
            
            print(f"🔍 AND operation - Left results: {len(left_results)}, Right results: {len(right_results)}")
            print(f"🔍 Left results sample: {left_results[:2] if left_results else 'None'}")
            print(f"🔍 Right results sample: {right_results[:2] if right_results else 'None'}")
            
            # Get unique file IDs from both results
            left_file_ids = {r["file_id"] for r in left_results}
            right_file_ids = {r["file_id"] for r in right_results}
            
            print(f"🔍 Left file IDs: {left_file_ids}")
            print(f"🔍 Right file IDs: {right_file_ids}")
            
            # Find intersection
            intersection_ids = left_file_ids.intersection(right_file_ids)
            print(f"🔍 Intersection IDs: {intersection_ids}")
            
            # Combine results for intersection files
            combined_results = []
            for result in left_results + right_results:
                if result["file_id"] in intersection_ids:
                    combined_results.append(result)
            
            # Remove duplicates and limit
            unique_results = []
            seen_file_ids = set()
            for result in combined_results:
                if result["file_id"] not in seen_file_ids:
                    unique_results.append(result)
                    seen_file_ids.add(result["file_id"])
                    if len(unique_results) >= limit:
                        break
            
            print(f"🔍 Final unique results: {len(unique_results)}")
            return unique_results
            
        elif parsed["operator"] == "OR":
            # Union of results
            left_results = await self._execute_advanced_search(parsed["left"], limit)
            right_results = await self._execute_advanced_search(parsed["right"], limit)
            
            # Combine and deduplicate
            combined_results = left_results + right_results
            unique_results = []
            seen_file_ids = set()
            
            for result in combined_results:
                if result["file_id"] not in seen_file_ids:
                    unique_results.append(result)
                    seen_file_ids.add(result["file_id"])
                    if len(unique_results) >= limit:
                        break
            
            return unique_results
        
        return []
    
    def build_search_sql(self, parsed: Dict[str, Any]) -> str:
        """
        Build PostgreSQL full-text search SQL from parsed expression
        """
        if parsed["type"] == "term":
            return f"to_tsvector('english', ctl.line_text) @@ plainto_tsquery('english', '{parsed['value']}')"
        
        if parsed["operator"] == "AND":
            left_sql = self.build_search_sql(parsed["left"])
            right_sql = self.build_search_sql(parsed["right"])
            return f"({left_sql}) AND ({right_sql})"
        
        if parsed["operator"] == "OR":
            left_sql = self.build_search_sql(parsed["left"])
            right_sql = self.build_search_sql(parsed["right"])
            return f"({left_sql}) OR ({right_sql})"
        
        return ""
