"""yandex_task_arxit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, include
from core.views import SaveImport, ChangeData, GetData, GetPresents, GetStats


urlpatterns = [
    path('imports', SaveImport.as_view()),
    path('imports/<int:import_id>/',
         include([
                    path('citizens/<int:citizen_id>', ChangeData.as_view()),
                    path('citizens', GetData.as_view()),
                    path('citizens/birthdays', GetPresents.as_view()),
                    path('towns/stat/percentile/age', GetStats.as_view()),
            ]))
]
