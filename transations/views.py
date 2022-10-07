from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from transations.models import AccountModel, TransactionModel
from transations.serializers import AccountSerializer, TransactionSerializer, AccountTransactionSerializer, TransferFromAccountToAccount

from django_filters import rest_framework as filters

from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator

from rest_framework import viewsets


@method_decorator(name='list', decorator=swagger_auto_schema( 
    operation_description="Listado de cuentas"
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema( 
    operation_description="Consulta de una unica cuenta"
))
@method_decorator(name='create', decorator=swagger_auto_schema( 
    operation_description="Creacion de cuentas"
))
@method_decorator(name='update', decorator=swagger_auto_schema( 
    operation_description="Actualizacion de cuentas"
))
@method_decorator(name='destroy', decorator=swagger_auto_schema( 
    operation_description="Eliminacion de cuentas"
))
@method_decorator(name='account_transaction_history', decorator=swagger_auto_schema( 
    operation_description="Detalle de transaciones para una sola cuenta"
))
@method_decorator(name='account_transaction_amount', decorator=swagger_auto_schema( 
    operation_description="Transaciones entre cuentas"
))
class AccountViewSet(viewsets.ModelViewSet):
    """
    Vista para la creación de cuentas con balance inicial
    """
    serializer_class = AccountSerializer
    queryset = AccountModel.objects.all()
    http_method_names = ["get", "post", "put", "delete"]

    @action(
        detail=True, 
        methods=["get"],
        serializer_class=AccountTransactionSerializer, 
        url_name="account_transaction_history"
    )
    def account_transaction_history(self, request, pk=None):
        """
        Historico de transaciones realizadas en la cuenta
        """
        instance_account = self.get_object()
        serializer = self.get_serializer(instance=instance_account)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], serializer_class=TransferFromAccountToAccount, url_name="account_transaction_amount")
    def account_transaction_amount(self, request):
        """
        Transferencia de dinero hacia otras cuentas
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()        
        return Response({"message": "transferencia exitosa"})


@method_decorator(name='list', decorator=swagger_auto_schema( 
    operation_description="Listado de transaciones"
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema( 
    operation_description="Consulta de una unica transacion"
))
@method_decorator(name='create', decorator=swagger_auto_schema( 
    operation_description="Creacion de transaciones"
))
@method_decorator(name='destroy', decorator=swagger_auto_schema( 
    operation_description="Eliminacion de transaciones"
))
class TransationViewSet(viewsets.ModelViewSet):
    """
    Vista para la creacion de transaciones
    """
    serializer_class = TransactionSerializer
    queryset = TransactionModel.objects.select_related("account").all()
    http_method_names = ["get", "post", "delete"]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_fields = {
        "account": ["exact"],
        "date": ["year", "month"]
    }

    def balance_adjustment_on_delete(self, instance):
        """
        Funcion para actualizar el saldo al eliminar una transacion
        """
        instance_account = instance.account

        if not instance.income:
            instance_account.balance = instance_account.balance + instance.amount
        else:
            instance_account.balance = instance_account.balance - instance.amount
        
        instance_account.save()


    def destroy(self, request, *args, **kwargs):
        """
        Eliminacion de una transacion ser retorna el balance anterior
        """
        instance = self.get_object()
        self.balance_adjustment_on_delete(instance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)