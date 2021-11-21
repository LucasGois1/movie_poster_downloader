import asyncio

from pipeline_methods import get_content


def main():
    loop = asyncio.get_event_loop()
    download_pipeline = get_content(1, 10000)
    counts = loop.run_until_complete(download_pipeline)
    loop.close()

    return counts


if __name__ == '__main__':
    print(main())
