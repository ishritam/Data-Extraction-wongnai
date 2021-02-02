import requests
import json
import config
from tqdm import tqdm
from scrapy import Selector
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError
import requests
import shutil
from loguru import logger
import os


logger.remove()
root_dir = os.path.dirname(os.path.abspath(__file__))

@logger.catch
def log_create(log_dir_name = 'logs'):
    log_path = os.path.join(root_dir, log_dir_name)

    if not os.path.isdir(log_path):
        os.makedirs(log_path)

    # all logger.info('message') goes strictly to info.log
    info_filter = lambda record: record["level"].name == "INFO"
    logger.add(
        log_path + "/info.log",
        mode="a",
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
        filter=info_filter,
    )

    # all logger.error('message') goes strictly to error.log, traceback is not shown due to the second condition
    error_filter = (
        lambda record: record["level"].name == "ERROR"
        and not "traceback" in record["extra"]
    )
    logger.add(
        log_path + "/error.log",
        mode="a",
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
        filter=error_filter,
    )

    # here we make traceback separate from all other 'ERROR' level messages, goes strictly to traceback.log
    traceback_filter = (
        lambda record: "traceback" in record["extra"]
        and record["level"].name == "ERROR"
    )
    logger.add(
        log_path + "/traceback.log",
        mode="a",
        format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
        filter=traceback_filter,
    )



@logger.catch
def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=config.ACCESS_KEY,
                      aws_secret_access_key=config.SECRET_KEY)

    try:
        resp = s3.upload_file(local_file, bucket, s3_file)
        print(resp)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

@logger.catch
def download_images_localy(image_url):
    filename = image_url.split("/")[-1]

    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get(image_url, stream = True)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True
        
        # Open a local file with wb ( write binary ) permission.
        with open(local_image_download_folder+filename,'wb') as f:
            shutil.copyfileobj(r.raw, f)
        logger.info(
                f'Image sucessfully Downloaded: {filename}'
            )
    else:
         logger.info(
                f'Image Couldn\'t be retreived: {filename}'
            )




@logger.catch
def list_view_urls(lv_url):
    '''
    This function extract all the list view urls.
    arg:
        lv_url : List view URL i.e "https://www.wongnai.com/restaurants?regions=9681&categories=21"
    '''
    response = requests.get(lv_url, headers=headers, params=params)
    sel = Selector(text = response.text)
    res_string = sel.xpath('//head/script[1]/text()').extract()[0]
    dict_script = eval(res_string) 
    urls = [i['url'] for i in dict_script['itemListElement']]
    return urls

@logger.catch
def view_more_products(View_More_URL):
    '''
    Scrape all the products information from the View More page

    arg:
        View_More_URL: link to viewmore url

    '''

    response = requests.get(View_More_URL, headers=headers, params=params)
    sel = Selector(text = response.text)
    len_product_format = len(sel.xpath('//div[@class="content"]/span/div[2]/div[2]/div[1]/div/div/div/div/div[1]/text()').extract())
    es_string = sel.xpath("//script[contains(., 'window._wn')]/text()").extract_first()
    sliced = es_string[15:-3]
    res = json.loads(sliced) 
    product_list=[]
    for i in res['store']['businessMenu']['value']['menuGroups']:
        for j in i['items']:
            temp = {}
            temp["Product Name"] = j['displayName']
            temp["Product Price (Without currency)"] = j['price']['exact']
            temp["Currency (THB constant for Thailand)"] = j['price']['text']
            temp["Product Image"] = j['photo'].get('largeUrl', j['photo']['thumbnailUrl']) if 'photo' in j else 'NA'
            product_list.append(temp)
    return product_list


@logger.catch
def product_view(urls):
    '''
    Scrape and aggreate all nessary data i.e 
    Cafe Name, Cafe Category/ Type of Food, Product Name, 
    Product Price (Without currency), Currency (THB constant for Thailand), Product Image

    Store it into a CSV.

    args:
        urls: URL's of all the Product View pages.
    '''


    lis = []
    for url in tqdm(urls):
        try:
            response = requests.get(url, headers=headers, params=params)
            sel = Selector(text = response.text)
            res_string = sel.xpath('//head/script[1]/text()').extract()[0]
            res = json.loads(res_string) 
            View_More_URL = url.split("?")[0]+'/menu'
            view_more_products_data = view_more_products(View_More_URL)
            for product in view_more_products_data:
                temp = {}
                temp['Cafe Name'] = res['name']
                temp['Cafe Category/ Type of Food'] = ",".join(sel.xpath('//*[@id="body"]/div[2]/div/div[2]/div[1]/div/div/div[3]/span[1]/span[@class = "sc-AxirZ juZDil"]/text()').extract())
                #temp['reviewCount'] = res['aggregateRating']['reviewCount'] if 'aggregateRating' in res else 'NA'
                temp['Product Name'] = product['Product Name']
                temp['Product Price (Without currency)'] = product['Product Price (Without currency)']
                temp['Product Price (Without currency)'] = product['Product Price (Without currency)']
                temp['Currency (THB constant for Thailand)'] = product['Currency (THB constant for Thailand)']
                temp['Product Image'] = product['Product Image']
                download_images_localy(product['Product Image'])
                lis.append(temp)
        except Exception as e:
            logger.error(
                f'Error wile scraping Product View URL:{url} \n {e}'
            )
    df = pd.DataFrame(lis)
    # saving the dataframe 
    df.to_csv('final.csv')


if __name__ =="__main__":
    #uploaded = upload_to_aws('/home/shritam/Desktop/Palette/download.jpeg', config.bucket, 'download.jpeg')
    log_create()
    headers = config.headers
    params = config.params
    allowed_domain = 'https://www.wongnai.com/'
    local_image_download_folder = config.download_img_folder
    logger.info(
                f'Config has been passed Successfully!!'
            )


    lv_url = "https://www.wongnai.com/restaurants?regions=9681&categories=21"
    list_view_urls =list_view_urls(lv_url)
    if len(list_view_urls) > 0:
        logger.info(
            'All Listview URL has been scrapped!!'
        )
        product_view(list_view_urls)
