"""
Explanation Agent for Financial Risk Management System
Phase 4: Agent Layer Implementation

This agent uses IBM watsonx.ai (Granite model) to generate natural language
explanations of risk assessment results for compliance officers.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
try:
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    WATSONX_AVAILABLE = True
except ImportError:
    WATSONX_AVAILABLE = False
    logging.warning("ibm-watsonx-ai not available. ExplanationAgent will use fallback mode.")


class ExplanationAgent:
    """
    Agent specialized in generating natural language explanations of risk assessments.
    
    Uses IBM watsonx.ai Granite model to create clear, actionable explanations
    for compliance officers. Falls back to rule-based explanations if LLM fails.
    """
    
    MODEL_ID = "ibm/granite-4-h-small"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        url: Optional[str] = None,
        project_id: Optional[str] = None
    ):
        """
        Initialize the Explanation Agent.

        Args:
            api_key: IBM Cloud API key for watsonx.ai
            url: watsonx.ai service URL
            project_id: watsonx.ai project ID
        """
        self.agent_name = "ExplanationAgent"
        self.api_key = api_key
        self.url = url
        self.project_id = project_id
        self.model = None
        
        # Initialize watsonx.ai model if credentials provided
        if WATSONX_AVAILABLE and api_key and url and project_id:
            try:
                credentials = Credentials(
                    api_key=api_key,
                    url=url
                )
                self.model = ModelInference(
                    model_id=self.MODEL_ID,
                    credentials=credentials,
                    project_id=project_id,
                    params={
                        "max_new_tokens": 500,
                        "temperature": 0.3,
                        "repetition_penalty": 1.1
                    }
                )
                logging.info(f"ExplanationAgent initialized with {self.MODEL_ID}")
            except Exception as e:
                logging.error(f"Failed to initialize watsonx.ai model: {e}")
                self.model = None
        else:
            logging.info("ExplanationAgent initialized in fallback mode (no LLM)")
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate natural language explanation of risk assessment results.
        
        Args:
            input_data: Dictionary containing:
                - account_id (str, required): Account ID
                - risk_score (float, required): Risk score (0.0-1.0)
                - risk_level (str, required): Risk level (critical/high/medium/low/minimal)
                - aml_patterns (list, optional): List of detected AML patterns
                - recommendations (list, optional): List of recommendations
                
        Returns:
            Dictionary with:
                - status (str): "success" or "error"
                - result (dict): Explanation results if successful
                - metadata (dict): Agent execution metadata
                
        Example:
            >>> agent = ExplanationAgent(api_key="...", url="...", project_id="...")
            >>> result = agent.run({
            ...     "account_id": "8000EBD30",
            ...     "risk_score": 0.73,
            ...     "risk_level": "high",
            ...     "aml_patterns": [{"pattern_type": "smurfing", "severity": "high"}],
            ...     "recommendations": [{"action": "REVIEW", "priority": "high"}]
            ... })
            >>> print(result['result']['explanation'])
        """
        start_time = datetime.utcnow()
        
        try:
            # Validate input
            validation_error = self._validate_input(input_data)
            if validation_error:
                return {
                    'status': 'error',
                    'result': None,
                    'metadata': {
                        'agent': self.agent_name,
                        'error': validation_error,
                        'timestamp': start_time.isoformat()
                    }
                }
            
            account_id = input_data['account_id']
            risk_score = float(input_data['risk_score'])
            risk_level = input_data['risk_level']
            aml_patterns = input_data.get('aml_patterns', [])
            recommendations = input_data.get('recommendations', [])
            
            # Try to generate LLM explanation
            explanation = None
            model_used = "fallback"
            tokens_used = 0
            
            if self.model:
                try:
                    explanation, tokens_used = self._generate_llm_explanation(
                        account_id, risk_score, risk_level, aml_patterns, recommendations
                    )
                    model_used = self.MODEL_ID
                except Exception as e:
                    logging.warning(f"LLM explanation failed: {e}. Using fallback.")
            
            # Fallback to rule-based explanation if LLM failed or unavailable
            if not explanation:
                explanation = self._generate_fallback_explanation(
                    account_id, risk_score, risk_level, aml_patterns, recommendations
                )
            
            result = {
                'account_id': account_id,
                'explanation': explanation,
                'model_used': model_used,
                'tokens_used': tokens_used,
                'risk_score': risk_score,
                'risk_level': risk_level
            }
            
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            return {
                'status': 'success',
                'result': result,
                'metadata': {
                    'agent': self.agent_name,
                    'execution_time_seconds': round(execution_time, 3),
                    'timestamp': end_time.isoformat(),
                    'model_used': model_used,
                    'tokens_used': tokens_used
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'result': None,
                'metadata': {
                    'agent': self.agent_name,
                    'error': f"Unexpected error: {str(e)}",
                    'error_type': type(e).__name__,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
    
    def _validate_input(self, input_data: Dict[str, Any]) -> Optional[str]:
        """Validate input data. Returns error message if invalid, None if valid."""
        if not input_data:
            return "Input data is required"
        
        required_fields = ['account_id', 'risk_score', 'risk_level']
        for field in required_fields:
            if field not in input_data:
                return f"Missing required field: {field}"
        
        # Validate risk_score
        try:
            risk_score = float(input_data['risk_score'])
            if risk_score < 0.0 or risk_score > 1.0:
                return "risk_score must be between 0.0 and 1.0"
        except (ValueError, TypeError):
            return "risk_score must be a valid number"
        
        # Validate risk_level
        valid_levels = ['critical', 'high', 'medium', 'low', 'minimal']
        if input_data['risk_level'] not in valid_levels:
            return f"risk_level must be one of: {', '.join(valid_levels)}"
        
        return None
    
    def _generate_llm_explanation(
        self,
        account_id: str,
        risk_score: float,
        risk_level: str,
        aml_patterns: List[Dict],
        recommendations: List[Dict]
    ) -> tuple[str, int]:
        """
        Generate explanation using IBM watsonx.ai Granite model.
        
        Returns:
            Tuple of (explanation_text, tokens_used)
        """
        # Build prompt
        prompt = self._build_prompt(
            account_id, risk_score, risk_level, aml_patterns, recommendations
        )

        # Call the model using chat API
        messages = [{"role": "user", "content": prompt}]
        response = self.model.chat(messages=messages)

        # Extract text and tokens
        tokens_used = 0
        try:
            explanation = response['choices'][0]['message']['content'].strip()
            tokens_used = response.get('usage', {}).get('total_tokens', 0)
        except (KeyError, IndexError, TypeError):
            explanation = str(response)

        return explanation, tokens_used
    
    def _build_prompt(
        self,
        account_id: str,
        risk_score: float,
        risk_level: str,
        aml_patterns: List[Dict],
        recommendations: List[Dict]
    ) -> str:
        """Build the prompt for the LLM."""
        
        # Format AML patterns
        patterns_text = "None detected"
        if aml_patterns:
            patterns_list = []
            for pattern in aml_patterns:
                pattern_type = pattern.get('pattern_type', 'unknown')
                severity = pattern.get('severity', 'unknown')
                description = pattern.get('description', '')
                patterns_list.append(f"- {pattern_type.upper()} (severity: {severity}): {description}")
            patterns_text = "\n".join(patterns_list)
        
        # Format recommendations
        recommendations_text = "No specific actions required"
        if recommendations:
            rec_list = []
            for rec in recommendations:
                action = rec.get('action', 'UNKNOWN')
                priority = rec.get('priority', 'unknown')
                description = rec.get('description', rec.get('reason', ''))
                rec_list.append(f"- {action} (priority: {priority}): {description}")
            recommendations_text = "\n".join(rec_list)
        
        prompt = f"""You are a financial compliance expert. Explain the following risk assessment results to a compliance officer in clear, professional English.

Account ID: {account_id}
Risk Score: {risk_score:.4f} (scale: 0.0-1.0)
Risk Level: {risk_level.upper()}

Detected AML Patterns:
{patterns_text}

Recommended Actions:
{recommendations_text}

Provide a concise explanation (3-5 sentences) that:
1. Summarizes the overall risk level and what it means
2. Highlights the most critical findings or patterns
3. Explains why the recommended actions are necessary
4. Uses professional but accessible language for compliance officers

Explanation:"""
        
        return prompt
    
    def _generate_fallback_explanation(
        self,
        account_id: str,
        risk_score: float,
        risk_level: str,
        aml_patterns: List[Dict],
        recommendations: List[Dict]
    ) -> str:
        """
        Generate rule-based explanation when LLM is unavailable or fails.
        
        Returns:
            Explanation text
        """
        # Risk level descriptions
        risk_descriptions = {
            'critical': 'This account exhibits critical risk indicators requiring immediate attention. The risk score of {score:.2f} suggests a high probability of illicit activity.',
            'high': 'This account shows high-risk characteristics that warrant enhanced monitoring. The risk score of {score:.2f} indicates significant suspicious activity patterns.',
            'medium': 'This account demonstrates medium-level risk factors. The risk score of {score:.2f} suggests some concerning patterns that require increased oversight.',
            'low': 'This account presents low risk with minimal suspicious indicators. The risk score of {score:.2f} indicates generally normal activity patterns.',
            'minimal': 'This account shows minimal risk with no significant red flags. The risk score of {score:.2f} reflects standard, expected transaction behavior.'
        }
        
        # Start with risk level description
        explanation_parts = [
            risk_descriptions.get(
                risk_level,
                f'Account {account_id} has a risk score of {risk_score:.2f}.'
            ).format(score=risk_score)
        ]
        
        # Add AML patterns if present
        if aml_patterns:
            high_severity_patterns = [p for p in aml_patterns if p.get('severity') == 'high']
            if high_severity_patterns:
                pattern_types = [p.get('pattern_type', 'unknown') for p in high_severity_patterns]
                explanation_parts.append(
                    f"Critical findings include {', '.join(pattern_types)} patterns, which are strong indicators of potential money laundering activity."
                )
            else:
                pattern_types = [p.get('pattern_type', 'unknown') for p in aml_patterns[:2]]
                explanation_parts.append(
                    f"The analysis detected {', '.join(pattern_types)} patterns that require further investigation."
                )
        
        # Add recommendations context
        if recommendations:
            high_priority_recs = [r for r in recommendations if r.get('priority') in ['critical', 'high']]
            if high_priority_recs:
                actions = [r.get('action', 'REVIEW') for r in high_priority_recs[:2]]
                explanation_parts.append(
                    f"Immediate actions recommended include {' and '.join(actions)} to mitigate identified risks and ensure regulatory compliance."
                )
            else:
                explanation_parts.append(
                    "Standard monitoring procedures should be maintained with periodic reviews to ensure continued compliance."
                )
        else:
            if risk_level in ['critical', 'high']:
                explanation_parts.append(
                    "Enhanced due diligence and immediate review by the compliance team is strongly recommended."
                )
        
        return " ".join(explanation_parts)


# Made with Bob