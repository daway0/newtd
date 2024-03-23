from rest_framework import serializers

from . import models as m


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.TagSpecefication
        fields = ["parent", "title"]


class PeopleSerializer(serializers.ModelSerializer):
    specifications = SpecificationSerializer(many=True)

    class Meta:
        model = m.People
        fields = [
            "national_code",
            "firstname",
            "lastname",
            "gender",
            "birthdate",
            "people_type",
            "contract_date",
            "end_contract_date",
            "specifications",
            "personnel_role",
            "note",
        ]


class PeopleDetailsSerializer(serializers.ModelSerializer):
    people = PeopleSerializer()

    class Meta:
        model = m.PeopleDetailedInfo
        fields = [
            "detail_type",
            "people",
            "address",
            "phone_number",
            "card_number",
            "note",
        ]


class OrderSerializer(serializers.ModelSerializer):
    client = PeopleSerializer()
    assigned_personnel = PeopleSerializer()
    service_location = PeopleDetailsSerializer()
    referral_people = PeopleSerializer()

    class Meta:
        model = m.Order
        fields = [
            "id",
            "created_at",
            "client",
            "service",
            "assigned_personnel",
            "service_location",
            "referral_people",
            "referral_other",
            "cost",
            "discount",
        ]


class ContractSerializer(serializers.ModelSerializer):
    patients = PeopleSerializer(many=True)
    personnel = PeopleSerializer()
    service_location = PeopleDetailsSerializer()
    referral_people = PeopleSerializer()

    class Meta:
        model = m.Contract
        fields = [
            "id",
            "created_at",
            "care_for",
            "patients",
            "relationship_with_patient",
            "personnel",
            "service_location",
            "shift",
            "saturday",
            "sunday",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "shift_start",
            "shift_end",
            "start",
            "end",
            "include_holidays",
            "personnel_monthly_salary",
            "personnel_salary_payment_time",
            "healthcare_franchise_amount",
            "referral_people",
            "referral_other",
        ]


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.Service
        fields = ["title", "base_price", "healthcare_franchise", "parent"]


class PaymentSerializer(serializers.ModelSerializer):
    source = PeopleSerializer()
    destination = PeopleSerializer()
    order = OrderSerializer()
    contract = ContractSerializer()

    class Meta:
        model = m.Payment
        fields = [
            "source",
            "destination",
            "amount",
            "paid_at",
            "note",
            "order",
            "contract",
        ]
