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


class PeopleMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.People
        fields = ["id", "full_name", "get_absolute_url"]


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.Service
        fields = ["title", "healthcare_franchise"]


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


class ReferralSerializer(serializers.Serializer):
    people = PeopleMinimalSerializer(source="referral_people")
    others = serializers.SerializerMethodField()

    def get_others(self, obj):
        if obj.referral_other is None:
            return None

        return obj.referral_other.title


class OrderSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    order_at = serializers.CharField(max_length=10)
    client = PeopleMinimalSerializer()
    services = ServiceSerializer(many=True)
    assigned_personnel = PeopleMinimalSerializer()
    service_location = serializers.CharField(source="service_location.address")
    referral = serializers.SerializerMethodField()
    discount = serializers.IntegerField()

    def get_referral(self, obj):
        return ReferralSerializer(instance=obj).data


class ContractSerializer(serializers.ModelSerializer):
    patients = PeopleMinimalSerializer(many=True)
    personnel = PeopleMinimalSerializer()
    service_location = serializers.CharField(source="service_location.address")
    referral = serializers.SerializerMethodField()

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        instance.pop("referral_people")
        instance.pop("referral_other")
        return instance

    def get_referral(self, obj):
        return ReferralSerializer(instance=obj).data

    class Meta:
        model = m.Contract
        fields = [
            "id",
            "contract_at",
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
            "referral",
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


class PaymentMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.Payment
        fields = ["amount", "paid_at", "note"]


class ButtonSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=250)
    icon = serializers.CharField(max_length=250)
    link = serializers.CharField(max_length=250)


class DataTableSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=250)
    icon = serializers.CharField(max_length=250)
    headers = serializers.SerializerMethodField(required=False)
    data = serializers.SerializerMethodField()

    def get_headers(self, obj):
        return obj["data"].child.Meta.fields
    
    def get_data(self, obj):
        return obj["data"].data


class PreviewSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=250)
    icon = serializers.CharField(max_length=250)
    buttons = ButtonSerializer(many=True)
    table = serializers.SerializerMethodField()
    data_tables = DataTableSerializer(many=True)

    def get_table(self, obj):
        return obj["table"].data
