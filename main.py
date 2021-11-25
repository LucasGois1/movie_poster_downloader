import asyncio

import uvloop as uvloop

from pipeline_methods import get_content


def main():
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    counter = asyncio.run(get_content(10000, 20000))

    return counter


if __name__ == '__main__':
    print(main())
