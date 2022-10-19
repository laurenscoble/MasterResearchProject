# Monash University Masters Research Project
## October 2022

### Data collection code repository
This repository contains the Python code I wrote to scrape education-relation news from abc.net.au.

I scraped HTML pages and images using `main_dataCollection.py`, class objects within `ABCWebComponent.py` and functions within `parallelProcessingFunctions.py` to scrape multiple webpages at a time using parallel processing.

I used `main_dataPreProcessing` along with functions within`parallelProcessingFunctions.py` to extract the article text from the HTML and store it in individual JSON files. This process also used pool processing to speed up the process by handling more than one HTML file at a time.

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.
