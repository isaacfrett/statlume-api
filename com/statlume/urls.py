"""
URL configuration for statlume project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from typing import Any, List
from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI, Redoc
from requests import Request
from com.statlume.database import Database
from django.http import FileResponse, JsonResponse
from flask import jsonify


#  add to api-> docs_decorator=staff_member_required
api = NinjaAPI(title="Statlume API", docs=Redoc(), csrf=True)

@api.get("/nba/playerstats")
def playerstats(request: Request, name: str):
    player = Database('nba').get_player_stat(name=name)
    return JsonResponse(player)

@api.get("/nba/playerlogs")
def playerlogs(request: Request, id: int):
    player = Database('nba').get_player_logs(id=id)
    return JsonResponse(player)

@api.get("/nba/playerlogs/games")
def playerlogs_games(request: Request, name: str, games: int):
    player = Database('nba').get_player_logs_games(name=name, games=games)
    return JsonResponse(player)

@api.get("/nba/teams")
def teams(request: Request):
    teams = Database('nba').get_teams()
    return JsonResponse(teams)

@api.get("/nba/players")
def players(request: Request, team: str):
    players = Database('nba').get_players(team)
    return JsonResponse(players)

@api.get("/nba/odds")
def odds(request: Request, name: str, prop: str):
    odds = Database('nba').get_odds(name, prop)
    return JsonResponse(odds)

@api.get("/nba/datasheets")
def datasheets(request: Request):
    datasheets = Database('nba').get_datasheets()
    return JsonResponse(datasheets, safe=False)



urlpatterns: List[Any] = [
    path("admin/", admin.site.urls),
    path("api/", api.urls)
]
