"""
В этом задании вам предстоит работать с моделью поста в блоге. У него есть название, текст, имя автора, статус
(опубликован/не опубликован/забанен), дата создания, дата публикации, категория (одна из нескольких вариантов).

Ваша задача:
- создать соответствующую модель (в models.py)
- создать и применить миграцию по созданию модели (миграцию нужно добавить в пул-реквест)
- заполнить вашу локальную базу несколькими ноутбуками для облегчения тестирования
- реализовать у модели метод to_json, который будет преобразовывать объект книги в json-сериализуемый словарь
- по очереди реализовать каждую из вьюх в этом файле, проверяя правильность их работу в браузере
"""
import random
import lorem  # type: ignore
from datetime import datetime, timedelta

from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from challenges.models import LoremCategory, Post, PostStatus
from django.db.models import Q
from django.utils import timezone

from .utils import extract_request_body, make_reply, lorem_word, random_date


def create_posts_view(request: HttpRequest) -> HttpResponse:
    try:
        for _ in range(20):
            created_at = random_date()
            status = random.choice([status.name for status in PostStatus])
            if status == PostStatus.unpublished.value:
                published_at = None
            else:
                published_at = random_date(created_at)
            post = Post(
                title=lorem.sentence(),
                content=lorem.paragraph(),
                author=lorem_word(),
                status=status,
                created_at=created_at,
                published_at=published_at,
                category=random.choice([category.value for category in LoremCategory]))
            post.save()

        return HttpResponse("Posts were created successfully", status=200)

    except Exception as e:
        return HttpResponseServerError(str(e))


def last_posts_list_view(request: HttpRequest) -> HttpResponse | JsonResponse:

    """
    В этой вьюхе вам нужно вернуть 3 последних опубликованных поста.
    """
    posts = Post.objects.all().filter(status=PostStatus.published.value).order_by('published_at')
    posts_len = len(posts)
    if posts_len == 0:
        return HttpResponseNotFound('Your request resulted in no results')
    elif posts_len == 1:
        response = {'last published post': [post.to_json() for post in posts]}
    elif posts_len == 2:
        response = {'last 2 published posts': [post.to_json() for post in posts]}
    else:
        response = {'last 3 published posts': [post.to_json() for post in posts[-3:]]}
    return JsonResponse(response)


def posts_search_view(request: HttpRequest) -> HttpResponse | JsonResponse:
    """
    В этой вьюхе вам нужно вернуть все посты, которые подходят под поисковый запрос.
    Сам запрос возьмите из get-параметра query.
    Подходящесть поста можете определять по вхождению запроса в название или текст поста, например.
    """

    request_body = extract_request_body(request)
    if isinstance(request_body, str):
        return HttpResponseBadRequest(request_body)
    else:
        query_request = request_body.get("query", None)

    if query_request is None or query_request == "":
        return HttpResponseBadRequest("'query' as required parameter is missing or query is empty")

    query_words = [query.strip() for query in query_request.split(",")]
    search_behavior = request_body.get("behavior", None)

    try:
        query_results = Post.objects.all()
        iterated_query = Post.objects.none()

        for word in query_words:

            if search_behavior is None or search_behavior == 'loose':
                iterated_query |= query_results.filter(Q(title__icontains=word) | Q(content__icontains=word))

            elif search_behavior == 'strict':
                word = r'\b' + word + r'\b'
                iterated_query |= query_results.filter(Q(title__iregex=word) | Q(content__iregex=word))

            else:
                return HttpResponseBadRequest('please specify search behavior - "behavior" key should be either "strict" or "loose"')

        query_results = iterated_query.order_by('created_at')

        if not query_results.exists():
            return HttpResponseNotFound('Your request resulted in no results')

        else:
            response = make_reply(query_results)
            return JsonResponse(response)

    except Post.DoesNotExist:
        return HttpResponseBadRequest()


def untagged_posts_list_view(request: HttpRequest) -> JsonResponse | HttpResponse:
    """
    В этой вьюхе вам нужно вернуть все посты без категории, отсортируйте их по автору и дате создания.
    """
    try:
        posts = Post.objects.filter(category=None).order_by('author', 'created_at')
        response = make_reply(posts)
        return JsonResponse(response)
    except Post.DoesNotExist:
        return HttpResponseNotFound('Your request resulted in no results')


def categories_posts_list_view(request: HttpRequest) -> HttpResponse:
    """
    В этой вьюхе вам нужно вернуть все посты все посты, категория которых принадлежит одной из указанных.
    Возьмите get-параметр categories, в нём разделённый запятой список выбранных категорий.
    """

    request_body = extract_request_body(request)
    if isinstance(request_body, str):
        return HttpResponseBadRequest(request_body)
    else:
        category_in_request = request_body.get("category", None)

    if category_in_request is None or category_in_request == "":
        return HttpResponseBadRequest("'category' as required parameter is missing or is empy")

    categories = [cat.strip() for cat in category_in_request.split(",")]

    checked_categories = [cat for cat in categories if LoremCategory.is_valid(cat)]

    if checked_categories == []:
        return HttpResponseBadRequest('No valid category proivided - you shall choose from available options: '
                                      + " ".join([name.value for name in LoremCategory]))

    try:
        posts = Post.objects.filter(category__in=categories).order_by('author', 'created_at')
        reply = make_reply(posts)
        return JsonResponse(reply)
    except Post.DoesNotExist:
        return HttpResponseNotFound('Your request resulted in no results')


def last_days_posts_list_view(request: HttpRequest) -> HttpResponse | JsonResponse:
    """
    В этой вьюхе вам нужно вернуть посты, опубликованные за последние last_days дней.
    Значение last_days возьмите из соответствующего get-параметра.
    """
    request_body = extract_request_body(request)
    if isinstance(request_body, str):
        return HttpResponseBadRequest(request_body)
    else:
        last_days_request = request_body.get("last_days", None)

    if last_days_request is None:
        return HttpResponseBadRequest("'last_days' as required parameter is missing")

    try:
        last_days = int(last_days_request)
        if last_days < 0:
            return HttpResponseBadRequest("'last_days' should be positive integer")
    except ValueError:
        return HttpResponseBadRequest("'last_days' should be an integer")

    query_date = datetime.now() - timedelta(days=last_days)
    query_date = timezone.make_aware(query_date)

    try:
        posts = Post.objects.filter(Q(published_at__gt=query_date) & Q(status=PostStatus.published.value)).order_by('author', 'created_at')
        reply = make_reply(posts)
        return JsonResponse(reply)
    except Post.DoesNotExist:
        return HttpResponseNotFound('Your request resulted in no results')
