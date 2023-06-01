from http import HTTPStatus

from django.contrib.auth import authenticate, login
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from oauth.models import Client
from oauth.serializers import ClientSerializer


class ClientViewSet(ViewSet):
    # todo: secrets data will serialize and send to client
    authentication_classes = [SessionAuthentication]

    def list(self, request: HttpRequest) -> JsonResponse:
        clients = request.user.clients.all()
        serializer = ClientSerializer(clients, many=True)
        return JsonResponse({"clients": serializer.data})

    def retrieve(self, request: HttpRequest, pk: str) -> JsonResponse:
        client = request.user.clients.get(client_id=pk)
        serializer = ClientSerializer(client, many=False)
        return JsonResponse({"client": serializer.data})

    def create(self, request: HttpRequest) -> JsonResponse:
        client = Client.objects.create(
            client_name=request.data["client_name"],
            redirect_uris=request.data["redirect_uris"],
            owner=request.user,
        )
        context = {
            "client_id": client.client_id,
            "client_secret": client.client_secret,
        }
        return JsonResponse(context)

    def update(self, request: HttpRequest, pk: str) -> JsonResponse:
        client = request.user.clients.get(client_id=pk)
        redirect_uris = request.data.get("redirect_uris")
        scopes = request.data.get("scopes")
        if redirect_uris is not None:
            client.redirect_uris = redirect_uris
        if scopes is not None:
            client.scopes = scopes
        client.save()
        serializer = ClientSerializer(client, many=False)
        return JsonResponse({"client": serializer.data})

    def delete(self, request: HttpRequest, pk: str) -> JsonResponse:
        client = request.user.clients.get(client_id=pk)
        client.delete()
        return JsonResponse({"msg": "success"})


class AuthorizeView(APIView):
    def get(self, request: HttpRequest) -> HttpResponse:
        client_id = request.query_params["client_id"]
        redirect_uri = request.query_params["redirect_uri"]
        code = request.query_params["code"]
        scope = request.query_params["scope"]

        if request.user.is_authenticated:
            client = Client.objects.get(client_id=client_id)
            try:
                assert redirect_uri in client.redirect_uris
                assert code == client.grant_type
                assert scope in client.scopes.split(" ")
                client.users.add(request.user)
                return redirect("/oauth/login")
            except AssertionError:
                return HttpResponse("", status=HTTPStatus.BAD_REQUEST)
        return redirect("/auth/login")


class LoginView(APIView):
    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, "oauth/login.html")

    def post(self, request: HttpRequest) -> HttpResponse:
        username = request.data["username"]
        password = request.data["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            uris = user.client.redirect_uris.strip(",")
            return redirect(uris[0])
        return redirect("/auth/login")


class Token(APIView):
    pass
