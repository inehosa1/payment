from rest_framework import  serializers
from transations.models import AccountModel, TransactionModel
from datetime import datetime



class AccountSerializer(serializers.ModelSerializer):
    """
    Serializador para la creacion de cuentas de usuario con nombre y balance
    """
    
    def create_transation(self, validated_data, instance, description, income=True):
        """
        Crea las transaciones necesarias a la hora de actualizar y crear una cuenta
        """
        TransactionModel.objects.create(
            amount=validated_data.get("balance"),
            description=description,
            income=income,
            account=instance,
            date=datetime.now()
        )

    def create(self, validated_data):
        """
        Se sobreescribe para crear transacion con el balance de ajuste manual
        """        
        instance = super().create(validated_data)
        self.create_transation(validated_data, instance, "balance inicial")
        return instance
    
    def update(self, instance, validated_data):
        """
        Se sobreescribe para crear transacion con el balance de ajuste manual
        """        
        self.create_transation(validated_data, instance, "ajuste manual")
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
            validated_data["description"] = "ingresos"
            instance_account.balance = instance_account.balance + validated_data.get("amount")
        else:
            validated_data["description"] = "egresos"
            instance_account.balance = instance_account.balance - validated_data.get("amount")
        
        instance = super().create(validated_data)        
        instance_account.save()
        return instance 
    
    class Meta:
        model = TransactionModel
        fields = "__all__"
        read_only_fields = ('description',)        


class TransferFromAccountToAccount(serializers.Serializer):
    """
    Serializador customizado para el envio de dinero entre cuentas
    """
    queryset_account = AccountModel.objects.all()
    from_account = serializers.SlugRelatedField(
        queryset=queryset_account,
        slug_field='id'
    )
    to_account = serializers.SlugRelatedField(
        queryset=queryset_account,
        slug_field='id'
    )
    amount = serializers.DecimalField(max_digits=8, decimal_places=2)

    def validate(self, data):
        """
        Validaciones a la cuenta para poder transferir el dinero
        """
        if data.get("from_account") == data.get("to_account"):
            raise serializers.ValidationError("La cuenta de remitente no puede ser igual a la cuenta de destino")
        
        if data.get("amount") > data.get("from_account").balance:
            raise serializers.ValidationError("El monto a transferir no puede ser mayor a lo que posee el remitente")
        return data

    def instance_transation(self, validated_data, instance, description, income=True):
        """
        retorna instancia de transacion
        """
        return TransactionModel(
            amount=validated_data.get('amount'),
            description=description,
            income=income,
            account=instance,
            date=datetime.now()
        )

    def create(self, validated_data):
        """
        Se sobreescribe para crear transaciones y descuentos de balance 
        """             
        # Cuenta remitente
        from_account = validated_data.get("from_account")
        from_account.balance = from_account.balance - validated_data.get('amount')

        # Cuenta destino
        to_account = validated_data.get("to_account")
        to_account.balance = to_account.balance + validated_data.get('amount')

        instance_from_account = self.instance_transation(
            validated_data, from_account, "transferencia hacia: {}".format(to_account.name), income=False)

        instance_to_account = self.instance_transation(
            validated_data, to_account, "transferencia desde: {}".format(from_account.name))

        # Creacion y actualizacion multiple para minimizar querys
        AccountModel.objects.bulk_update([from_account, to_account], ['balance'])
        TransactionModel.objects.bulk_create([instance_from_account, instance_to_account])

        return True


class AccountTransactionSerializer(serializers.ModelSerializer):
    """
    Serializador para consultar las transacciones de la cuenta
    """
    account_transaction = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = AccountModel
        fields = ("name", "balance", "account_transaction", )
