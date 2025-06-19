import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter

async def crawl_imdb():
    print("🎬 Starting IMDb Top Movies Crawler...")
    
    # Simple browser config
    browser_config = BrowserConfig(
        headless=True,
        user_agent_mode="random",
        ignore_https_errors=True
    )

    # Simple crawler config
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=1,
            max_pages=50,
            filter_chain=FilterChain([
                URLPatternFilter(patterns=["*/title/*"])
            ])
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        wait_until="domcontentloaded",
        page_timeout=60000,
        magic=True,
        verbose=True,
        stream=True
    )

    movies = []
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            async for result in await crawler.arun("https://www.imdb.com/chart/top/", config=config):
                if result.success:
                    try:
                        # Extract movie data
                        movie = {
                            "title": result.extract_text("h1[data-testid='hero-title-block__title']") or "Unknown Title",
                            "year": result.extract_text("a[href*='releaseinfo']") or "Unknown Year",
                            "rating": result.extract_text("span[data-testid='hero-rating-bar__aggregate-rating__score']") or "No Rating",
                            "plot": result.extract_text("span[data-testid='plot-xl']") or "No Plot Available",
                            "actors": []
                        }

                        # Get actors
                        actor_elements = result.extract_all("a[data-testid='title-cast-item__actor']")
                        for actor in actor_elements:
                            if actor:
                                movie["actors"].append({
                                    "name": actor.get("text", "Unknown Actor"),
                                    "profile_url": actor.get("href", "")
                                })

                        movies.append(movie)

                        # Print immediate results
                        print("\n" + "="*50)
                        print(f"🎬 Movie: {movie['title']} ({movie['year']})")
                        print(f"⭐ Rating: {movie['rating']}")
                        print(f"📝 Plot: {movie['plot'][:150]}...")
                        print("👥 Cast:")
                        for actor in movie["actors"]:
                            print(f"  - {actor['name']}")
                        print("="*50 + "\n")

                        # Small delay between requests
                        await asyncio.sleep(2)

                    except Exception as e:
                        print(f"Error extracting data: {str(e)}")

    except Exception as e:
        print(f"Crawler error: {str(e)}")

    print(f"\n📊 Successfully processed {len(movies)} movies")
    return movies

if __name__ == "__main__":
    movies = asyncio.run(crawl_imdb())