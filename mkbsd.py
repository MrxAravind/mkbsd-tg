import os
import time
import aiohttp
import asyncio
from pyrogram import Client, filters
from config import *
from database import *
from urllib.parse import urlparse
url = 'https://storage.googleapis.com/panels-api/data/20240916/media-1a-i-p~s'




logging.basicConfig(
    filename='MKBSD-TG.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)




# Create the Pyrogram client
app = Client("SpidyPHVDL", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN,workers=100)






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
    except Exception as e:
        print(f"Error downloading image: {str(e)}")

async def main():
    async with app:
       try:
         async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"⛔ Failed to fetch JSON file: {response.status}")
                json_data = await response.json()
                data = json_data.get('data')
                
                if not data:
                    raise Exception('⛔ JSON does not have a "data" property at its root.')

                download_dir = os.path.join(os.getcwd(), 'downloads')
                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)
                    print(f"📁 Created directory: {download_dir}")

                file_index = 1
                for key, subproperty in data.items():
                    if subproperty and subproperty.get('dhd'):
                        image_url = subproperty['dhd']
                        print(f"🔍 Found image URL!")
                        parsed_url = urlparse(image_url)
                        ext = os.path.splitext(parsed_url.path)[-1] or '.jpg'
                        filename = f"{file_index}{ext}"
                        file_path = os.path.join(download_dir, filename)

                        await download_image(session, image_url, file_path)
                        print(f"🖼️ Downloaded image to {file_path}")
                        pic = await app.send_photo(Chat_ID,photo=file_path)
                        doc = await app.send_document(Chat_ID,document=file_path)
                        file_index += 1
                        await delay(250)

       except Exception as e:
            print(f"Error: {str(e)}")
if __name__ == "__main__":
    app.run(main())
