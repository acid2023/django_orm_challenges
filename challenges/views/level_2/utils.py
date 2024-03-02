from typing import Any
import random
from datetime import datetime, timedelta
import lorem  # type: ignore

from django.db.models.query import QuerySet
from django.http import HttpRequest


def extract_request_body(request: HttpRequest) -> dict[str, str] | str:
    if request.method == 'POST':
        return request.POST
    elif request.method == 'GET':
        return request.GET
    else:
        return 'incorrect request method'


def make_reply(query_results: QuerySet) -> dict[str, dict[int, dict[str, Any]]]:
    posts_serialized = {post.id: post.to_json() for post in query_results}
    return {f'search results - {len(query_results)} posts found': posts_serialized}


def lorem_word():
    words = lorem.text().split(" ")
    length = len(words)
    choice = random.randint(0, length - 1)
    return words[choice]

def random_date(start=datetime.strptime('1/1/2018 1:30 PM', '%m/%d/%Y %I:%M %p')):
    end = datetime.strptime('1/3/2024 4:50 AM', '%m/%d/%Y %I:%M %p')
    delta = end - start
    int_delta = (delta.days * 24 * 60) + (delta.seconds / 60)
    random_minute = random.randrange(int_delta)
    return start + timedelta(minutes=random_minute)