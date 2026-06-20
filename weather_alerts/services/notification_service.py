import logging
from weather_alerts.config.settings import settings
from weather_alerts.models.alert import Alert
from weather_alerts.models.user import User
from weather_alerts.services.aws_factory import get_sns_client

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.sns = get_sns_client()
        self.topic_arn = settings.sns_topic_arn

    def send_alert(self, user: User, alert: Alert):
        if not self.topic_arn:
            logger.warning("SNS Topic ARN not configured. Skipping notification.")
            return

        message = (
            f"Weather Alert for {user.location}:\n"
            f"Type: {alert.alert_type.value}\n"
            f"Details: {alert.message}\n"
            f"Temp: {alert.temperature}°C\n"
        )

        try:
            self.sns.publish(
                TopicArn=self.topic_arn,
                Message=message,
                Subject=f"Weather Alert: {alert.alert_type.value}",
                MessageAttributes={
                    "email": {
                        "DataType": "String",
                        "StringValue": user.email
                    }
                }
            )
            logger.info(f"Sent SNS notification for alert {alert.alert_id}")
        except Exception as e:
            logger.error(f"Failed to send SNS notification: {e}")