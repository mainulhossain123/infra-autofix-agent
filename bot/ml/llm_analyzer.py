"""
LLM-Powered Incident Analyzer using Ollama

Provides AI-generated insights for incidents:
- Root cause analysis
- Remediation suggestions
- Natural language explanations
- Historical pattern recognition
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)


class LLMAnalyzer:
    """Ollama-based LLM for incident analysis"""
    
    def __init__(self, ollama_url: str = "http://ollama:11434", model: str = "llama3.2:3b"):
        """
        Initialize LLM Analyzer
        
        Args:
            ollama_url: Ollama API endpoint
            model: Model name (default: llama3.2:3b)
        """
        self.ollama_url = ollama_url
        self.model = model
        self.is_available = self._check_availability()
    
    def _check_availability(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                if self.model in model_names:
                    logger.info(f"Ollama available with model {self.model}")
                    return True
                else:
                    logger.warning(f"Model {self.model} not found. Available: {model_names}")
                    return False
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    def analyze_incident(self, incident: Dict) -> Dict:
        """
        Analyze incident and provide AI insights
        
        Args:
            incident: Incident dictionary with type, severity, details
            
        Returns:
            Analysis with root cause, suggestions, explanation
        """
        if not self.is_available:
            return {
                'error': 'LLM service not available',
                'root_cause': 'Unknown - LLM offline',
                'suggestions': ['Check Ollama service status'],
                'explanation': 'AI analysis unavailable'
            }
        
        # Build prompt
        prompt = self._build_incident_prompt(incident)
        
        # Query LLM
        try:
            response = self._query_ollama(prompt)
            analysis = self._parse_response(response)
            
            return {
                'root_cause': analysis.get('root_cause', 'Unknown'),
                'suggestions': analysis.get('suggestions', []),
                'explanation': analysis.get('explanation', ''),
                'confidence': analysis.get('confidence', 'medium'),
                'analyzed_at': datetime.now().isoformat(),
                'model': self.model
            }
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}", exc_info=True)
            return {
                'error': str(e),
                'root_cause': 'Analysis failed',
                'suggestions': ['Review logs manually'],
                'explanation': f'Error during analysis: {e}'
            }
    
    def _build_incident_prompt(self, incident: Dict) -> str:
        """Build structured prompt for LLM"""
        incident_type = incident.get('type', 'unknown')
        severity = incident.get('severity', 'UNKNOWN')
        details = incident.get('details', {})
        
        prompt = f"""You are an expert infrastructure monitoring analyst. Analyze this incident and provide insights.

INCIDENT DETAILS:
- Type: {incident_type}
- Severity: {severity}
- Details: {json.dumps(details, indent=2)}

Provide analysis in JSON format:
{{
  "root_cause": "Brief explanation of the root cause",
  "suggestions": ["Specific action 1", "Specific action 2", "Specific action 3"],
  "explanation": "Detailed technical explanation",
  "confidence": "high/medium/low"
}}

Focus on:
1. Identifying the root cause
2. Providing actionable remediation steps
3. Explaining technical context
4. Rating confidence in the analysis

Response (JSON only):"""
        
        return prompt
    
    def _query_ollama(self, prompt: str, max_tokens: int = 500) -> str:
        """Query Ollama API"""
        url = f"{self.ollama_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,  # Lower = more deterministic
                "top_p": 0.9,
                "num_predict": max_tokens
            }
        }
        
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result.get('response', '')
    
    def _parse_response(self, response: str) -> Dict:
        """Parse LLM response into structured data"""
        try:
            # Try to extract JSON from response
            # LLM might add extra text, so find JSON block
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = response[start:end]
                parsed = json.loads(json_str)
                return parsed
            else:
                # Fallback: treat as plain text
                return {
                    'root_cause': 'Unable to parse structured response',
                    'suggestions': ['Review raw LLM output'],
                    'explanation': response[:500],
                    'confidence': 'low'
                }
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON from LLM response: {response[:200]}")
            return {
                'root_cause': 'Response parsing failed',
                'suggestions': ['Check LLM output format'],
                'explanation': response[:500],
                'confidence': 'low'
            }
    
    def analyze_metrics_pattern(self, metrics_history: List[Dict]) -> Dict:
        """
        Analyze historical metrics pattern
        
        Args:
            metrics_history: List of metric dictionaries
            
        Returns:
            Pattern analysis
        """
        if not self.is_available:
            return {'error': 'LLM service not available'}
        
        # Summarize metrics
        summary = self._summarize_metrics(metrics_history)
        
        prompt = f"""Analyze these infrastructure metrics and identify patterns or anomalies.

METRICS SUMMARY:
{json.dumps(summary, indent=2)}

Provide analysis in JSON format:
{{
  "patterns": ["Pattern 1", "Pattern 2"],
  "anomalies": ["Anomaly 1", "Anomaly 2"],
  "trends": ["Trend 1", "Trend 2"],
  "recommendations": ["Recommendation 1", "Recommendation 2"]
}}

Response (JSON only):"""
        
        try:
            response = self._query_ollama(prompt, max_tokens=400)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"Metrics pattern analysis failed: {e}")
            return {'error': str(e)}
    
    def _summarize_metrics(self, metrics: List[Dict]) -> Dict:
        """Summarize metrics for LLM analysis"""
        if not metrics:
            return {}
        
        # Calculate statistics
        cpu_values = [m.get('cpu_usage_percent', 0) for m in metrics]
        memory_values = [m.get('memory_usage_mb', 0) for m in metrics]
        error_rates = [m.get('error_rate', 0) for m in metrics]
        
        return {
            'sample_count': len(metrics),
            'time_range': f"{metrics[0].get('timestamp')} to {metrics[-1].get('timestamp')}",
            'cpu': {
                'min': min(cpu_values),
                'max': max(cpu_values),
                'avg': sum(cpu_values) / len(cpu_values)
            },
            'memory': {
                'min': min(memory_values),
                'max': max(memory_values),
                'avg': sum(memory_values) / len(memory_values)
            },
            'errors': {
                'min': min(error_rates),
                'max': max(error_rates),
                'avg': sum(error_rates) / len(error_rates)
            }
        }
    
    def suggest_remediation(self, incident_type: str, context: Dict) -> List[str]:
        """
        Get remediation suggestions for specific incident type
        
        Args:
            incident_type: Type of incident
            context: Additional context
            
        Returns:
            List of remediation suggestions
        """
        if not self.is_available:
            return ['LLM service unavailable - use default remediations']
        
        prompt = f"""As an infrastructure expert, suggest specific remediation actions.

INCIDENT TYPE: {incident_type}
CONTEXT: {json.dumps(context, indent=2)}

Provide 3-5 specific, actionable remediation steps in JSON format:
{{
  "immediate_actions": ["Action 1", "Action 2"],
  "preventive_measures": ["Prevention 1", "Prevention 2"],
  "monitoring_adjustments": ["Adjustment 1"]
}}

Response (JSON only):"""
        
        try:
            response = self._query_ollama(prompt, max_tokens=300)
            parsed = self._parse_response(response)
            
            # Flatten all suggestions
            suggestions = []
            suggestions.extend(parsed.get('immediate_actions', []))
            suggestions.extend(parsed.get('preventive_measures', []))
            suggestions.extend(parsed.get('monitoring_adjustments', []))
            
            return suggestions[:5]  # Return top 5
        except Exception as e:
            logger.error(f"Remediation suggestion failed: {e}")
            return ['Check system logs', 'Review metrics', 'Contact support']
    
    def generate_incident_report(self, incident: Dict, analysis: Dict, 
                                 remediation_actions: List[Dict]) -> str:
        """
        Generate natural language incident report
        
        Args:
            incident: Incident data
            analysis: LLM analysis
            remediation_actions: List of remediation actions taken
            
        Returns:
            Formatted report string
        """
        if not self.is_available:
            return self._generate_fallback_report(incident, remediation_actions)
        
        prompt = f"""Generate a concise incident report for stakeholders.

INCIDENT:
{json.dumps(incident, indent=2)}

ANALYSIS:
{json.dumps(analysis, indent=2)}

REMEDIATION ACTIONS:
{json.dumps(remediation_actions, indent=2)}

Generate a 3-paragraph executive summary:
1. What happened (incident description)
2. Why it happened (root cause)
3. What was done (remediation and outcome)

Keep it non-technical and concise (max 200 words).

Report:"""
        
        try:
            response = self._query_ollama(prompt, max_tokens=300)
            return response.strip()
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return self._generate_fallback_report(incident, remediation_actions)
    
    def _generate_fallback_report(self, incident: Dict, actions: List[Dict]) -> str:
        """Generate basic report without LLM"""
        report = f"""Incident Report

Type: {incident.get('type', 'Unknown')}
Severity: {incident.get('severity', 'Unknown')}
Time: {incident.get('timestamp', 'Unknown')}

Description:
{incident.get('details', {})}

Remediation Actions Taken:
"""
        for i, action in enumerate(actions, 1):
            report += f"{i}. {action.get('action_type', 'Unknown')} - "
            report += "Success" if action.get('success') else "Failed"
            report += "\n"
        
        return report


def create_default_analyzer() -> LLMAnalyzer:
    """Create analyzer with default settings"""
    return LLMAnalyzer()
