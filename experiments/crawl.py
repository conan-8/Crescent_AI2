import os
import asyncio
from crawl4ai import *
import chromadb
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.crescentschool.org/family-handbook/general-information",
        )
        print(result.markdown.raw_markdown)
        print(result.markdown.fit_markdown)

if __name__ == "__main__":
    asyncio.run(main())