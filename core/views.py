from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from .models import Import
from .validator import post_validate, patch_validate

import json

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


# 1
@method_decorator(csrf_exempt, name='dispatch')
class SaveImport(View):
    """
    Принимает на вход набор с данными о жителях (json)
    и сохраняет его с уникальным идентификатором import_id.

    """
    def post(self, request):
        try:
            document = json.loads(request.body)
            post_validate(document)
        except (TypeError, ValueError, json.JSONDecodeError, IndexError, AttributeError) as exc:
            return HttpResponse(exc.args[0], status=405)

        # по-моему это бессмысленный кусок кода, но ТЗ есть ТЗ
        document['data'] = document.pop('citizens')
        # -----------------------------------------------------

        data = json.dumps(document, indent=4, ensure_ascii=False)

        payload = Import.objects.create(value=data)
        return HttpResponse(payload.pk, status=200)


# 2
@method_decorator(csrf_exempt, name='dispatch')
class ChangeData(View):
    """
    Изменяет инормацию о жителе в указанном наборе данных.

    """
    def patch(self, request, import_id, citizen_id):

        try:
            # берем нужный импорт
            my_import = Import.objects.get(pk=import_id)
        except Import.DoesNotExist:
            return HttpResponse('Такого импорта не существует')

        # из него берем нужных людей
        all_citizens = json.loads(my_import.value)['data']

        # находим интересуещего нас жителя
        citizen = next(x for x in all_citizens if x['citizen_id'] == citizen_id)

        # собираемся его пропатчить
        patch_citizen = all_citizens.pop(all_citizens.index(citizen))

        try:
            patch_data = json.loads(request.body)
            patch_validate(patch_data)
        except (json.JSONDecodeError, ValueError, TypeError, IndexError, AttributeError) as exc:
            return HttpResponse(exc.args[0], status=400)

        # приступаем к патчингу
        for key in patch_data:
            if key == 'relatives':
                # добавим пару проверок
                if patch_data['relatives'] is None:
                    return HttpResponse('Поле relatives не должно быть null')

                if not all(isinstance(relative, int) for relative in patch_data['relatives']):
                    return HttpResponse("Все элементы поля relative должны быть int", status=400)

                if citizen_id in patch_data['relatives']:
                    return HttpResponse('У жителя не может быть отношений с самим собой', status=400)

                if len(set(patch_data['relatives'])) != len(patch_data['relatives']):
                    return HttpResponse('В поле relatives не должно быть дубликатов')

                citizens_ids = [id_relative['citizen_id'] for id_relative in all_citizens]
                for relative in patch_data['relatives']:
                    if relative not in citizens_ids:
                        return HttpResponse('Отношений с данным id быть не может, так как его нет в данной выгрузке')

                # удалить все существующие:
                for relative in patch_citizen['relatives']:
                    new_relative = next(x for x in all_citizens if x['citizen_id'] == relative)
                    all_citizens[all_citizens.index(new_relative)][key].remove(citizen_id)

                # если апдэйтнулись родственные связи
                if patch_data[key]:
                    for relative in patch_data[key]:
                        new_relative = next(x for x in all_citizens if x['citizen_id'] == relative)
                        all_citizens[all_citizens.index(new_relative)][key].append(citizen_id)

            patch_citizen[key] = patch_data[key]

        # добавляем обратно в список жителей
        all_citizens.append(patch_citizen)

        # сохраняем обратно в базу
        my_import.value = json.dumps({"data": all_citizens}, ensure_ascii=False, indent=4)
        my_import.save()

        return HttpResponse('ok', status=200)


# 3
class GetData(View):
    """
    Возвращает список жителей для указанного набора данных.

    """
    def get(self, request, import_id):
        try:
            data = Import.objects.get(pk=import_id).value
        except Import.DoesNotExist:
            return HttpResponse(status=404, content='Импорта с таким номером не существует')

        return HttpResponse(data, content_type='application/json', status=200)


class GetPresents(View):
    """
    Возвращает жителей и кол-во подарков, которые они будут покупать
    своим ближайшим родственникам.
    Ответ сгруппирован по месяцам из указанного набора данных

    """

    # test
    def get(self, request, import_id):
        return HttpResponse(f'Get presents data for {import_id}')


class GetStats(View):
    """
    Возвращает статистику по городам для набора данных
    в разрезе возраста жителей.

    """

    # test
    def get(self, request, import_id):
        return HttpResponse(f'Get stats data for {import_id}')


class TestClass(View):
    def get(self, request, item_id):

        try:
            data = Import.objects.get(pk=item_id).value

        except Import.DoesNotExist:
            return HttpResponse(status=404, content='Импорта с таким номером не существует')

        return HttpResponse(data, content_type='application/json')