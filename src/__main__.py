import requests
from dotenv import load_dotenv
import os
import pandas as pd
import logging

load_dotenv()

logging.basicConfig(
    filename="status.log", format="%(asctime)s %(message)s", filemode="w"
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

MUDAH_API_URL = os.getenv("MUDAH_API_PREFIX")
PHONE_CATEGORY = 3020
iphonepro_variants = [13, 14, 15]


def get_api_data(offset, category, iphone):
    offset = offset * 50
    url_params = f"?category={category}&from={offset}&include=extra_images%2Cbody&limit=50&q=iphone%20{iphone}%20pro&type=sell"
    full_url = MUDAH_API_URL + url_params
    response = requests.get(full_url)
    logger.info(f"Request sent to MUDAH API with offset {offset}")
    logger.info(f"Response Status Code: {response.status_code}")
    data = response.json()
    return data["data"]


def get_all_iphonepro_data(variants):
    lst_to_store = []
    final_data = []
    for iphone in variants:
        logger.info(f"Fetching data for iPhone {iphone} Pro")
        for i in range(10):
            data = get_api_data(i, PHONE_CATEGORY, iphone)
            lst_to_store.extend(data)
    for data in lst_to_store:
        final_data.append(data["attributes"])
    return final_data


def filter_data(lst_to_transform):
    df = pd.DataFrame(lst_to_transform)
    cols = ["date", "subject", "price", "condition_name", "subarea_name", "adview_url"]
    df = df.loc[:, cols]
    df = df.drop_duplicates(subset=["subarea_name", "adview_url"])
    return df


def main():
    iphone_data = get_all_iphonepro_data(iphonepro_variants)
    df_iphonepro = filter_data(iphone_data)
    try:
        df_iphonepro.to_csv("data/ip13pro_ip14pro_ip15pro_listings.csv", index=False)
        logging.info("Data has been saved to csv")
    except Exception as e:
        logging.info(f"Data has not been saved to csv: {e}")


if __name__ == "__main__":
    main()
    print("Script has been executed")
