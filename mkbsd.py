import os
import time
import aiohttp
import asyncio
import logging
from pyrogram import Client, filters
from config import *
from database import *
from urllib.parse import urlparse

url = 'https://storage.googleapis.com/panels-api/data/20240916/media-1a-i-p~s'

# Configure logging
logging.basicConfig(
    filename='MKBSD-TG.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Create the Pyrogram client
app = Client("SpidyPHVDL", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, workers=10)

db = connect_to_mongodb(DATABASE, "Spidydb")

async def delay(ms):
    await asyncio.sleep(ms / 1000)

async def download_image(session, image_url, file_path):
    try:
        async with session.get(image_url) as response:
            if response.status != 200:
                raise Exception(f"Failed to download image: {response.status}")
            content = await response.read()
            with open(file_path, 'wb') as f:
                f.write(content)
        logging.info(f"🖼️ Image downloaded successfully to {file_path}")
    except Exception as e:
        logging.error(f"Error downloading image: {str(e)}")

async def main():
    async with app:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"⛔ Failed to fetch JSON file: {response.status}")
                    json_data = await response.json()
                    data = json_data.get('data')
                    logging.info(data)

                    if not data:
                        raise Exception('⛔ JSON does not have a "data" property at its root.')

                    download_dir = os.path.join(os.getcwd(), 'downloads')
                    if not os.path.exists(download_dir):
                        os.makedirs(download_dir)
                        logging.info(f"📁 Created directory: {download_dir}")

                    file_index = 1
                    for key, subproperty in data.items():
                        if subproperty and subproperty.get('dhd'):
                            image_url = subproperty['dhd']
                            logging.info(f"🔍 Found image URL: {image_url}")
                            parsed_url = urlparse(image_url)
                            ext = os.path.splitext(parsed_url.path)[-1] or '.jpg'
                            logging.info(f"Filename : {parsed_url.path.split('/')[-1]}")
                            filename = f"{file_index}{ext}"
                            file_path = os.path.join(download_dir, filename)

                            documents = find_documents(db, COLLECTION_NAME)
                            downloaded_files = {doc["FILENAME"] for doc in documents}
                            if filename not in downloaded_files:
                                await download_image(session, image_url, file_path)
                                pic = await app.send_photo(LOG_ID, photo=file_path, caption=parsed_url.path.split('/')[-1])
                                doc = await app.send_document(LOG_ID, document=file_path,caption=parsed_url.path.split('/')[-1],file_name=parsed_url.path.split('/')[-1])
                                result = {"PIC_ID":pic.id,"DOC_ID":doc.id,"FILENAME":parsed_url.path.split('/')[-1],"IMAGE_URL":image_url}
                                insert_document(db,COLLECTION_NAME,result)
                                file_index += 1
                                os.remove(file_path)
                                logging.info(f"📄 Image sent and removed from {file_path}")
                            await delay(250)

        except Exception as e:
            logging.exception(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Bot Started")
    app.run(main())
