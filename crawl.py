import asyncio
from crawl4ai import *
import chromadb
from google import genai

client = genai.Client(api_key="AIzaSyCaJ7me7Ans9STNva8-YrNUHf0dPBj6HfI")

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.crescentschool.org/family-handbook/general-information",
        )
        print(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())