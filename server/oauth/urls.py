from django.urls import include, path
from rest_framework import routers

from oauth import views

router = routers.SimpleRouter(trailing_slash=False)
router.register("client", viewset=views.ClientViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
