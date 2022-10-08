from rest_framework import  serializers
from transations.models import AccountModel, TransactionModel
from datetime import datetime


class AccountSerializer(serializers.ModelSerializer):
    """
    Serializador para la creacion de cuentas de usuario con nombre y balance
    """
    
    def create_transation(self, instance, description, income=True):
        """
        Crear transacion

        Args:
            instance (AccountModel): con la cuenta a realizar la transacion
            description (str): descripcion para la transacion aplicada
            income (bool, optional): tipo de transacion ingreso/egreso . por defecto True.
        """
        TransactionModel.objects.create(
            amount=instance.balance,
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
        self.create_transation(instance, "balance inicial")
        return instance
    
    def update(self, instance, validated_data):
        """
        Se sobreescribe para crear transacion con el balance de ajuste manual
        """        
        instance = super().update(instance, validated_data)
        self.create_transation(instance, "ajuste manual")
        return instance


    class Meta:
        model = AccountModel
        fields = "__all__"



class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializador para la consulta de transaciones de la cuenta
    """

    def validate(self, data):
        """
        Validaciones a aplicar en la transacion
        """
        if not data.get("income") and data.get("amount") > data.get("account").balance:
            raise serializers.ValidationError("El balance a retirar no puede ser mayor al disponible")
        return data

    def update_account_balance(self, validated_data):
        """
        Funcion para actualizar balance de la cuenta cuando se realiza una transacion

        Args:
            validated_data (dict): con la data validada
        """
        instance_account = validated_data.get("account")
        
        if validated_data.get("income"):
            validated_data["description"] = "ingreso"
            instance_account.balance = instance_account.balance + validated_data.get("amount")
        else:
            validated_data["description"] = "egreso"
            instance_account.balance = instance_account.balance - validated_data.get("amount")
        instance_account.save()

    def create(self, validated_data):
        """
        Se sobreescribe para crear transacion con el balance de ajuste manual    
        """      
        instance = super().create(validated_data)        
        self.update_account_balance(validated_data)
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

        Args:
            data (dict): proceda para aplicar las validaciones
        Raises:
            serializers.ValidationError: La cuenta de remitente no puede ser igual a la cuenta de destino
            serializers.ValidationError: El monto a transferir no puede ser mayor a lo que posee el remitente
        Returns:
            dict: con las validaciones aplicadas
        """
        if data.get("from_account") == data.get("to_account"):
            raise serializers.ValidationError("La cuenta de remitente no puede ser igual a la cuenta de destino")
        
        if data.get("amount") > data.get("from_account").balance:
            raise serializers.ValidationError("El monto a transferir no puede ser mayor a lo que posee el remitente")
        
        return data

    def instance_transation(self, validated_data, instance, description, income=True):
        """
        retorna instancia de transacion
        Args:
            validated_data (dict): diccionario con las valicaciones realizadas a la data
            instance (AccountModel): instancia de tipo accountmodel
            description (str): descripcion para la transacion aplicada
            income (bool, optional): tipo de transacion ingreso/egreso . por defecto True.
        Returns:
            instance (TransactionModel): objecto con la transacion a realizar
        """
        return TransactionModel(
            amount=validated_data.get('amount'),
            description=description,
            income=income,
            account=instance,
            date=datetime.now()
        )

    def update_account_balance(self, validated_data):
        """
        Funcion para actualizar el saldo en la cuenta remitente y la cuenta destino

        Args:
            validated_data (dict): con las validaciones procesadas

        Returns:
           instance (AccountModel): cuenta remitente
           instance (AccountModel): cuenta destino
        """
        # Cuenta remitente
        from_account = validated_data.get("from_account")
        from_account.balance = from_account.balance - validated_data.get('amount')

        # Cuenta destino
        to_account = validated_data.get("to_account")
        to_account.balance = to_account.balance + validated_data.get('amount')

        # Actualiza los balances en 1 solo query
        AccountModel.objects.bulk_update([from_account, to_account], ['balance'])
        return from_account, to_account

    def create_money_transfer_transaction(self, validated_data, from_account, to_account):
        """
        Funcion para crear el log de la transferencia realizada

        Args:
            validated_data (dict): con las validaciones procesadas
            from_account (AccountModel): cuenta remitente
            to_account (AccountModel): cuenta destino
        """
        instance_from_account = self.instance_transation(
            validated_data, from_account, "transferencia hacia: {}".format(to_account.name), income=False)

        instance_to_account = self.instance_transation(
            validated_data, to_account, "transferencia desde: {}".format(from_account.name))

        # Crea las 2 transaciones en 1 solo query
        return TransactionModel.objects.bulk_create([instance_from_account, instance_to_account])

    def create(self, validated_data):
        """
        Se sobreescribe para crear transaciones y descuentos de balance 
        """           
        from_account, to_account = self.update_account_balance(validated_data)
        return self.create_money_transfer_transaction(validated_data, from_account, to_account)        


class AccountTransactionSerializer(serializers.ModelSerializer):
    """
    Serializador para consultar las transacciones de la cuenta
    """
    account_transaction = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = AccountModel
        fields = ("name", "balance", "account_transaction", )
