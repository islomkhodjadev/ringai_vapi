from django.shortcuts import render, get_object_or_404
from .serializers import UserSerializer, CompanySerializer, CustomerSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .models import Customer
from .permissions import IsOwner

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class RegisterLoginView(APIView):

    def post(self, request, *args, **kwargs):

        user = UserSerializer(data=request.data, context={"request": request})

        if user.is_valid(raise_exception=True):

            user = user.save()
            token = Token.objects.create(user=user)

            data = UserSerializer(user).data

            data["token"] = token.key

            return Response(data=data, status=status.HTTP_201_CREATED)


class Login(APIView):

    def post(self, request, *args, **kwargs):

        username = request.data.get("username", None)
        password = request.data.get("password", None)

        if not username or not password:
            return Response(data={"error": "you should provide both username and password"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)

        if not user:

            return Response(data={"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)


        token, created = Token.objects.get_or_create(user=user)

        return Response(data={"token": token.key}, status=status.HTTP_202_ACCEPTED)



class RetrieveToken(APIView):
    def post(self, request, *args, **kwargs):

        username = request.data.get("username", None)
        password = request.data.get("password", None)

        if not username or not password:
            return Response(data={"error": "you should provide both username and password"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)

        if not user:

            return Response(data={"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)

        if Token.objects.filter(user=user).exists():
            Token.objects.get(user=user).delete()

        token = Token.objects.create(user=user)

        return Response(data={"token": token.key}, status=status.HTTP_202_ACCEPTED)

class CustomerView(APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self, pk):
        obj = get_object_or_404(Customer, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        pk = kwargs.pop("pk", None)
        if pk:
            object = self.get_object(pk)
            return Response(CustomerSerializer(object).data, status=status.HTTP_200_OK)

        queryset = Customer.objects.filter(company_id=request.user.company.pk)
        return Response(CustomerSerializer(queryset, many=True).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['company_id'] = request.user.company.pk
        customer = CustomerSerializer(data=data)
        if customer.is_valid(raise_exception=True):
            customer = customer.save()
            return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        customer_id = kwargs.get('pk')

        customer = self.get_object(customer_id)
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        customer_id = kwargs.get('pk')
        customer = self.get_object(customer_id)
        customer.delete()
        return Response(data={"success": "The instance successfully deleted"}, status=status.HTTP_204_NO_CONTENT)

class Call(APIView):

    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self, pk):
        obj = get_object_or_404(Customer, pk=pk)
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):


        customer_id = kwargs.pop("customer_id", None)
        if Customer.objects.filter(pk=customer_id).exists():
            customer = self.get_object(pk=customer_id)
        else:
            return Response({"error": "this customer does not exist"}, status=status.HTTP_404_NOT_FOUND)

        import requests

        url = "https://api.vapi.ai/call/phone"

        payload = {
            "maxDurationSeconds": 60,
            "assistantId": "5ea1c6b4-fe29-4751-b4e0-d1e9ac72103c",
            "type": "outboundPhoneCall",
            "phoneNumberId": "5ecbe56c-6b4f-44a3-942b-ede5bc9f0507",
            "customer": {
                "number": customer.phoneNumber,
                "name": customer.fullName,
                "extension": customer.info if customer.info else " "
            }
        }
        headers = {
            "Authorization": f"Bearer {os.getenv('vapiToken')}",
            "Content-Type": "application/json"
        }

        response = requests.request("POST", url, json=payload, headers=headers).json()

        if response.get("status") == "queued":

            return Response(data=response, status=status.HTTP_202_ACCEPTED)

        return Response(data=response, status=status.HTTP_403_FORBIDDEN)
