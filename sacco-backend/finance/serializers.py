from rest_framework import serializers

from finance.models import LoanAccount, LoanApplication, Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            "id",
            "tx_type",
            "direction",
            "amount",
            "description",
            "status",
            "reference",
            "external_reference",
            "created_at",
        )
        read_only_fields = fields


class DepositSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    payment_method = serializers.ChoiceField(choices=["mtn", "airtel", "card", "bank"])
    phone_number = serializers.CharField(max_length=32, required=False, allow_blank=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate(self, attrs):
        payment_method = attrs.get("payment_method")
        phone_number = str(attrs.get("phone_number", "")).strip()
        if payment_method in {"mtn", "airtel"} and not phone_number:
            raise serializers.ValidationError(
                {"phone_number": "Phone number is required for mobile money deposits."}
            )
        return attrs


class LoanApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = (
            "id",
            "amount",
            "purpose",
            "term_months",
            "collateral_type",
            "collateral_value",
            "applicant_first_name",
            "applicant_last_name",
            "applicant_id_number",
            "employer",
            "monthly_salary",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "status", "created_at")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Loan amount must be greater than zero.")
        return value

    def validate_term_months(self, value):
        if value < 6 or value > 60:
            raise serializers.ValidationError("Repayment term must be between 6 and 60 months.")
        return value

    def create(self, validated_data):
        return LoanApplication.objects.create(member=self.context["request"].user, **validated_data)


class LoanApplicationSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source="member.full_name", read_only=True)
    member_email = serializers.EmailField(source="member.email", read_only=True)

    class Meta:
        model = LoanApplication
        fields = (
            "id",
            "member_name",
            "member_email",
            "amount",
            "purpose",
            "term_months",
            "collateral_type",
            "collateral_value",
            "applicant_first_name",
            "applicant_last_name",
            "applicant_id_number",
            "employer",
            "monthly_salary",
            "status",
            "review_note",
            "reviewer",
            "reviewed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class LoanAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanAccount
        fields = (
            "id",
            "application_id",
            "principal",
            "interest_rate",
            "term_months",
            "outstanding_balance",
            "next_repayment_date",
            "status",
            "created_at",
        )
        read_only_fields = fields


class LoanDecisionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["approve", "reject"])
    review_note = serializers.CharField(required=False, allow_blank=True)


class TransferSerializer(serializers.Serializer):
    transfer_type = serializers.ChoiceField(choices=["internal", "external"])
    destination = serializers.CharField(max_length=255)
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    note = serializers.CharField(required=False, allow_blank=True, max_length=255)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class WithdrawalSerializer(serializers.Serializer):
    destination_type = serializers.ChoiceField(choices=["bank", "mobile"])
    amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    bank_name = serializers.CharField(required=False, allow_blank=True, max_length=120)
    account_number = serializers.CharField(required=False, allow_blank=True, max_length=64)
    routing_number = serializers.CharField(required=False, allow_blank=True, max_length=64)
    mobile_network = serializers.ChoiceField(choices=["mtn", "airtel"], required=False)
    phone_number = serializers.CharField(required=False, allow_blank=True, max_length=32)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate(self, attrs):
        destination_type = attrs["destination_type"]
        if destination_type == "bank":
            required_fields = ("bank_name", "account_number", "routing_number")
        else:
            required_fields = ("mobile_network", "phone_number")

        missing_fields = [field for field in required_fields if not attrs.get(field)]
        if missing_fields:
            raise serializers.ValidationError(
                {field: "This field is required for the selected destination type." for field in missing_fields}
            )
        return attrs
