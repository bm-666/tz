import os

from django.core.wsgi import get_wsgi_application
import csv

from rest_framework.response import Response

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission, IsAdminUser
from rest_framework import serializers
from rest_framework import status

from coin.models import *
from datetime import date, datetime
from typing import Any
from enum import IntEnum
import logging




logger = logging.getLogger(__name__)


class UserPrizeSerializer(serializers.Serializer):
    player = serializers.CharField(required=True)
    level = serializers.CharField(required=True)
    prize = serializers.CharField(required=True)
    score = serializers.IntegerField(required=True)

class StatusCode(IntEnum):
    SUCCESS = 0 # Успешное выполнение
    INCORRECT_DATA = 1 # Некорректные данные
    ERROR = 2 # Любые ошибки приложения

class Request:
    data: dict
    def __init__(self, data: dict) -> None:
        self.data = data

class BaseResponse:
    status_code: StatusCode
    def __init__(self, status_code: StatusCode, data: Any = None) -> None:
        self.status_code = status_code
        if data is not None:
            self.data = data


class IsApp(BasePermission):
    """Реализация прав приложения"""
    def has_permission(self, request, view):
        if request.role == 'app':
            return True
# Задание 2-1

def _give_prize(data: dict):
    try:
        level = Level.objects.get(title=data.get('level'))
        PlayerLevel.objects.create(
            player=Player.objects.get(player_id=data.get('player')),
            level=level,
            is_completed=True,
            completed=date.today(),
            score=data.get('score')
        )
        LevelPrize.objects.create(
            level=level,
            prize=Prize.objects.get(title=data.get('prize')),
            received=date.today()

        )
        return BaseResponse(status_code=StatusCode.SUCCESS)
    except Exception as error:
        logger.exception(error.args)
        return BaseResponse(status_code=StatusCode.ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsApp])
def give_prize(request: Request) -> Response:
    """
    метод выдачи приза игроку
    :param request :type Request
    :return обьект :type BaseResponse
    """
    data: dict = request.data
    serializer_data = UserPrizeSerializer(data=data)

    if serializer_data.is_valid():
        data:BaseResponse = _give_prize(serializer_data.data)

        if data.status_code == StatusCode.SUCCESS:
            return Response(status=status.HTTP_201_CREATED)
        elif data.status_code == StatusCode.ERROR:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif data.status_code == StatusCode.INCORRECT_DATA:
            return Response(status=status.HTTP_400_BAD_REQUEST)


    else:

        return Response(status=status.HTTP_400_BAD_REQUEST)

# Задание 2-2

class UserLevelInfo:
    id: int
    level: str
    is_completed: bool
    prize: str

    def __init__(
            self,
            id: int,
            level: str,
            is_completed: bool,
            prize: str) -> None:

        self.id = id
        self.level = level
        self.is_completed = is_completed
        self.prize = prize

def _user_level_info() -> list[dict]:
    """метод выгрузки данных согласно тестового задания
    :return list[dict]
    """
    list_to_csv: list[dict] = []
    players = Player.objects.select_related()
    for player in players:
        player_levels = [
            UserLevelInfo(
                id=item.id,
                level=item.level.title,
                is_completed=item.is_completed,
                prize=item.level.levelprize_set.select_related('prize')[0].prize.title if item.is_completed else ''
            ).__dict__
            for item in player.playerlevel_set.select_related()
        ]
        list_to_csv += player_levels
    return list_to_csv

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def export_to_csv(request: Request) -> Response:
    """"Метод выгрузки в данных в файл .csv"""
    try:
        user_level_info = _user_level_info()
        with open(f'player_level_info_{datetime.now()}.csv', 'w') as file:
            writer = csv.DictWriter(file, fieldnames=user_level_info[0].keys())
            writer.writeheader()

            for item in user_level_info:
                writer.writerow(item)
        return Response(status=status.HTTP_200_OK)

    except Exception as e:
        logger.exception(f'{e.__class__} : {e.args}')
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)