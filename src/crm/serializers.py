import jdatetime
from rest_framework import serializers

from . import models as m
from . import utils, validators


class TranslatedSerializer(serializers.Serializer):
    translated_fields = dict()

    def to_representation(self, instance, exclude: list[str] = []):
        data = super().to_representation(instance)
        return utils.translate_serializer_fields(
            data, self.translated_fields, exclude
        )


class DynamicFieldSerializer(TranslatedSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop("fields", None)
        exclude = kwargs.pop("exclude", None)
        super().__init__(*args, **kwargs)

        if fields:
            allowed = set(fields)
            existings = set(self.fields)
            for field in existings.difference(allowed):
                self.fields.pop(field)

        if exclude:
            exludes = set(exclude)
            existings = set(self.fields)
            for field in existings.intersection(exludes):
                self.fields.pop(field)


class PersianBooleanField(serializers.BooleanField):
    def to_representation(self, value):
        val = super().to_representation(value)
        return "بله" if val else "خیر"


class SeperatedCharField(serializers.CharField):
    def __init__(self, threshold: int, **kwargs):
        self.threshold = threshold
        super().__init__(**kwargs)

    def to_representation(self, value):
        value = super().to_representation(value)
        value = str(value)

        return utils.seperate_numbers(self.threshold, value)


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.Catalog
        fields = ["parent", "title"]


class PeopleDetailsSerializer(TranslatedSerializer):
    detail_type = serializers.CharField(source="get_detail_type_display")
    value = serializers.CharField()
    note = serializers.CharField()

    translated_fields = {
        "detail_type": "نوع رکورد",
        "value": "مقدار",
        "note": "یادداشت",
    }


class PeopleSerializer(DynamicFieldSerializer):
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

    joined_at = serializers.CharField()
    national_code = serializers.CharField()
    membership_period = serializers.SerializerMethodField()
    fullname_with_prefix = serializers.CharField()
    people_type = serializers.CharField(source="get_people_type_display")
    gender_type = serializers.CharField(source="get_gender_display")
    birthdate = serializers.CharField()
    age = serializers.IntegerField()
    specifications = SpecificationSerializer(many=True)
    contract_date = serializers.CharField()
    end_contract_date = serializers.CharField()
    total_client_orders = serializers.IntegerField()
    total_client_contracts = serializers.IntegerField()
    total_client_debt = SeperatedCharField(threshold=3)
    total_personnel_orders = serializers.IntegerField()
    total_personnel_contracts = serializers.IntegerField()
    total_healthcare_debt_to_personnel = SeperatedCharField(threshold=3)
    note = serializers.CharField()

    translated_fields = {
        "joined_at": "تاریخ عضویت",
        "membership_period": "عضویت از",
        "national_code": "کد ملی",
        "full_name": "نام و نام خانوادگی",
        "fullname_with_prefix": "نام و نام خانوادگی",
        "get_people_type_display": "نوع شخص",
        "get_gender_display": "جنسیت",
        "birthdate": "تاریخ تولد",
        "age": "سن",
        "note": "یادداشت",
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

    def get_membership_period(self, obj):
        date_obj = utils.create_jdate_from_str(obj.joined_at)
        return utils.time_left_til_specific_date_verbose(
            date_obj, jdatetime.date.today()
        )


class PeopleMinimalSerializer(serializers.Serializer):
    value = serializers.CharField(source="full_name")
    link = serializers.CharField(source="get_absolute_url_api")


class ReferralOtherSerializer(TranslatedSerializer):
    title = serializers.CharField()

    translated_fields = {"title": "عنوان"}


class OrderSerializer(DynamicFieldSerializer):
    order_at = serializers.CharField()
    title = serializers.CharField(source="__str__")
    client = PeopleMinimalSerializer()
    services = serializers.CharField(source="services_list")
    assigned_personnel = PeopleMinimalSerializer()
    service_location = serializers.CharField(source="service_location.value")
    referral_people = PeopleMinimalSerializer()
    referral_other = ReferralOtherSerializer()
    client_debt = SeperatedCharField(threshold=3)
    client_payment_status = serializers.CharField()
    debt_to_personnel = SeperatedCharField(threshold=3)
    personnel_payment_status = serializers.CharField()
    total_cost = SeperatedCharField(threshold=3)
    total_franchise = SeperatedCharField(threshold=3)
    discount = SeperatedCharField(threshold=3)
    service_cost = serializers.SerializerMethodField()
    link = serializers.CharField(source="get_absolute_url_api")

    translated_fields = {
        "order_at": "تاریخ خدمت",
        "title": "عنوان خدمت",
        "client": "کارفرما",
        "services": "خدمت‌ها",
        "assigned_personnel": "پرسنل",
        "service_location": "محل خدمت",
        "referral_people": "معرف",
        "referral_other": "معرف دیگر",
        "client_debt": "بدهی کارفرما",
        "client_payment_status": "وضعیت پرداخت کارفرما",
        "debt_to_personnel": "بدهی مرکز به پرسنل",
        "personnel_payment_status": "وضعیت پرداخت پرسنل",
        "total_cost": "هزینه با تخفیف",
        "total_franchise": "فرانشیز مرکز",
        "discount": "تخفیف",
        "service_cost": "قیمت سرویس",
    }

    def to_representation(self, instance):
        return super().to_representation(instance, exclude=["link"])

    def get_service_cost(self, obj: m.Order):
        assert self.context.get(
            "service"
        ), "you forget to pass the service in context."

        service = self.context["service"]
        obj_service = obj.orderservices_set.get(service=service)

        return utils.seperate_numbers(3, str(obj_service.cost))


class ContractSerializer(DynamicFieldSerializer):
    contract_at = serializers.CharField()
    client = PeopleMinimalSerializer()
    care_for = serializers.CharField(source="get_care_for_display")
    patients = serializers.CharField(source="all_patients")
    relationship_with_patient = serializers.CharField(
        source="get_relationship_with_patient_display"
    )
    personnel = PeopleMinimalSerializer()
    service_location = serializers.CharField(source="service_location.value")
    shift = serializers.CharField(source="get_shift_display")
    shift_days = serializers.SerializerMethodField()
    shift_start = serializers.IntegerField()
    shift_end = serializers.IntegerField()
    start = serializers.CharField()
    start_hour = serializers.CharField()
    end = serializers.CharField()
    end_hour = serializers.CharField()
    end_verbose = serializers.SerializerMethodField()
    include_holidays = PersianBooleanField()
    personnel_monthly_salary = SeperatedCharField(threshold=3)
    personnel_salary_payment_time = serializers.CharField(
        source="get_personnel_salary_payment_time_display"
    )
    healthcare_franchise_amount = SeperatedCharField(threshold=3)
    client_debt = SeperatedCharField(threshold=3)
    client_payment_status = serializers.CharField()
    referral_people = PeopleMinimalSerializer()
    referral_other = ReferralOtherSerializer()
    link = serializers.CharField(source="get_absolute_url_api")

    translated_fields = {
        "contract_at": "تاریخ قرارداد",
        "client": "کارفرما",
        "care_for": "مراقبت از",
        "patients": "بیماران",
        "relationship_with_patient": "نسبت با بیمار",
        "personnel": "پرسنل",
        "service_location": "محل خدمت",
        "shift": "شیفت",
        "shift_days": "روز‌های شیفت",
        "shift_start": "ساعت شروع شیفت",
        "shift_end": "ساعت پایان شیفت",
        "start": "تاریخ شروع قرارداد",
        "start_hour": "ساعت شروع قرارداد",
        "end": "تاریخ پایان قرارداد",
        "end_hour": "ساعت پایان قرارداد",
        "end_verbose": "سررسید قرارداد",
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
        return super().to_representation(instance, exclude=["link"])

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

    def get_end_verbose(self, obj):
        date_obj = utils.create_jdate_from_str(obj.end)
        return utils.time_left_til_specific_date_verbose(
            jdatetime.date.today(), date_obj
        )


class PaymentSerializer(DynamicFieldSerializer):
    paid_at = serializers.CharField()
    source = PeopleSerializer()
    destination = PeopleSerializer()
    payment_type = serializers.SerializerMethodField()
    amount = SeperatedCharField(threshold=3)
    order = OrderSerializer()
    contract = ContractSerializer()
    reason = serializers.SerializerMethodField()
    note = serializers.CharField()

    translated_fields = {
        "source": "مبداء",
        "destination": "مقصد",
        "payment_type": "نوع پرداختی",
        "amount": "مقدار",
        "paid_at": "تاریخ پرداخت",
        "reason": "علت پرداخت",
        "note": "یادداشت",
    }

    def to_representation(self, instance):
        return super().to_representation(instance, ["contract", "order"])

    def get_payment_type(self, obj):
        if obj.source:
            return "پرداختی کارفرما"
        return "پرداختی پرسنل"

    def get_reason(self, obj):
        reason = obj.order or obj.contract
        return reason.__str__()


class ButtonSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=250)
    icon = serializers.CharField(max_length=250)
    link = serializers.CharField(max_length=250)


class DataTableSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=250)
    icon = serializers.CharField(max_length=250)
    data = serializers.SerializerMethodField()

    def get_data(self, obj):
        return obj["data"].data


class PreviewSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=250)
    icon = serializers.CharField(max_length=250)
    description = serializers.CharField(max_length=250)
    buttons = ButtonSerializer(many=True, required=False)
    table = serializers.SerializerMethodField()
    data_tables = DataTableSerializer(many=True)

    def get_table(self, obj):
        return obj["table"].data


class OrderServiceSerializer(DynamicFieldSerializer):
    title = serializers.CharField(source="service.title")
    cost = SeperatedCharField(threshold=3)
    link = serializers.CharField(source="service.get_absolute_url_api")

    translated_fields = {"title": "عنوان", "cost": "هزینه"}

    def to_representation(self, instance):
        return super().to_representation(instance, exclude=["link"])


class CallSerializer(DynamicFieldSerializer):
    called_at = serializers.CharField()
    reason = serializers.SerializerMethodField()
    call_direction = serializers.CharField(source="get_call_direction_display")
    from_number = serializers.CharField()
    to_number = serializers.CharField()
    who_called = serializers.SerializerMethodField()
    response_status = serializers.CharField(
        source="get_response_status_display"
    )
    note = serializers.CharField()
    link = serializers.SerializerMethodField()

    translated_fields = {
        "called_at": "تاریخ تماس",
        "reason": "علت تماس",
        "call_direction": "نوع تماس",
        "from_number": "شماره",
        "to_number": "شماره",
        "who_called": "طرفین",
        "response_status": "وضعیت پاسخ",
        "note": "یادداشت",
    }

    def to_representation(self, instance):
        data = super().to_representation(instance, exclude=["link"])
        return utils.omit_null_fields(data, ["from_number", "to_number"])

    def get_who_called(self, obj: m.Call):
        client = obj.from_people or obj.to_people
        return client.full_name

    def get_reason(self, obj: m.Call):
        reason = obj.order or obj.contract
        return reason.__str__()

    def get_link(self, obj: m.Call):
        call_reason_obj = obj.order or obj.contract
        return call_reason_obj.get_absolute_url_api()


class ServiceSerializer(DynamicFieldSerializer):
    title = serializers.CharField()
    base_price = SeperatedCharField(threshold=3)
    healthcare_franchise = SeperatedCharField(threshold=3)
    healthcare_franchise_in_tooman = SeperatedCharField(threshold=3)
    personnel_franchise = serializers.CharField()
    personnel_franchise_in_tooman = SeperatedCharField(threshold=3)
    total_orders = serializers.IntegerField()
    total_orders_in_passed_month = serializers.IntegerField()

    translated_fields = {
        "title": "عنوان خدمت",
        "base_price": "مبلغ پایه",
        "healthcare_franchise": "فرانشیز مرکز",
        "healthcare_franchise_in_tooman": "فرانشیز مرکز به تومان",
        "personnel_franchise": "فرانشیز پرسنل",
        "personnel_franchise_in_tooman": "فرانشیز پرسنل به تومان",
        "total_orders": "کل خدمات",
        "total_orders_in_passed_month": "کل خدمات ماه گذشته",
    }


class EditInfoSerializer(serializers.Serializer):
    person = serializers.IntegerField()
    info = serializers.CharField(max_length=11, min_length=11)
    new_info = serializers.CharField(required=False)

    def validate_person(self, person_id: int):
        person = m.People.objects.filter(id=person_id)
        if not person.exists():
            raise serializers.ValidationError({"error": "invalid person id."})

        return person.first()

    def validate(self, attrs: dict):
        attrs = super().validate(attrs)

        new_info = attrs.get("new_data")
        if self.context["request"].method == "PUT" and new_info is None:
            raise serializers.ValidationError(
                {"error": "new info is required."}
            )

        return attrs


class CatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.Catalog
        fields = ["id", "title", "code"]
