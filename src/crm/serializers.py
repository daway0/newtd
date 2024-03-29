import jdatetime
from rest_framework import serializers

from . import models as m
from . import utils


class CommonPatternSerializer(serializers.Serializer):
    value = serializers.CharField(source="title")
    link = serializers.CharField(source="get_absolute_url")


class DynamicFieldSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        super().__init__(*args, **kwargs)

        if fields:
            allowed = set(fields)
            existings = set(self.fields)
            for field in existings.difference(allowed):
                self.fields.pop(field)


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.TagSpecefication
        fields = ["parent", "title"]


class PeopleDetailsSerializer(serializers.ModelSerializer):
    link = serializers.CharField(source="get_absolute_url")

    class Meta:
        model = m.PeopleDetailedInfo
        fields = [
            "get_detail_type_display",
            "address",
            "phone_number",
            "card_number",
            "note",
            "link",
        ]

    translated_titles = {
        "get_detail_type_display": "نوع رکورد",
        "address": "آدرس",
        "phone_number": "شماره تلفن",
        "card_number": "شماره کارت",
        "note": "نوت",
        "link": "لینک",
    }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        omitabale_keys = ["address", "phone_number", "card_number"]
        new_data = dict()

        for key, value in data.items():
            if key in omitabale_keys and value is None:
                continue
            new_data[key] = value

        return utils.translate_serializer_fields(
            new_data, PeopleDetailsSerializer.translated_titles, ["link"]
        )


class PeopleSerializer(DynamicFieldSerializer, serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", [])
        common_fields = [
            "joined_at",
            "membership_period",
            "national_code",
            "fullname_with_prefix",
            "get_people_type_display",
            "get_gender_display",
            "birthdate",
            "age",
            "note",
        ]
        common_fields.extend(fields)

        super().__init__(*args, **kwargs, fields=common_fields)

    specifications = SpecificationSerializer(many=True)
    membership_period = serializers.SerializerMethodField()

    translated_titles = {
        "joined_at": "تاریخ عضویت",
        "membership_period": "عضویت از",
        "national_code": "کد ملی",
        "fullname_with_prefix": "نام و نام خانوادگی",
        "get_people_type_display": "نوع شخص",
        "get_gender_display": "جنسیت",
        "birthdate": "تاریخ تولد",
        "age": "سن",
        "note": "نوت",
        "contract_date": "شروع قرارداد",
        "end_contract_date": "پایان قرارداد",
        "specifications": "صفت‌ها",
        "total_personnel_orders": "تعداد خدمت‌های پرسنل",
        "total_personnel_contracts": "تعداد قرارداد‌‌های پرسنل",
        "total_healthcare_debt_to_personnel": "بدهی مرکز به پرسنل",
        "total_case_contracts": "تعداد قرارداد‌های بیمار",
        "total_client_debt": "بدهی کارفرما",
        "total_client_orders": "تعداد خدمت‌های کارفرما",
        "total_client_contracts": "تعداد قرارداد‌های کارفرما",
    }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return utils.translate_serializer_fields(
            data, PeopleSerializer.translated_titles
        )

    def get_membership_period(self, obj):
        now = jdatetime.date.today()
        date_obj = jdatetime.date(
            int(obj.joined_at.split("/")[0]),
            int(obj.joined_at.split("/")[1]),
            int(obj.joined_at.split("/")[2]),
        )
        last_day_of_month = utils.get_last_day_of_month(date_obj)

        years_diff = now.year - date_obj.year
        months_diff = now.month - date_obj.month
        if months_diff < 0:
            months_diff = 12 - abs(months_diff)

        days_diff = now.day - date_obj.day
        if days_diff < 0:
            days_diff = last_day_of_month - abs(days_diff)

        return f"{years_diff} سال و {months_diff} ماه و {days_diff} روز"

    class Meta:
        model = m.People
        fields = [
            "joined_at",
            "membership_period",
            "fullname_with_prefix",
            "get_people_type_display",
            "get_gender_display",
            "birthdate",
            "age",
            "specifications",
            "note",
            "contract_date",
            "end_contract_date",
            "total_client_orders",
            "total_client_contracts",
            "total_client_debt",
            "total_personnel_orders",
            "total_personnel_contracts",
            "total_healthcare_debt_to_personnel",
        ]


class PeopleMinimalSerializer(CommonPatternSerializer):
    value = serializers.CharField(source="full_name")
    link = serializers.CharField(source="get_absolute_url_api")


class OrderSerializer(DynamicFieldSerializer):
    order_at = serializers.CharField()
    client = PeopleMinimalSerializer()
    services = serializers.CharField(source="services_list")
    assigned_personnel = PeopleMinimalSerializer()
    service_location = serializers.CharField(source="service_location.address")
    referral_people = PeopleMinimalSerializer()
    referral_other = CommonPatternSerializer()
    client_debt = serializers.IntegerField()
    client_payment_status = serializers.CharField()
    debt_to_personnel = serializers.IntegerField()
    personnel_payment_status = serializers.CharField()
    total_cost = serializers.IntegerField()
    total_franchise = serializers.IntegerField()
    discount = serializers.IntegerField()
    link = serializers.CharField(source="get_absolute_url_api")

    translated_titles = {
        "order_at": "زمان خدمت",
        "client": "کارفرما",
        "services": "خدمت‌ها",
        "assigned_personnel": "پرسنل مشخص شده",
        "service_location": "محل خدمت",
        "referral_people": "معرف",
        "referral_other": "معرف دیگر",
        "client_debt": "بدهی کارفرما",
        "client_payment_status": "وضعیت پرداخت کارفرما",
        "debt_to_personnel": "بدهی مرکز به پرسنل",
        "personnel_payment_status": "وضعیت پرداخت پرسنل",
        "total_cost": "هزینه کل",
        "total_franchise": "فرانشیز مرکز",
        "discount": "تخفیف",
    }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return utils.translate_serializer_fields(
            data, OrderSerializer.translated_titles, ["link"]
        )


class ContractSerializer(DynamicFieldSerializer):
    contract_at = serializers.CharField()
    client = PeopleMinimalSerializer()
    care_for = serializers.CharField(source="get_care_for_display")
    patients = PeopleMinimalSerializer(many=True)
    relationship_with_patient = serializers.CharField(
        source="get_relationship_with_patient_display"
    )
    personnel = PeopleMinimalSerializer()
    service_location = serializers.CharField(source="service_location.address")
    shift = serializers.CharField(source="get_shift_display")
    shift_days = serializers.SerializerMethodField()
    shift_start = serializers.IntegerField()
    shift_end = serializers.IntegerField()
    contract_start = serializers.SerializerMethodField()
    contract_end = serializers.SerializerMethodField()
    include_holidays = serializers.BooleanField()
    personnel_monthly_salary = serializers.IntegerField()
    personnel_salary_payment_time = serializers.CharField(
        source="get_personnel_salary_payment_time_display"
    )
    healthcare_franchise_amount = serializers.IntegerField()
    client_debt = serializers.IntegerField()
    client_payment_status = serializers.CharField()
    referral_people = PeopleMinimalSerializer()
    referral_other = CommonPatternSerializer()
    link = serializers.CharField(source="get_absolute_url_api")

    translated_values = {
        "contract_at": "زمان قرارداد",
        "client": "کارفرما",
        "care_for": "مراقبت از",
        "patients": "بیماران",
        "relationship_with_patient": "نسبت با بیمار",
        "personnel": "پرسنل مشخص شده",
        "service_location": "محل خدمت",
        "shift": "شیفت",
        "shift_days": "روز‌های شیفت",
        "shift_start": "ساعت شروع شیفت",
        "shift_end": "ساعت پایان شیفت",
        "contract_start": "شروع قرارداد",
        "contract_end": "پایان قرارداد",
        "include_holidays": "شامل تعطیلات می‌باشد",
        "personnel_monthly_salary": "حقوق ماهیانه پرسنل",
        "personnel_salary_payment_time": "زمان پرداخت حقوق پرسنل",
        "healthcare_franchise_amount": "فرانشیز مرکز",
        "client_debt": "بدهی کارفرما",
        "client_payment_status": "وضعیت پرداخت کارفرما",
        "referral_people": "معرف",
        "referral_other": "معرف های دیگر",
    }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return utils.translate_serializer_fields(
            data, ContractSerializer.translated_values, ["link"]
        )

    def get_shift_days(self, obj):
        shift_days = []
        if obj.saturday:
            shift_days.append("شنبه")
        if obj.sunday:
            shift_days.append("یک‌شنبه")
        if obj.monday:
            shift_days.append("دو‌شنبه")
        if obj.tuesday:
            shift_days.append("سه‌شنبه")
        if obj.wednesday:
            shift_days.append("چهارشنبه")
        if obj.thursday:
            shift_days.append("پنج‌شنبه")
        if obj.friday:
            shift_days.append("جمعه")

        return ", ".join(shift_days)

    def get_contract_start(self, obj):
        start_date = obj.start
        start_hour = obj.start_hour

        return f"{start_date} {start_hour}"

    def get_contract_end(self, obj):
        end_date = obj.end
        end_hour = obj.end_hour

        return f"{end_date} {end_hour}"


class PaymentSerializer(DynamicFieldSerializer, serializers.ModelSerializer):
    source = PeopleSerializer()
    destination = PeopleSerializer()
    order = OrderSerializer()
    contract = ContractSerializer()
    link = serializers.CharField(source="get_absolute_url")

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
            "link",
        ]


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
        return list(obj["data"].child.fields.keys())

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
