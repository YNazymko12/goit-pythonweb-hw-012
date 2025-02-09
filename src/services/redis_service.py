"""Redis caching service.

This module provides Redis caching functionality for the application,
particularly for caching user data to improve authentication performance.
"""

import json
from typing import Optional
import redis
from src.conf.config import settings
from src.database.models import User


class RedisService:
    """Service for handling Redis caching operations."""
    
    _instance = None
    
    def __new__(cls):
        """Implement singleton pattern for Redis connection."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True
            )
        return cls._instance

    def get_user_from_cache(self, user_id: int) -> Optional[User]:
        """Retrieve user from Redis cache.
        
        Args:
            user_id (int): ID of the user to retrieve
            
        Returns:
            Optional[User]: Cached user if found, None otherwise
        """
        try:
            user_data = self.redis_client.get(f"user:{user_id}")
            if user_data:
                user_dict = json.loads(user_data)
                return User(**user_dict)
        except (json.JSONDecodeError, redis.RedisError) as e:
            print(f"Redis error: {str(e)}")
        return None

    def cache_user(self, user: User) -> None:
        """Store user data in Redis cache.
        
        Args:
            user (User): User object to cache
        """
        try:
            user_dict = {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "confirmed": user.confirmed,
                "avatar": user.avatar,
                "created_at": str(user.created_at),
                "refresh_token": user.refresh_token
            }
            self.redis_client.setex(
                f"user:{user.id}",
                settings.REDIS_USER_CACHE_TTL,
                json.dumps(user_dict)
            )
        except redis.RedisError as e:
            print(f"Redis error: {str(e)}")

    def invalidate_user_cache(self, user_id: int) -> None:
        """Remove user data from cache.
        
        Args:
            user_id (int): ID of the user to remove from cache
        """
        try:
            self.redis_client.delete(f"user:{user_id}")
        except redis.RedisError as e:
            print(f"Redis error: {str(e)}")


# Create a global instance
redis_service = RedisService()
