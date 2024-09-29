import requests
from bs4 import BeautifulSoup
import asyncio
import aiohttp

async def scrape_wirecutter_reviews(keyword):
    print("Scraping wirecutter reviews")
    base_url = "https://www.nytimes.com/wirecutter/search/"
    search_url = f"{base_url}{keyword.replace(' ', '+')}"
    print("Search URL: ", search_url)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(search_url) as response:
            if response.status != 200:
                return f"Error: Unable to access the website. Status code: {response.status}"
            
            soup = BeautifulSoup(await response.text(), 'html.parser')
            
            results = []
            articles = soup.find_all('div', class_='product-tile')
            
            for article in articles:
                title = article.find('h3', class_='product-tile__title')
                snippet = article.find('p', class_='product-tile__excerpt')
                link = article.find('a', class_='product-tile__link')
                
                if title and snippet and link:
                    results.append({
                        'title': title.text.strip(),
                        'snippet': snippet.text.strip(),
                        'link': 'https://www.nytimes.com' + link['href']
                    })
            
            return results

async def get_wirecutter_reviews(keyword):

    print("Getting wirecutter reviews")
    reviews = await scrape_wirecutter_reviews(keyword)
    if isinstance(reviews, str):  # Error occurred
        return reviews
    
    formatted_reviews = "\n\n".join([
        f"Title: {review['title']}\nSnippet: {review['snippet']}\nLink: {review['link']}"
        for review in reviews
    ])
    
    return formatted_reviews if formatted_reviews else "No reviews found for the given keyword."

# Example usage:
# asyncio.run(get_wirecutter_reviews("headphones"))
