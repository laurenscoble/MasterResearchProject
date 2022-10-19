# @Author: Lauren Scoble <laurenscoble>
# @Date:   2022-05-11T13:24:41+10:00
# @Email:  lsco0006@student.monash.edu
# @Project: A Topic Modelling Analysis of ABC News Articles on Education Matters
# @Filename: main_dataPreProcessing.py
# @Last modified by:   laurenscoble
# @Last modified time: 2022-05-26T14:56:07+10:00

# Import required packages
from os import listdir
from os.path import isfile, join
from multiprocessing import Pool
from datetime import timedelta
import time
from parallelProcessingFunctions import article_html_to_json
import csv

if __name__ == "__main__":
    """ This Python file processes the ABC article HTML into individual
    JSON files """

    # Record the time the program started
    start_time = time.monotonic()

    # Define the path for the HTML articles
    path_to_html = "../_data/articles"

    # Get the filenames for each of the HTML articles
    html_articles = [join(path_to_html,f) for f in listdir(path_to_html) if isfile(join(path_to_html,f))]

    # Change this variable to control the number of articles processed
    # p_num = 1000

    # Let the user know how many articles are going to be processed
    print("***************************************************")
    print("*             {} ARTICLES TO PROCESS              *".format(len(html_articles)))
    print("***************************************************")

    # Use multiprocessors to convert html articles to JSON simutaneously
    with Pool() as P:
        success_count = P.map(article_html_to_json,
            html_articles)

    # Record thet ime the program finished
    end_time = time.monotonic()

    # Print the number of articles converted and the time it took to do so
    print("{} articles converted in {} minutes".format(sum(success_count),
        (end_time - start_time)/60))

    # Print the article url and whether or not it was saved for reviewing
    for url, conversion_success in zip(html_articles, success_count):
        with open("../_data/conversion_log.csv","a") as f:
            writer = csv.writer(f)
            writer.writerow([url,conversion_success])
