"""
В этом задании вам предстоит работать с моделью ноутбука. У него есть бренд (один из нескольких вариантов),
год выпуска, количество оперативной памяти, объём жесткого диска, цена, количество этих ноутбуков на складе
и дата добавления.

Ваша задача:
- создать соответствующую модель (в models.py)
- создать и применить миграцию по созданию модели (миграцию нужно добавить в пул-реквест)
- заполнить вашу локальную базу несколькими ноутбуками для облегчения тестирования
  (я бы советовал использовать для этого shell)
- реализовать у модели метод to_json, который будет преобразовывать объект ноутбука в json-сериализуемый словарь
- по очереди реализовать каждую из вьюх в этом файле, проверяя правильность их работу в браузере
"""
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, JsonResponse, HttpResponseForbidden
from challenges.models import Laptop, LaptopBrand


def laptop_details_view(request: HttpRequest, laptop_id: int) -> JsonResponse | HttpResponse:
    try:
        laptop = Laptop.objects.get(id=laptop_id)
        return JsonResponse(laptop.to_json())
    except Laptop.DoesNotExist:
        return HttpResponseNotFound(f'There is no record with id {laptop_id}')
    """
    В этой вьюхе вам нужно вернуть json-описание ноутбука по его id.
    Если такого id нет, вернуть 404.
    """
    pass


def laptop_in_stock_list_view(request: HttpRequest) -> JsonResponse | HttpResponse:
    """
    В этой вьюхе вам нужно вернуть json-описание всех ноутбуков, которых на складе больше нуля.
    Отсортируйте ноутбуки по дате добавления, сначала самый новый.
    """
    try:
        laptops = Laptop.objects.filter(count__gt=0)  # sorting order by default is set in class Laptop Meta
        response = {laptop.id: laptop.to_json() for laptop in laptops}
        return JsonResponse(response)
    except Laptop.DoesNotExist:
        return HttpResponseNotFound('No db entries found')
    pass


def laptop_filter_view(request: HttpRequest) -> JsonResponse | HttpResponse:
    """
    В этой вьюхе вам нужно вернуть список ноутбуков с указанным брендом и указанной минимальной ценой.
    Бренд и цену возьмите из get-параметров с названиями brand и min_price.
    Если бренд не входит в список доступных у вас на сайте или если цена отрицательная, верните 403.
    Отсортируйте ноутбуки по цене, сначала самый дешевый.
    """
    brand = request.POST.get("brand")
    min_price_str = request.POST.get("min_price")
    query_min_price = None

    if min_price_str is not None and min_price_str != '':
        try:
            query_min_price = float(min_price_str)
            if query_min_price < 0:
                return HttpResponseForbidden('Invalid min_price - cannot be negative')
        except ValueError:
            return HttpResponseForbidden('Invalid min_price - should be positive float value')

    if not brand or query_min_price is None:
        return HttpResponseBadRequest('One of required parameters is missing')

    if brand not in [brand.value for brand in LaptopBrand]:
        reply = 'Invalid brand - you shall choose from available options: ' + " ".join([brand.value for brand in LaptopBrand])
        return HttpResponseForbidden(reply)

    try:
        laptops = Laptop.objects.filter(brand=brand, price__gte=query_min_price).order_by('price')
        filtered_data = [laptop.to_json() for laptop in laptops]
        response = {'laptops': filtered_data}
        return JsonResponse(response)
    except Laptop.DoesNotExist:
        return HttpResponseNotFound('Your request resulted in no results')


def last_laptop_details_view(request: HttpRequest) -> JsonResponse | HttpResponse:
    """
    В этой вьюхе вам нужно вернуть json-описание последнего созданного ноутбука.
    Если ноутбуков нет вообще, вернуть 404.
    """
    laptops = Laptop.objects.all()
    if laptops is None:
        return HttpResponseNotFound('No db entries found')
    last_laptop = laptops.latest('created_at')
    return JsonResponse(last_laptop.to_json())
