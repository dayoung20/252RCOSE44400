import asyncio
import aiohttp
import random
from faker import Faker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_URL = os.environ.get("API_URL", "")
TOTAL_REQUESTS = 30  

fake = Faker("en_US")

# Expand review template data for variety
POSITIVE_ADJECTIVES = ["fantastic", "excellent", "great", "amazing", "good"]
NEGATIVE_ADJECTIVES = ["terrible", "bad", "poor", "useless", "awful"]
NEUTRAL_ADJECTIVES = ["average", "okay", "fine", "decent", "acceptable", "so-so"]

PRODUCTS = ["widget", "gadget", "app", "service", "tool"]


def generate_review_data():
    """Generates a random review payload with realistic sentiment distribution."""

    # Generate random float (0.0 to 1.0) to determine sentiment
    rand_val = random.random()

    if rand_val < 0.4:
        adj = random.choice(POSITIVE_ADJECTIVES)
        review_text = f"The {random.choice(PRODUCTS)} is {adj}. {fake.sentence()}"
    elif rand_val < 0.7:
        adj = random.choice(NEGATIVE_ADJECTIVES)
        review_text = f"The {random.choice(PRODUCTS)} was {adj}. {fake.sentence()}"
    else:
        adj = random.choice(NEUTRAL_ADJECTIVES)
        templates = [
            f"The {random.choice(PRODUCTS)} is {adj}.",
            f"It's {adj}, but not perfect.",
            f"Just an {adj} experience.",
            f"The {random.choice(PRODUCTS)} works as expected.",
        ]
        review_text = f"{random.choice(templates)} {fake.sentence()}"

    return {
        "user_name": fake.name(),
        "review": review_text,
        "timestamp": datetime.now().isoformat(),
    }


async def send_review(session, sem):
    """Sends a single review request asynchronously."""
    data = generate_review_data()
    try:
        async with sem:
            async with session.post(API_URL, json=data) as response:
                print(f"Status: {response.status} | {data['review']}")
    except Exception as e:
        print(f"Error sending request: {e}")


async def main():
    """Main function to handle concurrent requests."""
    async with aiohttp.ClientSession() as session:
        # Create a list of tasks
        sem = asyncio.Semaphore(5)
        tasks = [send_review(session, sem) for _ in range(TOTAL_REQUESTS)]
        # Execute tasks concurrently
        await asyncio.gather(*tasks)


start = datetime.now()
asyncio.run(main())
print("Execution time:", datetime.now() - start)
