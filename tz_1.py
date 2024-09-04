from django.db import models
from django.contrib.auth.models import User
import uuid
from enum import StrEnum

class TypeBoost(StrEnum):
    one = 'one'
    two = 'two'

CHOICES_BOOST = (
    (TypeBoost.one, TypeBoost.one),
    (TypeBoost.two, TypeBoost.two)
)
"""
1) Задание сделал бы примерно так. Во views при авторизации обновлять пользователя last_login
 и при начислениях за вход когда авторизовался проверить last_login если вчерашняя дата то начисляем за  вход обновляем дату
  При сохранеени вознаграждений в первый раз создается запись в boots вознаграждений по типам далее обновляется 
  в соответствии с логикой приложения. 
"""
class Player(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=1000)
    last_login = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'player'
    def __str__(self):
        return self.username


class Boost(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(choices=CHOICES_BOOST, max_length=10)
    coin = models.IntegerField(default=0)
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    last_boost = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'boost'
    def __str__(self):
        return self.id

