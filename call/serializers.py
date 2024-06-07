from rest_framework import serializers
from .models import Company, Customer
from twilio.rest import Client
from django.contrib.auth.models import User


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['founder', 'phoneNumber', 'companyName', 'twilioToken', 'twilioSid', 'twilioNumber']

    def validate_phoneNumber(self, value):
        # Get the request from the context properly
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context must be provided for phone number validation.")
        print(request.data)
        # Retrieve SID and Token from the request data or from the instance (if updating)
        sid = request.data.get("company").get('twilioSid', self.instance.twilioSid if self.instance else None)
        token = request.data.get("company").get('twilioToken', self.instance.twilioToken if self.instance else None)

        if not sid or not token:
            raise serializers.ValidationError("Twilio SID and Token are required for validation.")

        client = Client(sid, token)
        try:
            number = client.lookups.v1.phone_numbers(value).fetch(type=["carrier"])
        except Exception as e:
            raise serializers.ValidationError(f"Invalid phone number: {str(e)}")

        return value


class UserSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'company']

    def create(self, validated_data):
        company_data = validated_data.pop('company')
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        company_serializer = CompanySerializer(data=company_data, context={'request': self.context['request']})
        if company_serializer.is_valid(raise_exception=True):
            company_serializer.save(user=user)

        return user

    def update(self, instance, validated_data):
        company_data = validated_data.pop('company', None)
        company_instance = instance.company

        for attr, value in validated_data.items():
            if attr == 'password':
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()

        if company_data:
            company_serializer = CompanySerializer(company_instance, data=company_data, partial=True,
                                                   context={'request': self.context['request']})
            if company_serializer.is_valid(raise_exception=True):
                company_serializer.save()

        return instance


class CustomerSerializer(serializers.ModelSerializer):
    company_id = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(),
        source='company'  # Assumes the field name on the Customer model is 'company'
    )

    class Meta:
        model = Customer
        fields = ("pk", "company_id", "fullName", "phoneNumber", "info")
