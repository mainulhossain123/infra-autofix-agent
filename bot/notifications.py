"""
Notification handlers for Slack, PagerDuty, and console logging.
"""
import os
import logging
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)


class NotificationHandler:
    """Base class for notification handlers"""
    
    def send(self, message: str, severity: str = 'INFO', metadata: Dict[str, Any] = None):
        """Send notification"""
        raise NotImplementedError


class SlackNotificationHandler(NotificationHandler):
    """Send notifications to Slack via webhook"""
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.enabled = bool(webhook_url and webhook_url != 'YOUR_WEBHOOK_URL')
    
    def send(self, message: str, severity: str = 'INFO', metadata: Dict[str, Any] = None):
        """Send message to Slack"""
        if not self.enabled:
            logger.debug("Slack notifications disabled (no webhook configured)")
            return False
        
        # Choose emoji based on severity
        emoji_map = {
            'CRITICAL': ':red_circle:',
            'WARNING': ':warning:',
            'INFO': ':information_source:',
            'SUCCESS': ':white_check_mark:'
        }
        emoji = emoji_map.get(severity, ':bell:')
        
        # Format message
        formatted_message = f"{emoji} *{severity}* - {message}"
        
        # Add metadata if provided
        if metadata:
            formatted_message += "\n```" + str(metadata) + "```"
        
        payload = {
            'text': formatted_message,
            'username': 'Auto-Remediation Bot',
            'icon_emoji': ':robot_face:'
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=5)
            if response.status_code == 200:
                logger.debug(f"Slack notification sent: {message}")
                return True
            else:
                logger.warning(f"Slack notification failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Slack notification exception: {e}")
            return False


class ConsoleNotificationHandler(NotificationHandler):
    """Log notifications to console"""
    
    def send(self, message: str, severity: str = 'INFO', metadata: Dict[str, Any] = None):
        """Log message to console"""
        log_func = {
            'CRITICAL': logger.critical,
            'WARNING': logger.warning,
            'INFO': logger.info,
            'SUCCESS': logger.info
        }.get(severity, logger.info)
        
        log_message = f"[NOTIFICATION] {message}"
        if metadata:
            log_message += f" | Metadata: {metadata}"
        
        log_func(log_message)
        return True


class NotificationManager:
    """Manages multiple notification handlers"""
    
    def __init__(self, slack_webhook: str = None, enable_console: bool = True):
        self.handlers = []
        
        # Add console handler
        if enable_console:
            self.handlers.append(ConsoleNotificationHandler())
        
        # Add Slack handler if webhook provided
        if slack_webhook:
            slack_handler = SlackNotificationHandler(slack_webhook)
            if slack_handler.enabled:
                self.handlers.append(slack_handler)
                logger.info("Slack notifications enabled")
    
    def notify(self, message: str, severity: str = 'INFO', metadata: Dict[str, Any] = None):
        """Send notification through all handlers"""
        success_count = 0
        
        for handler in self.handlers:
            try:
                if handler.send(message, severity, metadata):
                    success_count += 1
            except Exception as e:
                logger.error(f"Notification handler error: {e}")
        
        return success_count > 0
    
    def notify_incident_detected(self, incident: Dict[str, Any], service: str):
        """Notify about detected incident"""
        incident_type = incident.get('type', 'unknown')
        severity = incident.get('severity', 'INFO')
        details = incident.get('details', {})
        
        message = f"Incident detected on `{service}`: **{incident_type}** ({severity})"
        self.notify(message, severity, details)
    
    def notify_remediation_started(self, action_type: str, target: str, reason: str):
        """Notify about remediation action starting"""
        message = f"Starting remediation: `{action_type}` on `{target}` - Reason: {reason}"
        self.notify(message, 'INFO')
    
    def notify_remediation_success(self, action_type: str, target: str, execution_time_ms: int):
        """Notify about successful remediation"""
        message = (
            f"✅ Remediation successful: `{action_type}` on `{target}` "
            f"(completed in {execution_time_ms}ms)"
        )
        self.notify(message, 'SUCCESS')
    
    def notify_remediation_failure(self, action_type: str, target: str, error: str):
        """Notify about failed remediation"""
        message = f"❌ Remediation failed: `{action_type}` on `{target}` - Error: {error}"
        self.notify(message, 'CRITICAL', {'error': error})
    
    def notify_circuit_breaker_opened(self, service: str, reason: str):
        """Notify about circuit breaker opening"""
        message = f"🚫 Circuit breaker OPENED for `{service}` - {reason}"
        self.notify(message, 'WARNING', {'reason': reason})
    
    def notify_escalation(self, service: str, reason: str):
        """Notify about incident escalation"""
        message = (
            f"🚨 ESCALATION REQUIRED for `{service}` - "
            f"Auto-remediation exhausted. Manual intervention needed. Reason: {reason}"
        )
        self.notify(message, 'CRITICAL', {'escalation_reason': reason})
