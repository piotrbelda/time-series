import os
import re

import httpx
from pathlib import Path
from scrapy.selector import Selector

NYC_TAXI_DATA_URL = "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page"

content = httpx.get(NYC_TAXI_DATA_URL)

latest_year_selector = Selector(text=content.text)

latest_year_data = latest_year_selector.xpath("//div[@class='faq-answers']").extract_first()
latest_month_selector = Selector(text=latest_year_data)
latest_month_data = latest_month_selector.xpath("//ul").getall()[-1]
yellow_taxi_data = Selector(text=latest_month_data)
data_url = yellow_taxi_data.xpath("//li//a//@href").getall()[0]
data_url = re.sub("%20$", "", data_url)

print(data_url)

path = Path(__file__).parent.resolve()

os.system(f"wget {data_url} -O {str(path)}/taxi_data.parquet")
breakpoint()
