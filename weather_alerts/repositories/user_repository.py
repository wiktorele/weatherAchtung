from typing import List, Optional
from boto3.dynamodb.conditions import Key
from weather_alerts.config.settings import settings
from weather_alerts.models.user import User
from weather_alerts.services.aws_factory import get_aws_client


class UserRepository:
    def __init__(self):
        self.dynamodb = get_aws_client("dynamodb")
        self.table = self.dynamodb.Table(settings.dynamodb_table_users)

    def create_user(self, user: User) -> User:
        # Convert Pydantic model to dict, handling datetimes if necessary
        item = user.model_dump()
        item["created_at"] = user.created_at.isoformat()
        if user.last_alert:
            item["last_alert"] = user.last_alert.isoformat()

        self.table.put_item(Item=item)
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        response = self.table.get_item(Key={"user_id": user_id})
        item = response.get("Item")
        if not item:
            return None
        return User(**item)

    def get_user_by_email(self, email: str) -> Optional[User]:
        # Scan is inefficient, ideally use a Global Secondary Index (GSI) on email
        response = self.table.scan(
            FilterExpression=Key("email").eq(email)
        )
        items = response.get("Items", [])
        if items:
            return User(**items[0])
        return None

    def list_users(self, limit: int = 100) -> List[User]:
        # Scan is inefficient for large tables, acceptable for MVP
        response = self.table.scan(Limit=limit)
        return [User(**item) for item in response.get("Items", [])]

    def update_user(self, user: User) -> User:
        return self.create_user(user)  # PutItem overwrites

    def delete_user(self, user_id: str) -> None:
        self.table.delete_item(Key={"user_id": user_id})