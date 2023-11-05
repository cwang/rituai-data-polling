import json
import os
from asyncio import get_event_loop
from datetime import datetime

import feedparser
import requests
from dotenv import load_dotenv
from loguru import logger
from motor import motor_asyncio
from pydantic import BaseModel

load_dotenv()


class IncomingDataItem(BaseModel):
    email_recipient: str
    data_type: str
    received_at: datetime | None = datetime.utcnow()
    extracted_content: str | None = None
    raw_content: str | None = None
    processed_at: datetime | None = None


client = motor_asyncio.AsyncIOMotorClient(os.getenv("MONGODB_URL"))
user_collection = client.get_default_database().get_collection("user-profiles")
data_collection = client.get_default_database().get_collection("incoming-data")


async def _parse_feed(email_recipient: str, feed_url: str):
    raw_content = requests.get(feed_url).text
    feed = feedparser.parse(raw_content)
    extracted_content = json.dumps(feed.entries)

    data = IncomingDataItem(
        email_recipient=email_recipient,
        data_type="feed",
        extracted_content=extracted_content,
        raw_content=raw_content,
    )
    return (await data_collection.insert_one(data.model_dump())).inserted_id


async def fetch():
    batch_size = 1000
    users = await user_collection.find().to_list(batch_size)
    for user in users:
        logger.info("Found user {}", user)
        await poll(user["username"], user["feeds"])


async def poll(email_recipient: str, feed_urls: list[str]):
    result = []
    for feed_url in feed_urls:
        result.append(await _parse_feed(email_recipient, feed_url))
    return result


if __name__ == "__main__":
    logger.info("Starting")
    loop = get_event_loop()
    loop.run_until_complete(fetch())
    logger.info("Finished")
