# @Author: Lauren Scoble <lsco0006>
# @Date:   2022-05-05T14:27:14+10:00
# @Email:  lsco0006@student.monash.edu
# @Project: A Topic Modelling Analysis of ABC News Articles on Education Matters
# @Last modified by:   laurenscoble
# @Last modified time: 2022-08-24T20:17:06+10:00


# Import packages
from ABCWebComponents import ArticlePage
from os import path
import time
from bs4 import BeautifulSoup, Tag
import numpy as np
import re
import unicodedata
from datetime import datetime
import json
import pytz
import glob


def download_article(article_url):
    """ This function iterates through a list of article urls and calls on
    the ArticlePage class to save HTML and images to local disk """

    # Create an instance of the ArticlePage class
    article = ArticlePage(article_url)

    # Get the article UUID
    article_id = article.get_page_uuid()

    # Check if the article has already been saved into the article's folder
    if path.exists("../_data/articles/{}.html".format(article_id)):
        print("Skipping {}".format(article_url))
        return 0

    else: # If the article hasn't previously been downloaded

        # Include wait times so that the ABC web server isn't pinged too frequently
        time.sleep(5)

        # Scrape the page HTML
        article_flag = article.make_page_soup()

        # Wait before grabbing images
        time.sleep(3)

        # If there were no issues getting the article_page
        if article_flag:

            # Download images and update image references in locally saved HTML
            article.save_page_images()

            # Save article HTML
            article.save_page_html()

            # Confirm article downloaded
            return 1

        else: # If the article wasn't able to be downloaded
            return 0


def standardise_article_timestamps(timestamp_str):
    """ This function converts various timestamp forms in ABC articles to
    standard %Y"""
    pass


def article_html_to_json(html_filepath):
    """ This function converts a HTML ABC article into a JSON file """

    # Open the passed HTML file
    with open(html_filepath, "r") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Create the article_dict that will eventually be exported into the
    # article article
    try:
        article_dict = {
        "title": re.sub("\n"," ", soup.title.text.strip()),
        "h1": re.sub("\n"," ", soup.h1.text.strip()),
        "url": re.sub(r".html","",re.sub(r"_","/",re.sub(r"../_data/articles",
            "https://www.abc.net.au", html_filepath)))
            }

    except:
        print("Couldn't get basic features for {}".format(html_filepath))
        return 0

    # Find publishsed date
    try:
        article_dict["posted_date"] = soup.time.get("datetime")
    except:
        timestamps_flag = False
    else:
        timestamps_flag = True

    try:
        article_dict["posted_date"]
    except:
        timestamps_flag = False
    else:
        if isinstance(article_dict["posted_date"],str) and len(article_dict["posted_date"]) == 0:
            timestamps_flag = False

        elif isinstance(article_dict["posted_date"],str) and len(article_dict["posted_date"]) > 0:
            timestamps_flag = True

        else:
            timestamps_flag = False

    if not timestamps_flag:
        # Set the timezones
        utc = pytz.utc
        aest = pytz.timezone('Australia/Melbourne')

        try: # Get all available timestamps
            av_timestamps = soup.find_all("span", attrs={"class":"timestamp"})

        except:
            timestamps_flag = False

        else:
            # If there's only one timestamp in the article
            if len(av_timestamps) == 1:
                # Set the flag
                av_timestamps_flag = True

                try: # Determine the format of the timestamp
                    pub_date = datetime.strptime(av_timestamps[0].text.strip(),
                        '%b %d, %Y at %H:%M:%S')

                except:
                    timestamps_flag = False
                    # print("Couldn't get pub date for {}".format(html_filepath))
                    # return 0

                else:
                    # Set the local timezone Australian Eastern Time
                    pub_date = aest.localize(pub_date)

                    # Convert the publish date to utc
                    pub_date_utc = pub_date.astimezone(utc)

                    # Save the date to the article dictionary
                    article_dict["posted_date"] = pub_date_utc.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                    timestamps_flag = True

            # If there is more than one timestamp in the list
            elif len(av_timestamps) > 1:
                # Iterate through the timestamps
                for each in av_timestamps:
                    if isinstance(each, Tag):
                        try:
                            pub_date = datetime.strptime(each.text.strip(),
                                '%B %d, %Y %H:%M:%S')

                        except: # If the date doesn't parse, then just skip
                            print(each.text.strip())

                        else:
                            # Set the local timezone Australian Eastern Time
                            pub_date = aest.localize(pub_date)

                            # Convert the publish date to utc
                            pub_date_utc = pub_date.astimezone(utc)

                            try: # Does minimum date exist?
                                min_date

                            except: # If there isn't a minimum date
                                min_date = pub_date_utc

                            else: # If there is already a minimum date
                                if pub_date_utc < min_date:
                                    min_date = pub_date_utc

                            try: # Now check for maximum date
                                max_date

                            except: # If there isn't a maximum date
                                max_date = pub_date_utc

                            else: # If there is a maximum date
                                if pub_date_utc > max_date:
                                    max_date = pub_date_utc

                try:
                    min_date

                except:
                    # print("No publish date was found for {}".format(html_filepath))
                    # return 0
                    timestamps_flag = False

                else:
                    # Check that a date was found
                    if isinstance(min_date, datetime):
                        # Once all dates have been reviewed

                        # Save the date to the article dictionary
                        article_dict["posted_date"] = min_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                        timestamps_flag = True

                        try: # Check that there is a max date
                            max_date
                        except:
                            pass
                        else:
                            # Confirm that the max date is larger than the min date
                            if max_date > min_date:

                                # Save the date to the article dictionary
                                article_dict["updated_date"] = max_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

                    else: # If no date was found
                        timestamps_flag = False
                        # print("No publish date was found for {}".format(html_filepath))
                        # return 0

    if not timestamps_flag: # If I still don't have a published date
        try:
            pub_date = soup.find("p", attrs={"class":"published"}).find(attrs={"class":"timestamp"}).text.strip()
        except:
            print("Couldn't get pub date for {}".format(html_filepath))
            return 0
        else:
            # Set the local timezone Australian Eastern Time
            pub_date = aest.localize(datetime.strptime(pub_date,
                '%B %d, %Y %H:%M:%S'))
            # Convert the publish date to utc
            pub_date_utc = pub_date.astimezone(utc)
            article_dict["posted_date"] = pub_date_utc.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    # Main paragraph text
    try:
        article_paragraphs = [each.text.strip() for each in soup.find_all(["p","h2"],
            attrs={"class":re.compile(r"_1HzXw|_1EAJU hMmqO SYcM3 zwVFG _1BqKa _3AExf _3HiTE x9R1x pDrMR hmFfs _390V1")})]
    #
    # print(article_paragraphs)
    #No found paragraph text
    except:
        article_text_flag = False

    else:
        article_text_flag = True

    if len(article_paragraphs) == 0:
        try:
            article_text = soup.find("div",
                attrs={"id":"body"}).span.string.strip()

        except: # If there isn't any paragraph text
            article_text_flag = False
            # print("No article text returned for {}".format(html_filepath))
            # return 0

    else:
        article_text = " ".join([re.sub("\n"," ",each) for each in article_paragraphs])
        article_text_flag = True

    if not article_text_flag:
        try: # Try another way to extract content
            article_paragraphs = soup.find('div',
                attrs={"class":"article section"}).find_all(['p','h2','blockquote'])

        except: # If this still doesn't return any content
            # print("No article text returned for {}".format(html_filepath))
            # return 0
            article_text_flag = False

        else:
            if len(article_paragraphs) > 0:
                article_paragraphs_ = [] # Set new list
                # Clean the paragraphs list before joining to make text
                for each in article_paragraphs:
                    if each not in soup.find_all("p",
                            attrs={"class":re.compile(r"published|topics|button")}):
                        each_ = each.text.strip()
                        if each_ not in article_paragraphs_: # No repeating sentences
                            article_paragraphs_.append(each_)
                article_text = " ".join([re.sub("\n"," ",each) for each in article_paragraphs_])
                article_text_flag = True

            else:
                # print("No article text returned for {}".format(html_filepath))
                # return 0
                article_text_flag = False

    if not article_text_flag:
        try:
            article_paragraphs = soup.find("div", attrs={"class":re.compile("comp-rich-text article-text clearfix|comp-rich-text article-text clearfix Narrative-article")})
        except:
            article_text_flag = False

        else:
            if len(article_paragraphs) > 0:
                article_text = " ".join([each.text.strip() for each in article_paragraphs.find_all("p")])
                article_text_flag = True

    if not article_text_flag:
        try:
            article_paragraphs = soup.find('div', attrs={'data-component':'LayoutContainer'}).find_all(['p','h2','aside'], attrs)
        except:
            article_text_flag = False
        else:
            print(article_paragraphs)


        # else:
        #     print(article_body)

    if article_text_flag:
        article_dict["article_body_text"] = re.sub("\n"," ",unicodedata.normalize('NFKC',article_text))

    else:
        print("No article text returned for {}".format(html_filepath))
        return 0

    # Try other fields that may not exist in the HTML
    # ABC channel or Information Source
    try:
        info_source = soup.find(attrs={"data-component":"InfoSource"})
    except:
        pass
    else:
        if isinstance(info_source, Tag):
            for each in info_source.contents:
                if isinstance(each, Tag):
                    article_dict["info_source"] = each.string.strip()

    # Byline
    try:
        byline = soup.find(attrs={"data-component":"Byline"})
    except:
        pass
    else:
        if isinstance(byline, Tag) and len(byline) > 0: # If the byline was returned
            for each in byline.contents:
                if isinstance(each, Tag):
                    byline_ = [auth.text.strip() for auth in each.find_all(attrs={"data-component":re.compile(r"Link|ContentLink|Text")})]
            if len(byline_ ) > 0:
                try:
                    article_dict["byline"] = [re.sub("By ", "", each) for each in byline_]
                except:
                    print("{} has no byline".format(html_filepath))

            else:
                byline_ = soup.find(attrs={"data-component":"Byline"})
                if isinstance(byline_, Tag) and len(byline_) > 0:
                    article_dict["byline"] = [re.sub("By ", "", byline_.find(attrs={"data-component":"Text"}).text.strip())]


        else: # If the byline wasn't found
            try: # Assume the HTML has another format
                byline = soup.find("div", attrs={"class":"byline"})
            except:
                pass
            else:
                if isinstance(byline, Tag) and len(byline) > 0:
                    byline_ = byline.find_all('a')
                    if len(byline_) == 1:
                        article_dict["byline"] = [re.sub("By ","",byline.find('a').text.strip())]
                    elif len(byline_) > 1:
                        for each in byline_:
                            if "/programs/" in each["href"]:
                                pass
                            else:
                                article_dict["byline"] = [each.text.strip()]

        # try:
        #     article_dict["byline"]
        # except:
        #     pass
            # print("No byline for {}".format(html_filepath))
        # else:
        #     print(article_dict["byline"])

    # Updated date
    for i, each in enumerate(soup.find_all("time",attrs={"data-component":"ScreenReaderOnly"})):
        if i == 1:
            try: # Validate the string is in the accepted format for displaying on page
                datetime.strptime(each.string.strip(), '%A %d %b %Y at %I:%M%p')
            except:
                pass
            else:
                # Assume that the second element in this find is the updated article date if the actual HTML text
                # is the assumed datetime format
                article_dict["updated_date"] = each["datetime"]

    # # Keep a record of the images used in the article
    # figures = soup.find_all("figure")
    #
    # # Set up a tmp_list for article image information
    # tmp_image_list = []
    #
    # for each in figures:
    #     try:
    #         img_dict = {"alt_text":each.img["alt"],
    #                    "img_filename":re.sub(r"../images/","",each.img["src"]),
    #                    "img_caption":" ".join(each.figcaption.text.split())}
    #     except:
    #         print("Images unavailable for {}".format(html_filepath))
    #     else:
    #         tmp_image_list.append(img_dict)
    #
    # if len(tmp_image_list) > 0:
    #     article_dict["images"] = tmp_image_list

    # Related ABC keywords
    try:
        tmp_keywords = [each.string.strip() for each in soup.find("div",
                        attrs={"data-component":"RelatedTopics"}).find_all("a")]

    except:
        tmp_keywords_flag = False

    else:
        tmp_keywords_flag = True

    if tmp_keywords_flag and len(tmp_keywords) > 0:
        article_dict["related_keywords"] = tmp_keywords
    else:
        try:
            article_dict["related_keywords"] = [each.text.strip() for each in soup.find("p",
                attrs={"class":"topics"}).find_all("a")]
        except:
            tmp_keywords_flag = False

    if not tmp_keywords_flag:
        try:
            tmp_keypoints = [each.text.strip() for each in soup.find_all("li",
                attrs={"class":"topic-subject"})]
        except:
            tmp_keypoints_flag = False
        else:
            if len(tmp_keypoints) > 0:
                article_dict["key_points"] = tmp_keypoints

    # If there are Key Points listed in the article
    try:
        tmp_keypoints = [unicodedata.normalize('NFKC',
            each.text.strip()) for each in soup.find(attrs={"data-component":"KeyPoints"}).find_all("li")]
    except:
        tmp_keypoints_flag = False

    else:
        tmp_keypoints_flag = True

    if tmp_keypoints_flag and len(tmp_keypoints) > 0:
        article_dict["key_points"] = tmp_keypoints

    else:
        try:
            article_dict["key_points"] = [each.text.strip() for each in soup.find("div",
                attrs={"class":"inline-content wysiwyg right"}).find_all("li")]
        except:
            tmp_keypoints_flag = False

    json_filepath = re.sub(".html",".json",
        re.sub("../_data/articles","../_data/json",html_filepath))

    try: # Export resulting dictionary to file
        with open(json_filepath, 'w') as fp:
            json.dump(article_dict, fp)

    except: # If the export doesn't work
        return 0

    else: # If export works, return True
        return 1


def get_articles_selected_words(html_filepath, words_list=["student","people"]):
    """Return a integer, 1 or 0, flagging if the article contains one or more of
    the words in the words_list parameter."""

    # # Create the filepath for the export file
    # json_filepath = re.sub(".html",".json",
    #     re.sub("../_data/articles",
    #     "../_data/json_matchedKeywords",
    #     html_filepath))
    #
    # # Get all the files that have already been exported
    # path_to_json = '../_data/json_matchedKeywords'
    # json_pattern = path.join(path_to_json, '*.json')
    # file_list = glob.glob(json_pattern)
    #
    # # If this HTML hasn't been processed
    # if json_filepath not in file_list:

    # Open the passed HTML file
    with open(html_filepath, "r") as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    matched_p = []

    # Search for the terms in the words_list
    for each in soup.find_all(["h1","h2","p"]):
        for word in words_list:
            if bool(re.search(r"{}".format(word),each.text.strip().lower())):
                try:
                    clean_string = each.string.strip()
                except:
                    pass
                else:
                    matched_p.append(clean_string)
                    response = 1
                    break

    try:
        response

    except:
        return 0

    else:
        matched_dict = {
        "url": re.sub(r".html","",re.sub(r"_","/",re.sub(r"../_data/articles",
            "https://www.abc.net.au", html_filepath))),
        "matched_p":matched_p
        }

        try: # Export resulting dictionary to file
            with open(json_filepath, 'w') as fp:
                json.dump(matched_dict, fp)

        except: # If the export doesn't work
            return 0

        else: # If export works, return True
            return 1

    # else:
    #     return 0

# Testing function
if __name__ in "__main__":

    test_file = "../_data/articles/news_2013-10-30_year-10-student-sophie-mason-wants-to-buck-trend-of-coag-report_5056944.html"
    test_words = ["student","people"]
    print(get_articles_selected_words(test_file,test_words))



    # article_dict  = article_html_to_json(test_file)
    #
    # print(article_dict)
