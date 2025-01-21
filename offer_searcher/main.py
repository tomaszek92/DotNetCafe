import asyncio
import uuid
from openai import OpenAI
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig
from supabase import create_client, Client
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, SearchRequest
import re
import os
import requests
import xml.etree.ElementTree as ET
import random

# Set your OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")

# Set your Supabase URL and API key
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Qdrant client setup
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"), 
    api_key=os.getenv("QDRANT_API_KEY"),
)

async def process_urls(urls: str, save_markdown: bool = False):
    browser_config = BrowserConfig(
        headless=True,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )

    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        session_id = "session1"
        counter = 0  # Initialize the counter
        for url in urls:
            crawl_config = CrawlerRunConfig(
                css_selector=".MuiBox-root.css-1kzbnue, .MuiBox-root.css-17h1y7k, .MuiBox-root.css-qal8sw",
                cache_mode=CacheMode.BYPASS
            )
            result = await crawler.arun(
                url=url,
                config=crawl_config,
                session_id=session_id
            )
            if result.success:
                counter += 1  # Increment the counter on successful crawl
                print(f"Successfully crawled: {url} (Total processed: {counter})")
                if save_markdown:
                    markdown_path = create_markdown_path(url)
                    with open(markdown_path, "w") as file:
                        file.write(result.markdown)
                    print(f"Result saved to {markdown_path}")
                embedding = get_embedding(result.markdown)
                save_to_qdrant(embedding, url)
            else:
                print(f"Failed: {url} - Error: {result.error_message}")
    finally:
        await crawler.close()

def create_markdown_path(url: str) -> str:
    # Create a safe file name from the URL
    safe_file_name = re.sub(r'\W+', '_', url) + ".md"
    markdown_dir = "markdowns"
    os.makedirs(markdown_dir, exist_ok=True)
    return os.path.join(markdown_dir, safe_file_name)

def get_embedding(text: str):
    client = OpenAI(api_key=openai_api_key)
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding

def save_to_supabase(url: str, embedding: list):
    supabase: Client = create_client(supabase_url, supabase_key)
    data = {
        "url": url,
        "embedding": embedding
    }
    response = supabase.table("job_offers").insert(data).execute()
    print("Data inserted into Supabase")
    return response.data[0]["id"]

def save_to_qdrant(vector: list, url: str):
    qdrant_client.upsert(
        collection_name="job_offers",
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"url": url}
            )
        ]
    )
    print("Data inserted into Qdrant")

async def search_matching_results(prompt: str):
    # Get the embedding for the prompt
    prompt_embedding = get_embedding(prompt)
    
    # Search for similar embeddings in Qdrant
    search_result = qdrant_client.search(
        collection_name="job_offers",
        query_vector=prompt_embedding,
        limit=20
    )
    
    # Print or process the matching results
    for result in search_result:
        print(f"Match: {result.payload['url']} with score {result.score}")

    # Filter results with score >= 0.5
    filtered_results = [result for result in search_result if result.score >= 0.5]
    
    # Collect markdown contents for filtered results
    markdown_contents = []
    for result in filtered_results:
        url = result.payload['url']
        markdown_path = create_markdown_path(url)
        try:
            with open(markdown_path, "r") as file:
                markdown_content = file.read()
                markdown_contents.append((url, markdown_content))
        except FileNotFoundError:
            print(f"Markdown file not found for URL: {url}")
    
    # Create a new prompt for ChatGPT
    if markdown_contents:
        chatgpt_prompt = "Given the following job descriptions, select the best match for the prompt: '{}'.\n\n".format(prompt)
        for url, content in markdown_contents:
            chatgpt_prompt += f"URL: {url}\nDescription:\n{content}\n\n"
        
        # Send the prompt to ChatGPT
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a the recruiter assistant. You need to find the best match."},
                {"role": "user", "content": chatgpt_prompt}
            ]
        )
        
        # Print the best URL as determined by ChatGPT
        print(f"Best URL according to ChatGPT: {response.choices[0].message.content}")
    else:
        print("No suitable matches found.")

def fetch_job_offer_urls() -> list:
    response = requests.get("https://justjoin.it/sitemaps/active-jobs/part0.xml")
    response.raise_for_status()
    root = ET.fromstring(response.content)
    urls = [url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text for url in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url')]
    
    # Randomly select 100 URLs
    if len(urls) > 100:
        urls = random.sample(urls, 100)
    
    return urls

async def main():
    job_offer_urls = fetch_job_offer_urls()
    await process_urls(job_offer_urls, save_markdown=True)

    await search_matching_results(prompt=".net software developer in Warsaw")

if __name__ == "__main__":
    asyncio.run(main())