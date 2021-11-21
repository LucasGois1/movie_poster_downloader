from typing import TypedDict


class Movie(TypedDict, total=False):
    id: int
    name: str
    poster_path: str
    poster_bytes: bytes