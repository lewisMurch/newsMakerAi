import requests
from bs4 import BeautifulSoup

bbc_url = 'https://www.bbc.co.uk/'
fox_url = 'https://www.foxnews.com/'
sky_url = 'https://news.sky.com/uk'
ind_url = 'https://www.independent.co.uk/'
stime_url = 'https://www.thetimes.com/'

# Function to get all news article links from a homepage
def scrape_news_articles(url):
    try:
        # Send a request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all <a> tags that contain href attribute
        links = soup.find_all('a', href=True)
        
        news_links = set()  # Using a set to avoid duplicates
        if url == bbc_url:
            # Filter the links to only include news articles (assuming they contain '/news/' in the href)
            filtered_links = [link['href'] for link in links if '/news/articles' in link['href'] and '#' not in link['href']]
            
            # Ensure the links are complete URLs
            for link in filtered_links:
                full_link = link if link.startswith('http') else 'https://www.bbc.co.uk' + link
                news_links.add(full_link)

        elif url == fox_url:
            filtered_links = [link['href'] for link in links if '/politics/' in link['href'] and '/category/' not in link['href'] and '/cartoons-slideshow' not in link['href']]
            
            # Ensure the links are complete URLs
            for link in filtered_links:

                if link.startswith('https'):
                    full_link = link
                elif link.startswith('//'):
                    full_link = 'https://' + link[2:]

                news_links.add(full_link)

        elif url == sky_url:  
            filtered_links = [link['href'] for link in links if '/story/' in link['href']]
            
            # Ensure the links are complete URLs
            for link in filtered_links:
                full_link = link if link.startswith('http') else 'https://news.sky.com' + link
                news_links.add(full_link)

        elif url == ind_url:  
            filtered_links = [link['href'] for link in links if (('/news/' in link['href'] or '/climate-change/' in link['href'] or '/asia/' in link['href']) and link['href'].endswith('.html'))]

            # Ensure the links are complete URLs
            for link in filtered_links:
                full_link = link if link.startswith('http') else 'https://www.independent.co.uk' + link
                news_links.add(full_link)

        elif url == stime_url:
            filtered_links = [link['href'] for link in links if '/article/' in link['href'] and '/football/' not in link['href'] and '/sport/' not in link['href'] and '/business-money/' not in link['href'] and '/corrections-and-' not in link['href'] and '/tv-guide' not in link['href'] and '/life-style/' not in link['href'] and '/culture/' not in link['href'] and '/comment/' not in link['href'] and '/magazines/' not in link['href']  and '/journalism-license' not in link['href'] and '/puzzles/' not in link['href']]
            
            # Ensure the links are complete URLs
            for link in filtered_links:
                full_link = link if link.startswith('http') else 'https://www.thetimes.com' + link
                news_links.add(full_link)

        return list(news_links)
    
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return []


def run(url, limit=10):
    news_article_links = scrape_news_articles(url)
    news_article_links = news_article_links[:limit]
    return news_article_links


# #For testing new additions
# x = scrape_news_articles(stime_url)
# x = x[:10]
# for i in x:
#     print(i)