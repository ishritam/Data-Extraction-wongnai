### What's for:
This project is based on Scrapy. It can be used as a sample backend or a sample to extract data from https://www.wongnai.com/.

### Special Usage:
* Scrapy as Python framework
* requests
* Pandas
* boto3
* loguru

### Project structure (Before run)
    .
    ├── main.py                      > Main file which contains all the functionality to run the Scraper and save the data into a CSV file and images into disired folder.
    ├── config.json                  > Enviornment file storing all required enviornment variables 
    ├── README.txt                   > The top-level README for developers using this project.
    ├── requirements.txt             > All the requirements which is needed to run this project.
    ├── final.csv                    > Scraped data in CSV form.


### Project structure (After run)
    .
    ├── main.py                      > Main file which contains all the functionality to run the Scraper and save the data into a CSV file and images into disired folder.
    ├── config.json                  > Enviornment file storing all required enviornment variables 
    ├── README.txt                   > The top-level README for developers using this project.
    ├── requirements.txt             > All the requirements which is needed to run this project.
    ├── final.csv                    > Scraped data in CSV form.
    ├── logs
        ├── info.log                  > all logger.info('message') goes strictly to info.log
        ├── error.log                 > all logger.error('message') goes strictly to error.log
        ├── traceback.log             > here traceback is separated from all other 'ERROR' level messages, goes strictly to traceback.log (any error inside functions)

### Testing:
* This can run on Windows / Linux(Ubuntu 20.04) system.
* It is advised to create a virtual enviornment if you have existing conflicts with python & other libraries/packages installtions.

### Quickstart:
* Make sure you have updated your OS to latest version.
* Install all necessary dependencies for this project from requirements.txt
* Run pip install -r requirements.txt for installing dependencies.
* Please change parameters accordingly in (config.py) config file as per your system configuration before running the main.py file.
* Run main.py file in for turn on the scrapper.
