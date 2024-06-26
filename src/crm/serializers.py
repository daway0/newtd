import jdatetime
from django.db import transaction
from django.db.utils import IntegrityError
from rest_framework import serializers

from . import models as m
from . import serializer_validators as sv
from . import utils
from .business import ManipulateInfo


def unique_field(list_of_datas: list[dict]) -> list[dict]:
    datas = []
    unique_field_data = []

    for data in list_of_datas:
        if data["value"] in datas:
            continue

        datas.append(data["value"])
        unique_field_data.append(data)

    return unique_field_data


def check_required_fields(required_fields: tuple[str], fields: dict):
    for field in required_fields:
        value = fields.get(field)
        if value is None:
            raise serializers.ValidationError(
                {field: "this field is required."}
            )


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
    def __init__(self, **kwargs):
        self.true_keyword = kwargs.pop("true", "بله")
        self.false_keyword = kwargs.pop("false", "خیر")
        super().__init__(**kwargs)

    def to_representation(self, value):
        val = super().to_representation(value)
        return self.true_keyword if val else self.false_keyword


class SeperatedCharField(serializers.CharField):
    def __init__(self, threshold: int, **kwargs):
        self.threshold = threshold
        super().__init__(**kwargs)

    def to_representation(self, value):
        value = super().to_representation(value)
        value = str(value)

        return utils.seperate_numbers(self.threshold, value)


class IntListField(serializers.ListField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        values = super().to_internal_value(data)

        int_values = []
        for value in values:
            try:
                int_values.append(int(value))
            except (TypeError, ValueError):
                serializers.ValidationError({"error": "Invalid type"})

        return int_values


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
        return utils.membership_from_verbose(date_obj, jdatetime.date.today())


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
        return utils.contract_end_verbose(jdatetime.date.today(), date_obj)


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


class TranslatedCatalogSerializer(TranslatedSerializer):
    title = serializers.CharField()
    rate = serializers.IntegerField(required=False)

    translated_fields = {"title": "عنوان", "rate": "نمره"}


class AddInfoSerializer(serializers.Serializer):
    person = serializers.IntegerField()
    info = serializers.CharField()
    note = serializers.CharField(required=False)

    def validate_person(self, person_id):
        person = m.People.objects.filter(pk=person_id)
        if not person.exists():
            raise serializers.ValidationError({"error": "invalid person id."})

        return person.first()


class EditInfoSerializer(serializers.Serializer):
    info_id = serializers.IntegerField()
    new_info = serializers.CharField(required=False)
    new_note = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)

        new_info = attrs.get("new_info")
        new_note = attrs.get("new_note")

        if new_info is None and new_note is None:
            raise serializers.ValidationError({"error": "invalid data."})

        return attrs


class InfoSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    note = serializers.CharField(max_length=255, required=False)


class CardNumberSerializer(InfoSerializer):
    value = serializers.CharField(validators=[sv.card_number])


class PhoneNumberSerializer(InfoSerializer):
    value = serializers.CharField(validators=[sv.phone_number])


class AddressSerializer(InfoSerializer):
    value = serializers.CharField()


class CatalogSerializerAPI(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    rate = serializers.IntegerField(required=False)


class CatalogSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="catalog_id")
    rate = serializers.IntegerField(required=False, min_value=1, max_value=10)


class FormSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        person: m.People = kwargs.get("instance")

        super().__init__(*args, **kwargs)

        current_fields = set(self.fields)

        look_up = {
            "پرسنل": FormSerializer.personnel_fields,
            "کارفرما": FormSerializer.client_fields,
            "مددجو": FormSerializer.patinet_fields,
        }

        for type in person.get_types_title:
            current_fields.update(look_up[type])

        for field in current_fields.difference(FormSerializer.Meta.fields):
            self.fields.pop(field)

    common_fields = [
        "joined_at",
        "national_code",
        "firstname",
        "lastname",
        "gender",
        "birthdate",
        "addresses",
        "numbers",
    ]

    personnel_fields = common_fields + [
        "card_number",
        "contract_date",
        "end_contract_date",
        "service_locations",
        "roles",
        "tags",
        "skills",
    ]

    client_fields = common_fields + []

    patinet_fields = common_fields + ["tags"]

    types = serializers.ListField(source="get_types")
    roles = serializers.ListField(source="get_roles")
    addresses = AddressSerializer(
        many=True,
    )
    card_number = CardNumberSerializer()
    numbers = PhoneNumberSerializer(many=True)
    skills = CatalogSerializer(many=True)

    class Meta:
        model = m.People
        fields = [
            "joined_at",
            "national_code",
            "firstname",
            "lastname",
            "gender",
            "birthdate",
            "roles",
            "types",
            "addresses",
            "numbers",
            "card_number",
            "contract_date",
            "end_contract_date",
            "service_locations",
            "tags",
            "skills",
        ]


class CreatePersonSerializer(serializers.Serializer):
    person_id = serializers.CharField(required=False)
    joined_at = serializers.CharField(validators=[sv.date])
    national_code = serializers.CharField(validators=[sv.national_code])
    firstname = serializers.CharField()
    lastname = serializers.CharField()
    gender = serializers.CharField(validators=[sv.gender])
    birthdate = serializers.CharField(validators=[sv.date])
    note = serializers.CharField(max_length=255, required=False)
    types = serializers.ListField()

    contract_date = serializers.CharField(validators=[sv.date], required=False)
    end_contract_date = serializers.CharField(
        validators=[sv.date], required=False
    )
    numbers = PhoneNumberSerializer(many=True)
    card_number = CardNumberSerializer(required=False)
    addresses = AddressSerializer(many=True, required=False)
    roles = IntListField(required=False)
    service_locations = IntListField(required=False)
    tags = IntListField(required=False)
    skills = CatalogSerializer(many=True, required=False)

    def validate_person_id(self, id):
        person_obj = m.People.objects.filter(pk=id).first()
        if not person_obj:
            raise serializers.ValidationError(
                {"error": ["ایدی شخص اشتباه است."]}
            )

        return person_obj

    def validate_types(self, types: list[str]):
        for type in types:
            if not type.startswith("TYP"):
                raise serializers.ValidationError(
                    {"error": ["نوع شخص اشتباه است."]}
                )

        db_types = m.Catalog.objects.filter(code__in=types).values(
            "id",
            "title",
        )
        if not db_types:
            raise serializers.ValidationError(
                {"error": ["نوع شخص اشتباه است."]}
            )

        return db_types

    def personnel_validation(data: dict):
        required_fields = (
            "card_number",
            "contract_date",
            "service_locations",
            "tags",
            "skills",
        )
        check_required_fields(required_fields, data)

    def client_validation(data: dict):
        required_fields = ("addresses",)
        check_required_fields(required_fields, data)

    def patient_validation(data: dict):
        required_fields = "tags"
        check_required_fields(required_fields, data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        type_valdiators = {
            "پرسنل": CreatePersonSerializer.personnel_validation,
            "کارفرما": CreatePersonSerializer.client_validation,
            "مددجو": CreatePersonSerializer.patient_validation,
        }

        for type in attrs["types"]:
            type_valdiators[type["title"]](attrs)

        numbers = attrs.get("numbers")
        if numbers is not None:
            numbers = unique_field(numbers)

        tags = attrs.get("tags")
        if tags is not None:
            tags = set(tags)

        person = attrs.get("person_id")
        if person is not None:
            self.manipulate_obj = ManipulateInfo(
                person,
                addresses=attrs.get("addresses", []),
                numbers=attrs.get("numbers", []),
                card_number=attrs.get("card_number"),
            )
            return attrs

        if m.People.objects.filter(
            national_code=attrs["national_code"]
        ).exists():
            raise serializers.ValidationError({"error": ["کدملی تکراری است."]})

        person = m.People()
        self.manipulate_obj = ManipulateInfo(
            person,
            addresses=attrs.get("addresses", []),
            numbers=attrs.get("numbers", []),
            card_number=attrs.get("card_number"),
        )
        attrs["person_id"] = person

        return attrs

    def create(self, validated_data) -> m.People:
        single_values = {
            "joined_at",
            "firstname",
            "lastname",
            "gender",
            "birthdate",
            "note",
            "contract_date",
            "end_contract_date",
        }
        person: m.People = validated_data.get("person_id")
        if person.pk is None:
            for field in single_values:
                setattr(person, field, validated_data.get(field))

            person.national_code = validated_data["national_code"]

        else:
            for field in single_values:
                value = validated_data.get(field)
                if value != getattr(person, field):
                    setattr(person, field, value)

        specs = []
        specs.extend(
            m.Specification(catalog_id=id, people=person)
            for id in validated_data.get("tags", [])
        )
        for skill in validated_data.get("skills", []):
            specs.append(
                m.Specification(
                    people=person,
                    catalog_id=skill["catalog_id"],
                    rate=skill["rate"],
                )
            )

        try:
            with transaction.atomic():
                person.save()
                self.manipulate_obj.manipulate()
                m.Specification.objects.filter(people=person).delete()
                m.Specification.objects.bulk_create(specs)
                person.roles.set(validated_data.get("roles", []))
                person.service_locations.set(
                    validated_data.get("service_locations", [])
                )
                person.types.set(
                    [type["id"] for type in validated_data["types"]]
                )
        except IntegrityError:
            pass

        return person
