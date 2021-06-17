import asyncio
import os
import re

from aiohttp import ClientSession

from internal.arg_parser import parse_args

output_dir = os.getcwd() + "/output"

COUNTER = 1


async def http_request(session, url):
    resp = await session.request(
        method="GET", url=url, headers={"User-Agent": "Mozilla/5.0"}
    )
    resp.raise_for_status()
    return resp


async def download_image(session, image_url):
    resp = await http_request(session, image_url)

    global COUNTER
    count = COUNTER
    COUNTER += 1

    with open(output_dir + "/" + str(count), "wb") as img_file:
        bytes_list = await resp.content.read()
        img_file.write(bytes_list)


def parse_urls_to_images_from_page(page_html):
    whitespace = r"\s*"
    non_whitespace = r"\S+"
    img_url = rf"({non_whitespace})"
    img_regex = re.compile(
        rf'<img{whitespace}class="t0fcAb"{whitespace}alt=""{whitespace}src="{img_url}"/>'
    )

    return [img.group(1) for img in re.finditer(img_regex, page_html)]


async def download_images_from_page(session, source_url):
    resp = await http_request(session, source_url)
    html = await resp.text()

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    tasks = [
        download_image(session, img) for img in parse_urls_to_images_from_page(html)
    ]
    await asyncio.gather(*tasks)


async def main():
    args = parse_args()

    async with ClientSession() as session:
        urls_to_scrape = [
            f"https://www.google.com/search?q={topic}&tbm=isch" for topic in args.topics
        ]

        tasks = [download_images_from_page(session, url) for url in urls_to_scrape]
        await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
