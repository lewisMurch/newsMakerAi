import article_scraper
from newsplease import NewsPlease
import json
import os
import requests
import openai
from openai.types import Completion, CompletionChoice, CompletionUsage
from pathlib import Path

# Define news URLs
bbc_url = article_scraper.bbc_url
fox_url = article_scraper.fox_url
sky_url = article_scraper.sky_url
ind_url = article_scraper.ind_url
stime_url = article_scraper.stime_url

article_amount = 2
ASMR_BBC_OFFSET = article_amount

# Fetch articles from sources
todays_articles_bbc = article_scraper.run(bbc_url, article_amount)
todays_articles_asmr_bbc = article_scraper.run(bbc_url, article_amount + ASMR_BBC_OFFSET)
todays_articles_fox = article_scraper.run(fox_url, article_amount)
todays_articles_sky = article_scraper.run(sky_url, article_amount)
todays_articles_ind = article_scraper.run(ind_url, article_amount)
todays_articles_stime = article_scraper.run(stime_url, article_amount)

openai.api_key = 'sk-proj-yourAPIkeyhere'


def historic_data_writer(headline, URL, image_link, politic):
    try:
        filepath = os.path.join('politics', politic, 'historic_stories', f'{politic}.json')
        if not os.path.exists(filepath):
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'a') as file:
            file.write(f"{headline}\n{URL}\n{image_link}\n{politic}\n\n")
            print("Story successfully written to historic_data.txt")
    except Exception as e:
        print(f"An error occurred while writing to the file, skipping this process. Error: {e}")

def get_json_length(politic, filename='news_info_to_render'):
    filepath = os.path.join('politics', politic, filename, f'{politic}.json')
    if not os.path.exists(filepath):
        os.makedirs(filepath, exist_ok=True)

    # Check if the file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} does not exist.")

    # Read and load the JSON data
    with open(filepath, 'r') as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            raise ValueError(f"File {filepath} is not a valid JSON or is empty.")

    # Determine the length of the data structure
    if isinstance(data, (list, dict)):
        length = len(data)
    else:
        raise TypeError(f"Data in {filepath} is not a list or dictionary.")

    return length

def clear_saved_articles_info(politic, filename='news_info_to_render'):
    filepath = os.path.join('politics', politic, filename, f'{politic}.json')

    # Check if the file exists
    if os.path.exists(filepath):
        # Open the file in write mode, which will clear its contents
        with open(filepath, 'w') as file:
            # Write an empty list to ensure the file is a valid JSON file
            json.dump([], file, indent=4)
        print(f"Cleared the contents of {filepath}")
    else:
        print(f"File {filepath} does not exist.")

def save_article_info(LLM_headline, URL, image_link, politic, filename='news_info_to_render', custom = False):
    # Create the full path for the JSON file
    if custom:
        full_filename = os.path.join('politics', politic, filename, f'{politic}_custom.json')
    else:
        full_filename = os.path.join('politics', politic, filename, f'{politic}.json')  


    # Ensure the directory exists
    if not os.path.exists(full_filename):
        os.makedirs(os.path.dirname(full_filename), exist_ok=True)

    # Check if the file exists and read its contents if it does
    if os.path.exists(full_filename):
        with open(full_filename, 'r') as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                # If the file is empty or corrupted, start with an empty list
                data = []
    else:
        # If the file does not exist, start with an empty list
        data = []

    # Append the new information to the list
    data.extend([LLM_headline, URL, image_link])

    # Write the updated data back to the file
    with open(full_filename, 'w') as file:
        json.dump(data, file, indent=4)

def summarise_text(text, politic, max_input_length=320, min_output_length=60):
    try:
        # Ensure the input text is within the maximum input length
        if len(text) > max_input_length:
            text = text[:max_input_length]

        # Create the prompt for summarization
        prompt = (f"summarize the following text so "
                  f"more than {min_output_length} characters, makes perfect sense, to provide a short news snippit with as much important info as possible. Make it Attention grabbing and give context. It must be suitable to be spoken by TTS, Include any unique/ intriguing Information:\n\n{text}")
        
        if politic != 'ASMR':
            # Create the prompt for summarization
            prompt = (f"summarize the following text so it has slight {politic}-leaning bias,"
                    f"more than {min_output_length} characters, makes perfect sense, to provide a short news snippit with as much important info as possible. Make it Attention grabbing and give context. It must be suitable to be spoken by TTS, Include any unique/ intriguing Information:\n\n{text}")
            
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content.strip()
        if content.startswith('"') and content.endswith('"'):
            content = content[1:-1]
        if content.startswith('Headline:'):
            content = content[9:]
        return content
    
    except Exception as e:
        print(f"An error occurred while summarizing the article content: {e}")
        return None

def fetch_news(URL):
    try:
        article = NewsPlease.from_url(URL)
        if isinstance(article, dict):
            article = list(article.values())[0]
        if not article.title or not article.maintext:
            raise ValueError("Article missing title or maintext")
        
        combined_text = f"Headline: {article.title}! {article.maintext}"
        image_link = article.image_url if article.image_url else ""
        return [combined_text, image_link]
    
    except Exception as e:
        print(f"An error occurred while fetching the article from {URL}: {e}")
        return ["", ""]

def get_all_news_from_domain(domain = 'unknown', politic='centre', custom = False, article_amount_custom = 10):
    clear_saved_articles_info(politic)  # fresh start for the JSON file
    filepath_custom = os.path.join('politics', politic, 'news_info_to_render', f'{politic}_custom.json')
    if os.path.exists(filepath_custom):
        with open(filepath_custom, 'w') as file:
            # Write an empty list to ensure the file is a valid JSON file
            json.dump([], file, indent=4)

    def get_news(todays_articles_list, custom = False):

        #If this is called using custom mode, meaning they can see all articels and pick their favourite
        if custom == True:
            todays_articles_bbc = article_scraper.run(bbc_url, article_amount_custom)
            todays_articles_asmr_bbc = article_scraper.run(bbc_url, article_amount_custom)
            todays_articles_fox = article_scraper.run(fox_url, article_amount_custom)
            todays_articles_sky = article_scraper.run(sky_url, article_amount_custom)
            todays_articles_ind = article_scraper.run(ind_url, article_amount_custom)
            todays_articles_stime = article_scraper.run(stime_url, article_amount_custom)

            if domain == 'BBC':
                todays_articles_list = todays_articles_bbc

            elif domain == 'FOX':
                todays_articles_list = todays_articles_fox

            elif domain == 'SKY':
                todays_articles_list = todays_articles_sky
                
            elif domain == 'IND':
                todays_articles_list = todays_articles_ind

            elif domain == 'STIME':
                todays_articles_list = todays_articles_stime

            for i, URL in enumerate(todays_articles_list, start=1): 
                article = NewsPlease.from_url(URL)
                if isinstance(article, dict):
                    article = list(article.values())[0]
                if not article.title or not article.maintext:
                    print("Article missing title or maintext... Skipping")
                print(f"{i}) {article.title}")

            article_choice = int(input("\nEnter Choice: "))
            if 1 <= article_choice <= len(todays_articles_list):
                chosen_custom_url = todays_articles_list[article_choice - 1] 
                combined_text, image_link = fetch_news(chosen_custom_url)
                if combined_text:  # Only proceed if fetching was successful
                    LLM_headline = summarise_text(combined_text, politic)
                    save_article_info(LLM_headline, URL, image_link, politic, 'news_info_to_render', True)
                return 1
            else:
                print("\nInvalid choice. Please enter a number from the list... Restarting Program\n")
                return 'wrong_choice'
            
        elif domain == 'ASMR_BBC':
            for URL in todays_articles_list[ASMR_BBC_OFFSET:]:
                combined_text, image_link = fetch_news(URL)
                if combined_text:  # Only proceed if fetching was successful
                    LLM_headline = summarise_text(combined_text, politic)
                    save_article_info(LLM_headline, URL, image_link, politic)
                    historic_data_writer(LLM_headline, URL, image_link, politic)
            return int(get_json_length(politic) / 3)  # returns the amount of articles in the file
        else:
            for URL in todays_articles_list:
                combined_text, image_link = fetch_news(URL)
                if combined_text:  # Only proceed if fetching was successful
                    LLM_headline = summarise_text(combined_text, politic)
                    save_article_info(LLM_headline, URL, image_link, politic)
                    historic_data_writer(LLM_headline, URL, image_link, politic)
            return int(get_json_length(politic) / 3)  # returns the amount of articles in the file
        
    if domain == 'BBC':
        print('Getting BBC articles')
        return get_news(todays_articles_bbc, custom)

    elif domain == 'FOX':
        print('Getting Fox News articles')
        return get_news(todays_articles_fox, custom)

    elif domain == 'SKY':
        print('Getting Sky News articles')
        return get_news(todays_articles_sky, custom)

    elif domain == 'IND':
        print('Getting Independent articles')
        return get_news(todays_articles_ind, custom)

    elif domain == 'ASMR_BBC':
        print('Getting The BBC articles')
        return get_news(todays_articles_asmr_bbc, custom)

    elif domain == 'STIME':
        print('Getting The Standard articles')
        return get_news(todays_articles_stime, custom)
