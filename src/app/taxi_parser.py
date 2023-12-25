import re

import httpx
import pandas as pd
from pathlib import Path
from scrapy.selector import Selector

NYC_TAXI_DATA_URL = "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page"
FILES_PATH = Path().parent.resolve() / "files"


def get_latest_taxi_data_url() -> str:
    content = httpx.get(NYC_TAXI_DATA_URL)
    latest_year_selector = Selector(text=content.text)
    latest_year_data = latest_year_selector.xpath("//div[@class='faq-answers']").extract_first()
    latest_month_selector = Selector(text=latest_year_data)
    latest_month_data = latest_month_selector.xpath("//ul").getall()[-1]
    yellow_taxi_data = Selector(text=latest_month_data)
    data_url = yellow_taxi_data.xpath("//li//a//@href").getall()[0]
    data_url = re.sub("%20$", "", data_url)
    # return data_url
    return "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-10.parquet"


def download_taxi_data(url: str):
    df = pd.read_parquet(url)
    df.to_parquet(FILES_PATH / "taxi_data.parquet")
