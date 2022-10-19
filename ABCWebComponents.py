# @Author: Lauren Scoble <lsco0006>
# @Date:   2022-05-01T13:40:37+10:00
# @Email:  lsco0006@student.monash.edu
# @Project: A Topic Modelling Analysis of ABC News Articles on Education Matters
# @Filename: TopicPage.py
# @Last modified by:   lsco0006
# @Last modified time: 2022-05-06T19:12:47+10:00

# import required packages
import requests
import re
from bs4 import BeautifulSoup, NavigableString, Tag
import shutil # to save it locally
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TopicPage:
    """
    This class loads a topic web page containing a list of articles for scraping
    """

    def __init__(self, selenium_driver):
        """Initilise the object"""
        self.driver = selenium_driver

    def get_web_page(self, topic_page_url):
        """Load the web page"""

        try: # Try to load the page
            self.driver.get(topic_page_url) # Load page

        except: # If the page load fails
            return False

        else: # Otherwise
            return True


    def click_cookie_consent(self,cookie_button_tag):
        """Click the cookie consent banner if available"""

        try: # Check for the existance of cookie consent banner
            self.cookie = self.driver.find_element_by_xpath('//button[@data-component="{}"]'.format(cookie_button_tag))

        except: # If there isn't a cookie consent banner
            return False # Return a False flag

        else: # Otherwise
            self.cookie.click() # Click to remove cookie consent banner

        return True


    def get_last_story_card_publish_date(self,date_tag):
        """Get the date of the last story card"""

        # Get all the card dates on the page
        self.card_date = self.driver.find_elements_by_xpath('//time[@data-component="{}"]'.format(date_tag))

        # Return the datetime of the last story card
        return self.card_date[-1].get_attribute('datetime')


    def click_load_more(self, load_more_tag):
        """Click the load more stories button"""

        # Set a wait variable
        # wait = WebDriverWait(self.driver, 10)

        # Find the load more stories button
        self.more_button = self.driver.find_element_by_xpath('//button[@data-component="{}"]'.format(load_more_tag))
        # self.more_button = wait.until(EC.element_to_be_clickable((By.XPATH,'//button[@data-component="{}"]')))

        # Check if the load more stories button has been disabled
        if self.more_button.text == "NO MORE STORIES TO LOAD":
            return False

        else: # If the button isn't disabled, then there are still more stories to load
            self.more_button.click() # Load more stories
            return True


    def get_story_links(self, story_tag):
        """Return the URLs of the stories on the visible page"""

        try: # Check that there are story cards on the page
            story_elements = self.driver.find_elements_by_xpath('//h3[@data-component="{}"]//a'.format(story_tag))

        except: # If no story cards
            return False

        else: #Otherwise
            # Extract the URLs from the elements
            story_urls = [each.get_attribute("href") for each in story_elements]

            # Return a list of story URLs
            return story_urls


class ArticlePage:
    """This class loads an article page and saves the contents to disk"""

    def __init__(self, article_url):
        """Initialise the object"""
        # self.driver = selenium_driver
        self.url = article_url


    def get_page_uuid(self):
        """Split the URL to get the article UUID"""
        # Remove the ABC domain from the URL
        self.a_uuid = re.sub(r'https://www.abc.net.au/',"",self.url)

        # Convert the forward slashes to underscores for saving to disk
        self.a_uuid = re.sub(r'\/',"_",self.a_uuid)

        return self.a_uuid # Return the result


    def make_page_soup(self):
        """ Get the webpage code and store in a class variable """
        self.r = requests.get(self.url) # Get the page

        if self.r.status_code != 404: # If there isn't a error when page is loaded
            self.soup = BeautifulSoup(self.r.text, 'html.parser')
            return True

        else:
            return False # Article not saved


    def save_page_images(self):
        """ Find images within the web page code. Save to disk and update links
        to local images """

        try:
            self.soup # Check if code has been copied into BS object

        except:
            print("You need to call make_page_soup first")
            return False

        # Only save the images in the main body of the article
        figures = self.soup.find_all("figure") # Find all the images in the page

        # For each of the figures found (images are included) in figures if __name__ == '__main__':
        # the HTML
        for fig in figures: # For each of the figures found
            for each in fig.contents: # Iterate through the tags
                # If the child isn't what is expected
                if isinstance(each, NavigableString):
                    print("Error with images for {}".format(self.url))

                # If the child is a BS Tag
                elif isinstance(each, Tag):
                    for img in each.find_all("img"): # For each of the image references in the HTML
                        try: # Check that the expected image tag is available
                            img["data-src"]

                        except: # If the tag isn't an image, move on
                            pass

                        else:
                            # If the image reference is a link
                            if re.match(r"https://live-production.wcms.abc-cdn.net.au", img["data-src"]):
                                # Remove trailing image formatting before downloading
                                img_url = re.findall(r"(https://live-production.wcms.abc-cdn.net.au/[a-z0-9]*)?", img["data-src"])[0]

                                # Get image ID
                                img_id = re.split(r"\/",img_url)[-1]

                                # Store the trailing image formatting for replacement
                                # image_format = re.search(r"\?(.*)",img["data-src"])[0]

                                try: # Check if image width in source link
                                    # Get image width from HTML
                                    img_width = int(re.findall(r"width=(\d{3})",img["data-src"])[0])

                                except: # If not, move on
                                    pass

                                else: # Add width as parameter
                                    img["width"] = img_width

                                try: # Check if image height in source link
                                    img_height = int(re.findall(r"height=(\d{3})",img["data-src"])[0])

                                except: # If not, move on
                                    pass

                                else: # Add height as parameter
                                    img["height"] = img_height

                                # Create the filename
                                img_filename = "../_data/images/{}.jpg".format(img_id)

                                # Replace the ABC image references with local URLs in the page HTML
                                img["data-src"] = "../images/{}.jpg".format(img_id)
                                img["src"] = "../images/{}.jpg".format(img_id)

                                # Get the image
                                r = requests.get(img_url, stream=True)

                                # If the image was retrieved
                                if r.status_code == 200:
                                    # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
                                    r.raw.decode_content = True
                                    # Open a local file with wb ( write binary ) permission.
                                    with open(img_filename,'wb') as f:
                                        shutil.copyfileobj(r.raw, f)

                                    img_download_flag = True # Flag for returning

                                else:
                                    print("Couldn't download image from {}".format(self.url))

                else: # Catch any other problems
                    print("Error with images for {}".format(self.url))

        try: # Check to see if any images have been downloaded
            img_download_flag

        except: # No images downloaded
            return False

        else:
            return True


    def save_page_html(self):
        """Get the article page"""

        try:
            self.soup # Check if code has been copied into BS object

        except:
            return False

        else:
            # Set the filename
            self.filename = "../_data/articles/{}.html".format(self.a_uuid)

            with open(self.filename, "w") as f: # Create a new HTML file
                f.write(self.soup.prettify())

            return True # Article saved


# Testing classes
if __name__ in "__main__":
    test_article_url = 'https://www.abc.net.au/news/2012-01-12/csu-gets-serious-about-far-west/3769250'
    article_page = ArticlePage(test_article_url)

    article_page.get_page_uuid()

    article_page.make_page_soup()

    article_page.save_page_images()

    article_page.save_page_html()
