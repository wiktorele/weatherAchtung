from typing import List, Optional
from boto3.dynamodb.conditions import Key
from weather_alerts.config.settings import settings
from weather_alerts.models.alert import Alert
from weather_alerts.services.aws_factory import get_aws_client


class AlertRepository:
    def __init__(self):
        self.dynamodb = get_aws_client("dynamodb")
        self.table = self.dynamodb.Table(settings.dynamodb_table_alerts)

    def create_alert(self, alert: Alert) -> Alert:
        item = alert.model_dump()
        item["created_at"] = alert.created_at.isoformat()
        self.table.put_item(Item=item)
        return alert

    def list_alerts(self, user_id: Optional[str] = None, limit: int = 100) -> List[Alert]:
        if user_id:
            # Query using Partition Key (user_id)
            # Assumes Schema: PK=user_id, SK=created_at (optional but good practice)
            response = self.table.query(
                KeyConditionExpression=Key("user_id").eq(user_id),
                Limit=limit
            )
        else:
            response = self.table.scan(Limit=limit)

        return [Alert(**item) for item in response.get("Items", [])]

    def get_alert(self, alert_id: str) -> Optional[Alert]:
        # If table uses composite key (user_id, alert_id), getting by just alert_id
        # requires a Scan or a GSI. For MVP, we'll Scan.
        response = self.table.scan(
            FilterExpression=Key("alert_id").eq(alert_id)
        )
        items = response.get("Items", [])
        if items:
            return Alert(**items[0])
        return None