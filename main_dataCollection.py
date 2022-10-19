# @Author: Lauren Scoble <lsco0006>
# @Date:   2022-04-30T16:17:01+10:00
# @Email:  lsco0006@student.monash.edu
# @Project: A Topic Modelling Analysis of ABC News Articles on Education Matters
# @Filename: main.py
# @Last modified by:   laurenscoble
# @Last modified time: 2022-09-17T22:12:19+10:00

# import required packages
from selenium import webdriver
from datetime import datetime, timedelta
from os import path
import time
from multiprocessing import Pool

# Import custom packages
from ABCWebComponents import TopicPage, ArticlePage
from parallelProcessingFunctions import download_article

if __name__ == "__main__":

    # Determine how long the program takes to process one topic page
    start_time = time.monotonic()

    # Example from https://selenium-python.readthedocs.io/waits.html

    driver = webdriver.Chrome(executable_path = '/Users/laurenscoble/opt/chromedriver') #start my crawler

    topic_page = TopicPage(driver)

    topic_page.get_web_page('https://www.abc.net.au/news/topic/university')

    topic_page.click_cookie_consent('CookieBanner_AcceptABCRequired')

    more_stories = True # Set the stories flag

    # Create a list to store the article URLs that have already been collected
    articles_processed = []

    # Count articles processed during runtime
    article_count = 0

    while more_stories: # While there are stories still to load on the page

        # Wait to ensure that the page has fully loaded
        time.sleep(10) # seconds

        # Find all the story cards on the page and get their URLs
        tmp_urls = topic_page.get_story_links('CardHeading')

        # Remove any URLs that have already been processed in this execution
        article_urls = [url for url in tmp_urls if url not in articles_processed]

        # Let the user know how many stories need to be downloaded
        print("***************************************************")
        print("*             {} STORIES TO PROCESS               *".format(len(article_urls)))
        print("***************************************************")

        # Use multiprocessors to download articles simutaneously
        with Pool() as P:
            # Use the download articles function with the articles URL
            success_count = P.map(download_article, article_urls)

            # Increment the article_count
            article_count += sum(success_count)

        # Time check
        time_check = time.monotonic()

        # Every 100 articles, print a user message
        if article_count % 100 == 0 and article_count != 0:
            print("Program has downloaded {} articles in {} minutes.".format(article_count,timedelta(minutes=time_check - start_time)))

        # Update the articles_processed list to include the articles just downloaded
        articles_processed += article_urls

        # Get the posted date of the last story displayed on the page
        last_story_date = datetime.strptime(topic_page.get_last_story_card_publish_date('Timestamp'),'%Y-%m-%dT%H:%M:%S.%fZ')

        # If the year of the last_story_date is before 2012, stop loading more stories
        if last_story_date.year < 2012:
            more_stories = False

        else: # If the stories are less than 10 years old

            # Scroll to the bottom of the page
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")

            # Click the pagination load more button
            try:
                more_stories = topic_page.click_load_more('PaginationLoadMoreButton')

            except:
                more_stories = False

    # Chrome driver no longer needed
    driver.close()

    # Get the end time
    end_time = time.monotonic()

    print("Program took {} minutes to download {} stories and their images".format(timedelta(minutes=end_time - start_time),article_count))
