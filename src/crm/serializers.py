from rest_framework import serializers

from . import models as m


class CommonPatternSerializer(serializers.Serializer):
    title = serializers.CharField()
    link = serializers.CharField(source="get_absolute_url")


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


class PeopleMinimalSerializer(CommonPatternSerializer):
    title = serializers.CharField(source="full_name")


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


class ServiceLocationSerializer(CommonPatternSerializer):
    title = serializers.CharField(source="address")


class OrderSerializer(serializers.Serializer):
    order_at = serializers.CharField()
    client = PeopleMinimalSerializer()
    services = CommonPatternSerializer(many=True)
    assigned_personnel = PeopleMinimalSerializer()
    service_location = ServiceLocationSerializer()
    referral_people = PeopleMinimalSerializer()
    referral_other = CommonPatternSerializer()
    discount = serializers.IntegerField()


class ContractSerializer(serializers.ModelSerializer):
    care_for = serializers.CharField(source="get_care_for_display")
    patients = PeopleMinimalSerializer(many=True)
    relationship_with_patient = serializers.CharField(
        source="get_relationship_with_patient_display"
    )
    personnel = PeopleMinimalSerializer()
    service_location = ServiceLocationSerializer()
    shift = serializers.CharField(source="get_shift_display")
    personnel_salary_payment_time = serializers.CharField(
        source="get_personnel_salary_payment_time_display"
    )
    referral_people = PeopleMinimalSerializer()
    referral_other = CommonPatternSerializer()

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
        ]


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
    link = serializers.CharField(source="get_absolute_url")

    class Meta:
        model = m.Payment
        fields = ["amount", "paid_at", "note", "link"]


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
