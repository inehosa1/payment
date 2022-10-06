from rest_framework import  serializers
from transations.models import AccountModel, TransactionModel
from datetime import datetime

class AccountSerializer(serializers.ModelSerializer):
    """
    Serializador para la creacion de cuentas de usuario con nombre y balance
    """
    
    def create(self, validated_data):
        """
        Se sobreescribe para crear transacion con el balance de ajuste manual
        """        
        instance = super().create(validated_data)
        
        TransactionModel.objects.create(
            amount=validated_data.get("balance"),
            description="balance inicial",
            income=True,
            account=instance
        )

        return instance
    
    def update(self, instance, validated_data):
        """
        Se sobreescribe para crear transacion con el balance de ajuste manual
        """        
        TransactionModel.objects.create(
            amount=validated_data.get("balance"),
            description="ajuste manual",
            income=True,
            account=instance
        )

        return super().update(instance, validated_data)


    class Meta:
        model = AccountModel
        fields = "__all__"



class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializador para la consulta de transaciones de la cuenta
    """

    def validate(self, data):
        if not data.get("income") and data.get("amount") > data.get("account").balance:
            raise serializers.ValidationError("El balance a retirar no puede ser mayor al disponible")
        return data

    def create(self, validated_data):
        """
        Se sobreescribe para crear transacion con el balance de ajuste manual
        """        
        # se actualiza el balance si se crea un deposito o retiro        
        instance_account = validated_data.get("account")
        
        if validated_data.get("income"):
            validated_data["description"] = "deposito"
            instance_account.balance = instance_account.balance + validated_data.get("amount")
        else:
            validated_data["description"] = "retiro"
            instance_account.balance = instance_account.balance - validated_data.get("amount")
        
        instance = super().create(validated_data)        
        instance_account.save()
        return instance 

    
    class Meta:
        model = TransactionModel
        fields = "__all__"
        read_only_fields = ('description',)        



class AccountTransactionSerializer(serializers.ModelSerializer):
    """
    Serializador para consultar las transacciones de la cuenta
    """
    account_transaction = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = AccountModel
        fields = ("name", "balance", "account_transaction", )
