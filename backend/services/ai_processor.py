import os
import json
import aiohttp
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List
from pathlib import Path

# Import configuration
try:
    from config import TEXT_PROCESSING_CONFIG, AI_MODEL_CONFIG, PROCESSING_CONFIG
except ImportError:
    # Fallback configuration if config file is not available
    TEXT_PROCESSING_CONFIG = {
        "MAX_TEXT_LENGTH_BEFORE_CHUNKING": 50000,
        "MAX_CHUNK_SIZE": 40000,
        "MIN_CHUNK_SIZE": 10000,
        "CHUNK_OVERLAP": 2000,
        "MAX_CHUNKS": 10,
    }
    AI_MODEL_CONFIG = {
        "MODEL_TOKEN_LIMITS": {
            'anthropic/claude-3.5-sonnet': 200000,
            'openai/gpt-4o': 128000,
            'anthropic/claude-3-haiku': 200000,
            'meta-llama/llama-3.1-8b-instruct': 8192,
        },
        "DEFAULT_MAX_TOKENS": 8000,
        "MIN_MAX_TOKENS": 2000,
        "SAFETY_BUFFER_TOKENS": 1000,
        "TEMPERATURE": 0.1,
    }
    PROCESSING_CONFIG = {
        "ENABLE_CHUNKING": True,
        "ENABLE_DETAILED_LOGGING": True,
        "MAX_CHUNK_RETRIES": 2,
        "AI_API_TIMEOUT": 120,
        "ENABLE_FALLBACK_MODELS": True,
    }

# Load environment variables
load_dotenv()

class AIProcessor:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
        
        # Primary model and fallback models
        self.primary_model = os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')
        self.fallback_models = [
            os.getenv('OPENROUTER_FALLBACK_MODEL_1', 'openai/gpt-4o'),
            os.getenv('OPENROUTER_FALLBACK_MODEL_2', 'anthropic/claude-3-haiku'),
            os.getenv('OPENROUTER_FALLBACK_MODEL_3', 'meta-llama/llama-3.1-8b-instruct')
        ]
        
        # Use configuration for token limits and processing parameters
        self.model_token_limits = AI_MODEL_CONFIG["MODEL_TOKEN_LIMITS"]
        self.enable_fallback_models = PROCESSING_CONFIG["ENABLE_FALLBACK_MODELS"]
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
    
    async def process_cv_to_json(self, filename: str, text_content: str) -> Dict[str, Any]:
        """
        Process CV text content and extract structured information using OpenRouter AI
        Sends entire CV to AI, handles response truncation if needed
        """
        print(f"Processing CV: {filename}")
        print(f"Text length: {len(text_content)} characters")
        
        # Always send the entire CV to AI - no text chunking
        print(f"📤 Sending entire CV ({len(text_content)} chars) to AI for processing...")
        
        # Try primary model first
        try:
            print(f"🤖 Attempting to process with primary model: {self.primary_model}")
            ai_response_info = await self._process_cv_single_request(filename, text_content, self.primary_model)
            
            # The ai_response_info already contains the parsed ai_data, no need to parse again
            return {
                "ai_data": ai_response_info["ai_data"],
                "model_used": ai_response_info["model_used"],
                "processing_duration_ms": ai_response_info["processing_duration_ms"],
                "success": True
            }
            
        except Exception as primary_error:
            print(f"❌ Primary model {self.primary_model} failed: {primary_error}")
            
            if not self.enable_fallback_models:
                raise primary_error
            
            # Try fallback models
            for fallback_model in self.fallback_models:
                try:
                    print(f"🔄 Trying fallback model: {fallback_model}")
                    ai_response_info = await self._process_cv_single_request(filename, text_content, fallback_model)
                    
                    # The ai_response_info already contains the parsed ai_data, no need to parse again
                    return {
                        "ai_data": ai_response_info["ai_data"],
                        "model_used": ai_response_info["model_used"],
                        "processing_duration_ms": ai_response_info["processing_duration_ms"],
                        "success": True
                    }
                    
                except Exception as fallback_error:
                    print(f"❌ Fallback model {fallback_model} failed: {fallback_error}")
                    continue
            
            # All models failed
            raise Exception(f"All AI models failed. Primary error: {primary_error}")
    

    

    

    

    

    
    def _calculate_max_tokens(self, model: str, prompt_length: int) -> int:
        """
        Calculate appropriate max_tokens based on model and prompt length
        """
        # Get model's context window limit
        model_limit = self.model_token_limits.get(model, 8192)
        
        # Estimate tokens from characters (rough approximation: 1 token ≈ 4 characters)
        estimated_prompt_tokens = prompt_length // 4
        
        # For CV processing, we need more tokens for comprehensive responses
        # Since we're sending the entire CV, allocate more tokens for the response
        base_response_tokens = 15000  # Base tokens for comprehensive CV response
        
        # Add extra tokens for long CVs to prevent truncation
        if prompt_length > 100000:
            base_response_tokens = 30000  # Very long CVs need more response tokens
        elif prompt_length > 50000:
            base_response_tokens = 25000  # Long CVs need more response tokens
        elif prompt_length > 20000:
            base_response_tokens = 20000  # Medium CVs need more response tokens
        
        # Reserve some tokens for the response
        response_tokens = min(
            base_response_tokens, 
            model_limit - estimated_prompt_tokens - AI_MODEL_CONFIG["SAFETY_BUFFER_TOKENS"]
        )
        
        # Ensure we don't exceed model limits
        max_tokens = min(
            response_tokens, 
            model_limit - estimated_prompt_tokens - AI_MODEL_CONFIG["SAFETY_BUFFER_TOKENS"]
        )
        
        # Set a minimum reasonable limit
        max_tokens = max(max_tokens, AI_MODEL_CONFIG["MIN_MAX_TOKENS"])
        
        print(f"Token calculation for {model}:")
        print(f"   Model limit: {model_limit}")
        print(f"   Estimated prompt tokens: {estimated_prompt_tokens}")
        print(f"   Base response tokens: {base_response_tokens}")
        print(f"   Max response tokens: {max_tokens}")
        print(f"   Available context: {model_limit - estimated_prompt_tokens - max_tokens}")
        
        return max_tokens
    
    async def _process_cv_single_request(self, filename: str, text_content: str, model: str) -> Dict[str, Any]:
        """
        Process CV with a single API request (for shorter texts or individual chunks)
        """
        # Try primary model first
        models_to_try = [self.primary_model] + (self.fallback_models if self.enable_fallback_models else [])
        last_error = None
        
        for i, model in enumerate(models_to_try):
            try:
                print(f"Trying model {i+1}/{len(models_to_try)}: {model}")
                
                # Create the AI prompt
                prompt = self._create_cv_prompt(filename, text_content)
                
                # Call OpenRouter API with current model
                ai_response_info = await self._call_openrouter_api(prompt, model)
                
                # Parse and validate the response
                result = await self._parse_ai_response(ai_response_info["content"], prompt, model)
                
                # Final validation to ensure the result is properly formatted
                if not isinstance(result, dict):
                    raise Exception(f"AI response is not a valid dictionary, got {type(result).__name__}")
                
                if "personal_information" not in result:
                    raise Exception("AI response missing required 'personal_information' section")
                
                print(f"Successfully processed with model: {model}")
                return {
                    "ai_data": result,
                    "model_used": model,
                    "processing_duration_ms": 0,  # Will be calculated by caller
                    "success": True
                }
                
            except Exception as e:
                print(f"Model {model} failed: {str(e)}")
                last_error = e
                
                # If this is the last model, raise the error
                if i == len(models_to_try) - 1:
                    break
                
                # Continue to next model
                continue
        
        # All models failed, return error details for frontend display
        error_details = {
            "error": True,
            "error_message": f"All models failed. Last error: {str(last_error)}",
            "raw_ai_response": getattr(last_error, 'raw_response', None),
            "filename": filename,
            "text_content_preview": text_content[:500] + "..." if len(text_content) > 500 else text_content,
            "models_tried": models_to_try
        }
        raise Exception(json.dumps(error_details))
    
    def _create_cv_prompt(self, filename: str, text_content: str) -> str:
        """
        Create the AI prompt for CV parsing
        """
        # For long texts, add a note about focusing on key information
        if len(text_content) > 20000:
            prompt = f"""Please analyze the following CV document and extract detailed information into a structured JSON format.
This is a long CV document - focus on extracting ALL available information while maintaining accuracy.

Document: {filename}
Text Length: {len(text_content)} characters

CV Content:
{text_content}

IMPORTANT: You MUST output the CV data in EXACTLY this JSON format. Do not modify the structure or field names.
Since this is a long document, ensure you capture ALL sections and details present."""
        else:
            prompt = f"""Please analyze the following CV document and extract detailed information into a structured JSON format.

Document: {filename}

CV Content:
{text_content}

IMPORTANT: You MUST output the CV data in EXACTLY this JSON format. Do not modify the structure or field names."""
        
        prompt += """

{
  "personal_information": {
    "first_name": "string",
    "middle_name": "string",
    "last_name": "string",
    "emails": ["string"],
    "birth_date": "YYYY-MM-DD",
    "gender": "string",
    "civil_status": "string",
    "alias": ["string"],
    "phones": [
      {
        "type": "string",
        "number": "string"
      }
    ],
    "address": {
      "street": "string",
      "barangay": "string",
      "city": "string",
      "state": "string",
      "postal_code": "string",
      "country": "string"
    },
    "desired_location": {
      "city": "string",
      "state": "string",
      "country": "string"
    },
    "work_preference": {
      "open_to_work_from_home": boolean,
      "open_to_onsite": boolean
    },
    "social_urls": [
      {
        "platform": "string",
        "url": "string"
      }
    ]
  },
  "professional_summary": "string",
  "work_experience": [
    {
      "job_title": "string",
      "company_name": "string",
      "location": "string",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or Present",
      "responsibilities": ["string"]
    }
  ],
  "it_system_used": [
    {
      "abbreviation": "string",
      "name_of_system": "string"
    }
  ],
  "education": [
    {
      "degree": "string",
      "institution": "string",
      "location": "string",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM",
      "gpa": "string (optional)",
      "honors": "string (optional)"
    }
  ],
  "skills": {
    "technical_skills": ["string"],
    "soft_skills": ["string"],
    "computer_languages": [
      {
        "language": "string",
        "proficiency": "string"
      }
    ]
  },
  "certifications": [
    {
      "name": "string",
      "issuing_organization": "string",
      "issue_date": "YYYY-MM",
      "expiration_date": "YYYY-MM (optional)",
      "credential_id": "string (optional)"
    }
  ],
  "projects": [
    {
      "title": "string",
      "description": "string",
      "technologies_used": ["string"],
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or Present",
      "project_url": "string (optional)"
    }
  ],
  "awards_and_honors": [
    {
      "title": "string",
      "issuer": "string",
      "date_received": "YYYY-MM",
      "description": "string"
    }
  ],
  "volunteer_experience": [
    {
      "role": "string",
      "organization": "string",
      "location": "string",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or Present",
      "description": "string"
    }
  ],
  "interests": ["string"],
  "references": [
    {
      "name": "string",
      "relationship": "string",
      "email": "string",
      "phone": "string"
    }
  ],
  "additional_information": "string (optional, for any extra details not fitting the above structure)"
}

CRITICAL REQUIREMENTS:
1. The output MUST follow this EXACT JSON structure - do not change field names or structure
2. REQUIRED fields: "first_name" and "last_name" in personal_information section
3. Extract ALL information possible from the CV content
4. If a field is not available in the CV, use null or empty string as appropriate
5. Ensure the response is valid JSON format
6. Do not include any explanations or text outside the JSON structure
7. Use arrays for multiple items (e.g., multiple skills, experiences)
8. For dates, use YYYY-MM format for months, YYYY-MM-DD for specific dates
9. For boolean values, use true/false
10. If the CV content is unclear or incomplete, make reasonable inferences based on context
11. The "end_date" can be "Present" for ongoing positions/education
12. IMPORTANT: Your response MUST be ONLY the JSON object - no markdown, no explanations, no additional text
13. CRITICAL: Ensure ALL object keys are properly quoted with double quotes (e.g., "name": not name:)
14. Pay special attention to nested objects in arrays like references, work_experience, etc.
15. BE CONCISE: Use brief, relevant descriptions. Avoid verbose explanations.
16. PRIORITIZE: Focus on the most important information if space is limited.
17. Work experience should be in reverse chronological order.

Please provide ONLY the JSON response without any additional text, markdown formatting, or explanations.

REMEMBER: The API is configured to expect JSON format only. Any non-JSON content will cause parsing errors."""
        
        return prompt
    
    async def _call_openrouter_api(self, prompt: str, model: str) -> Dict[str, Any]:
        """
        Call OpenRouter API with the CV processing prompt and specified model
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://cv-transform-app.com",
            "X-Title": "CV Transform App"
        }
        
        # Calculate appropriate token limits based on model and content length
        max_tokens = self._calculate_max_tokens(model, len(prompt))
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a CV parsing assistant. Output CV data in the EXACT JSON format specified. Include 'first_name' and 'last_name' in personal_information. Respond with valid JSON only - no explanations or markdown. If response is too long, prioritize key information and ensure JSON is complete."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": AI_MODEL_CONFIG["TEMPERATURE"],
            "response_format": {"type": "json_object"}
        }
        
        timeout = aiohttp.ClientTimeout(total=PROCESSING_CONFIG["AI_API_TIMEOUT"])
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenRouter API error: {response.status} - {error_text}")
                
                result = await response.json()
                ai_response = result['choices'][0]['message']['content']
                
                # TEMPORARY: Print the raw AI response for debugging
                print("\n" + "="*80)
                print("🤖 RAW AI RESPONSE:")
                print("="*80)
                print(ai_response)
                print("="*80)
                print(f"Response length: {len(ai_response)} characters")
                print(f"Response ends with '}}': {ai_response.strip().endswith('}')}")
                print("="*80 + "\n")
                
                # Check if response was truncated
                if result['choices'][0].get('finish_reason') == 'length':
                    print(f"⚠️  Warning: AI response was truncated due to token limit. Max tokens: {max_tokens}")
                    # Try to fix truncated JSON
                    ai_response = self._fix_truncated_json(ai_response)
                
                # Also check for other signs of truncation
                if not ai_response.strip().endswith('}'):
                    print(f"⚠️  Warning: AI response doesn't end with closing brace, may be truncated")
                    # Try to fix truncated JSON
                    ai_response = self._fix_truncated_json(ai_response)
                
                # Return response with model information
                return {
                    "content": ai_response,
                    "model_used": model,
                    "finish_reason": result['choices'][0].get('finish_reason'),
                    "usage": result.get('usage', {}),
                    "processing_duration_ms": 0  # Will be calculated by caller
                }
    
    def _fix_truncated_json(self, truncated_response: str) -> str:
        """
        Attempt to fix truncated JSON responses by completing missing parts
        """
        print("🔧 Attempting to fix truncated JSON response...")
        
        # Remove any trailing incomplete content
        response = truncated_response.strip()
        
        # Find the last complete JSON structure
        brace_count = 0
        bracket_count = 0
        last_complete_pos = 0
        
        for i, char in enumerate(response):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            elif char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
            
            # If we have balanced braces and brackets, this is a complete position
            if brace_count == 0 and bracket_count == 0:
                last_complete_pos = i + 1
        
        # If we found a complete JSON structure, use it
        if last_complete_pos > 0:
            complete_json = response[:last_complete_pos]
            print(f"✅ Found complete JSON structure at position {last_complete_pos}")
            return complete_json
        
        # If no complete structure found, try to complete the JSON
        print("⚠️  No complete JSON structure found, attempting to complete...")
        
        # Count opening braces/brackets to see what's missing
        open_braces = response.count('{') - response.count('}')
        open_brackets = response.count('[') - response.count(']')
        
        # Try to complete the JSON
        completed_response = response
        
        # Close any open brackets first
        for _ in range(open_brackets):
            completed_response += ']'
        
        # Close any open braces
        for _ in range(open_braces):
            completed_response += '}'
        
        print(f"🔧 Completed JSON with {open_brackets} brackets and {open_braces} braces")
        return completed_response
    
    async def _parse_ai_response(self, ai_response: str, original_prompt: str = None, model: str = None) -> Dict[str, Any]:
        """
        Parse and validate the AI response with enhanced error handling
        Now includes AI continuation for truncated responses with valid structure
        """
        try:
            # Try to parse the response as JSON
            result = json.loads(ai_response)
            
            # Validate that it's a dictionary
            if not isinstance(result, dict):
                raise Exception("AI response is not a valid JSON object")
            
            # Validate required fields
            self._validate_required_fields(result)
            
            # Validate JSON structure format
            self._validate_json_format(result)
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse AI response as JSON: {e}")
            print(f"AI Response length: {len(ai_response)} characters")
            print(f"AI Response preview: {ai_response[:500]}...")
            print(f"AI Response end: ...{ai_response[-500:]}")
            
            # NEW APPROACH: Try AI continuation if we have valid starting structure
            if original_prompt and model and self._has_valid_starting_structure(ai_response):
                print("🔄 Detected valid starting structure in truncated response, attempting AI continuation...")
                try:
                    continued_response = await self._continue_ai_response(ai_response, original_prompt, model)
                    if continued_response:
                        # Concatenate the original and continued responses
                        combined_response = self._concatenate_responses(ai_response, continued_response)
                        print(f"✅ Successfully continued AI response and combined")
                        print(f"Combined response length: {len(combined_response)} characters")
                        
                        # Try to parse the combined response
                        result = json.loads(combined_response)
                        return self._validate_and_return_result(result)
                    else:
                        print("❌ AI continuation failed")
                except Exception as continue_error:
                    print(f"❌ AI continuation error: {continue_error}")
            
            # Try multiple approaches to fix the JSON
            fixed_response = None
            
            # Approach 1: Fix common JSON issues
            try:
                fixed_response = self._fix_common_json_issues(ai_response)
                result = json.loads(fixed_response)
                print("✅ Successfully fixed JSON issues and parsed response")
                return self._validate_and_return_result(result)
            except Exception as fix_error:
                print(f"❌ Approach 1 (fix common issues) failed: {fix_error}")
            
            # Approach 2: Try to extract valid JSON from the response
            try:
                fixed_response = self._extract_valid_json(ai_response)
                if fixed_response:
                    result = json.loads(fixed_response)
                    print("✅ Successfully extracted valid JSON from response")
                    return self._validate_and_return_result(result)
            except Exception as extract_error:
                print(f"❌ Approach 2 (extract valid JSON) failed: {extract_error}")
            
            # Approach 3: Try to complete truncated JSON
            try:
                fixed_response = self._complete_truncated_json(ai_response)
                if fixed_response:
                    result = json.loads(fixed_response)
                    print("✅ Successfully completed truncated JSON")
                    return self._validate_and_return_result(result)
            except Exception as complete_error:
                print(f"❌ Approach 3 (complete truncated JSON) failed: {complete_error}")
            
            # All approaches failed
            print("❌ All JSON repair approaches failed")
            error_exception = Exception("AI response could not be parsed as valid JSON and all repair attempts failed")
            error_exception.raw_response = ai_response
            raise error_exception
                
        except Exception as e:
            print(f"Error parsing AI response: {e}")
            raise
    
    def _validate_and_return_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and return the parsed result
        """
        # Validate that it's a dictionary
        if not isinstance(result, dict):
            raise Exception("Fixed AI response is not a valid JSON object")
        
        # Validate required fields
        self._validate_required_fields(result)
        
        # Validate JSON structure format
        self._validate_json_format(result)
        
        return result
    
    def _extract_valid_json(self, response: str) -> str:
        """
        Try to extract valid JSON from a malformed response
        """
        print("🔍 Attempting to extract valid JSON from response...")
        
        # Look for JSON-like patterns
        import re
        
        # Find the first { and try to match it with the last }
        start_brace = response.find('{')
        if start_brace == -1:
            print("❌ No opening brace found")
            return None
        
        # Find the last } that balances the first {
        brace_count = 0
        end_brace = -1
        
        for i in range(start_brace, len(response)):
            if response[i] == '{':
                brace_count += 1
            elif response[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_brace = i
                    break
        
        if end_brace == -1:
            print("❌ No matching closing brace found")
            return None
        
        # Extract the potential JSON
        potential_json = response[start_brace:end_brace + 1]
        print(f"🔍 Extracted potential JSON from position {start_brace} to {end_brace}")
        
        # Try to parse it
        try:
            json.loads(potential_json)
            print("✅ Extracted JSON is valid")
            return potential_json
        except json.JSONDecodeError:
            print("❌ Extracted JSON is still invalid")
            return None
    
    def _complete_truncated_json(self, response: str) -> str:
        """
        Try to complete a truncated JSON response
        """
        print("🔧 Attempting to complete truncated JSON...")
        
        # Remove trailing incomplete content
        response = response.strip()
        
        # Find the last complete object or array
        last_complete = self._find_last_complete_structure(response)
        if last_complete:
            print(f"✅ Found last complete structure at position {last_complete}")
            return response[:last_complete]
        
        # If no complete structure, try to complete the JSON
        print("⚠️  No complete structure found, attempting to complete...")
        
        # Count unclosed braces and brackets
        open_braces = response.count('{') - response.count('}')
        open_brackets = response.count('[') - response.count(']')
        
        if open_braces < 0 or open_brackets < 0:
            print("❌ Too many closing braces/brackets")
            return None
        
        # Complete the JSON
        completed = response
        
        # Close arrays first, then objects
        for _ in range(open_brackets):
            completed += ']'
        
        for _ in range(open_braces):
            completed += '}'
        
        print(f"🔧 Completed with {open_brackets} brackets and {open_braces} braces")
        
        # Try to fix common issues before validation
        try:
            # Try to parse as-is first
            json.loads(completed)
            print("✅ Completed JSON is valid")
            return completed
        except json.JSONDecodeError as e:
            print(f"⚠️  Completed JSON has syntax errors: {e}")
            
            # Try to fix common syntax issues
            try:
                fixed = self._fix_common_json_issues(completed)
                json.loads(fixed)
                print("✅ Fixed and completed JSON is valid")
                return fixed
            except:
                print("❌ Could not fix syntax errors")
                return None
    
    def _find_last_complete_structure(self, response: str) -> int:
        """
        Find the position of the last complete JSON structure
        """
        brace_count = 0
        bracket_count = 0
        last_complete = 0
        
        for i, char in enumerate(response):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
            elif char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
            
            # If we have balanced braces and brackets, this is a complete position
            if brace_count == 0 and bracket_count == 0:
                last_complete = i + 1
        
        return last_complete
    
    def _fix_common_json_issues(self, ai_response: str) -> str:
        """
        Try to fix common JSON malformation issues
        """
        print("Attempting to fix common JSON issues...")
        
        import re
        
        # Fix missing quotes around object keys in various contexts
        # Pattern: { key: value } -> { "key": value }
        # This handles the main issue we saw with references
        
        # Fix missing quotes around object keys in arrays
        # Pattern: [ { key: value } ] -> [ { "key": value } ]
        fixed_response = re.sub(r'\[\s*{\s*([^"\s]+):', r'[{ "\1":', ai_response)
        
        # Fix missing quotes around object keys in nested objects
        # Pattern: "key": { nested_key: value } -> "key": { "nested_key": value }
        fixed_response = re.sub(r'{\s*([^"\s]+):', r'{ "\1":', fixed_response)
        
        # Fix missing quotes around object keys that appear after commas
        # Pattern: , key: value -> , "key": value
        fixed_response = re.sub(r',\s*([^"\s]+):', r', "\1":', fixed_response)
        
        # Fix missing quotes around object keys that appear after colons
        # Pattern: : { key: value } -> : { "key": value }
        fixed_response = re.sub(r':\s*{\s*([^"\s]+):', r': { "\1":', fixed_response)
        
        # Fix the specific case we saw: ": "value" -> "name": "value"
        # This handles cases where the key is completely missing
        fixed_response = re.sub(r'{\s*":\s*"([^"]+)"', r'{ "name": "\1"', fixed_response)
        
        print("JSON repair attempts completed")
        print(f"Original response length: {len(ai_response)}")
        print(f"Fixed response length: {len(fixed_response)}")
        
        return fixed_response
    
    def _validate_required_fields(self, data: Dict[str, Any]) -> None:
        """
        Validate that the required fields are present
        """
        try:
            # Check if personal_information section exists
            if "personal_information" not in data:
                raise Exception("Missing required section 'personal_information'")
            
            personal_info = data["personal_information"]
            
            # Check required fields
            if not personal_info.get("first_name"):
                raise Exception("Missing required field 'first_name' in personal_information")
            if not personal_info.get("last_name"):
                raise Exception("Missing required field 'last_name' in personal_information")
            
            print("Required fields validation passed: first_name and last_name are present")
            
        except Exception as e:
            print(f"Required fields validation failed: {str(e)}")
            raise
    
    def _validate_json_format(self, data: Dict[str, Any]) -> None:
        """
        Validate that the JSON follows the expected structure
        """
        try:
            expected_structure = {
                "personal_information": dict,
                "professional_summary": str,
                "work_experience": list,
                "it_system_used": list,
                "education": list,
                "skills": dict,
                "certifications": list,
                "projects": list,
                "awards_and_honors": list,
                "volunteer_experience": list,
                "interests": list,
                "references": list,
                "additional_information": str
            }
            
            validation_warnings = []
            
            for key, expected_type in expected_structure.items():
                if key in data:
                    if not isinstance(data[key], expected_type):
                        validation_warnings.append(f"Field '{key}' should be {expected_type.__name__}, got {type(data[key]).__name__}")
                else:
                    validation_warnings.append(f"Missing optional field '{key}'")
            
            # Validate personal_information structure
            if "personal_information" in data:
                personal_info = data["personal_information"]
                expected_personal_fields = {
                    "first_name": str,
                    "middle_name": str,
                    "last_name": str,
                    "emails": list,
                    "birth_date": str,
                    "gender": str,
                    "civil_status": str,
                    "alias": list,
                    "phones": list,
                    "address": dict,
                    "desired_location": dict,
                    "work_preference": dict,
                    "social_urls": list
                }
                
                for field, expected_type in expected_personal_fields.items():
                    if field in personal_info:
                        if not isinstance(personal_info[field], expected_type):
                            validation_warnings.append(f"personal_information.{field} should be {expected_type.__name__}, got {type(personal_info[field]).__name__}")
                    else:
                        validation_warnings.append(f"Missing optional personal_information field '{field}'")
            
            # Validate references structure specifically
            if "references" in data and isinstance(data["references"], list):
                for i, reference in enumerate(data["references"]):
                    if not isinstance(reference, dict):
                        validation_warnings.append(f"Reference {i} should be an object, got {type(reference).__name__}")
                    else:
                        if "name" not in reference:
                            validation_warnings.append(f"Reference {i} missing required 'name' field")
                        if "relationship" not in reference:
                            validation_warnings.append(f"Reference {i} missing required 'relationship' field")
            
            if validation_warnings:
                print("JSON structure validation warnings:")
                for warning in validation_warnings:
                    print(f"   - {warning}")
            else:
                print("JSON structure validation completed successfully")
                
        except Exception as e:
            print(f"JSON structure validation failed: {str(e)}")
            raise

    def _has_valid_starting_structure(self, response: str) -> bool:
        """
        Check if the truncated response has valid starting structure
        """
        print("🔍 Checking if response has valid starting structure...")
        
        # Look for the opening brace
        start_brace = response.find('{')
        if start_brace == -1:
            print("❌ No opening brace found")
            return False
        
        # Look for key CV structure elements
        required_elements = [
            '"personal_information"',
            '"first_name"',
            '"last_name"'
        ]
        
        found_elements = 0
        for element in required_elements:
            if element in response:
                found_elements += 1
                print(f"✅ Found required element: {element}")
        
        # We need at least 2 out of 3 required elements to consider it valid
        if found_elements >= 2:
            print(f"✅ Valid starting structure detected ({found_elements}/3 required elements)")
            return True
        else:
            print(f"❌ Insufficient starting structure ({found_elements}/3 required elements)")
            return False

    async def _continue_ai_response(self, truncated_response: str, original_prompt: str, model: str) -> str:
        """
        Ask the AI to continue from where the truncated response left off
        """
        print("🔄 Requesting AI to continue truncated response...")
        
        # Find the last complete object or array in the truncated response
        last_complete_pos = self._find_last_complete_structure(truncated_response)
        if last_complete_pos == 0:
            print("❌ Could not find last complete structure")
            return None
        
        # Extract the last complete part
        last_complete = truncated_response[:last_complete_pos]
        print(f"📝 Last complete structure ends at position {last_complete_pos}")
        
        # Create a continuation prompt
        continuation_prompt = f"""Your previous response was truncated. Please continue from where you left off.

Previous response (truncated):
{last_complete}

IMPORTANT: 
1. Continue the JSON structure from where it was cut off
2. Do NOT repeat any content from the previous response
3. Do NOT add opening braces or brackets - continue from where the previous response ended
4. Ensure the final result is valid JSON when combined with the previous response
5. Include the closing brace }} at the end

Continue the JSON response:"""
        
        try:
            # Call the AI with the continuation prompt
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://cv-transform-app.com",
                "X-Title": "CV Transform App"
            }
            
            # Use a smaller max_tokens for continuation
            max_tokens = min(10000, self.model_token_limits.get(model, 8000))
            
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a CV parsing assistant. Continue the JSON response from where it was truncated. Do not repeat content, just continue the structure."
                    },
                    {
                        "role": "user",
                        "content": continuation_prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": AI_MODEL_CONFIG["TEMPERATURE"],
                "response_format": {"type": "json_object"}
            }
            
            timeout = aiohttp.ClientTimeout(total=PROCESSING_CONFIG["AI_API_TIMEOUT"])
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        print(f"❌ Continuation API call failed: {response.status} - {error_text}")
                        return None
                    
                    result = await response.json()
                    continuation = result['choices'][0]['message']['content']
                    
                    print(f"✅ AI continuation received: {len(continuation)} characters")
                    print(f"Continuation preview: {continuation[:200]}...")
                    
                    return continuation
                    
        except Exception as e:
            print(f"❌ Error during AI continuation: {e}")
            return None

    def _concatenate_responses(self, original_response: str, continuation: str) -> str:
        """
        Concatenate the original truncated response with the continuation
        """
        print("🔗 Concatenating original response with continuation...")
        
        # Find the last complete structure in the original response
        last_complete_pos = self._find_last_complete_structure(original_response)
        if last_complete_pos == 0:
            print("❌ Could not find last complete structure in original response")
            return None
        
        # Extract the complete part of the original response
        complete_part = original_response[:last_complete_pos]
        
        # Remove any trailing commas or incomplete structures
        complete_part = complete_part.rstrip().rstrip(',')
        
        # Combine the complete part with the continuation
        combined = complete_part + continuation
        
        print(f"✅ Successfully concatenated responses")
        print(f"Original complete part: {len(complete_part)} characters")
        print(f"Continuation: {len(continuation)} characters")
        print(f"Combined: {len(combined)} characters")
        
        return combined
