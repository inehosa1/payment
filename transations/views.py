from django.core.exceptions import ObjectDoesNotExist

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from transations.models import AccountModel, TransactionModel
from transations.serializers import AccountSerializer, TransactionSerializer, AccountTransactionSerializer


# Create your views here.
class AccountViewSet(viewsets.ModelViewSet):
    """
    Vista para la creación de cuentas con balance inicial
    """
    serializer_class = AccountSerializer
    queryset = AccountModel.objects.all()
    http_method_names = ["get", "post", "put", "delete"]

    @action(detail=True, methods=["get"], url_name="detail_transations")
    def detail_transations(self, request, pk=None):
        """
        Detalle de las transaciones por cuenta
        """
        instance_account = self.get_object()
        serializer = AccountTransactionSerializer(instance_account, many=False)
        return Response(serializer.data)

    # @action(detail=False)
    # def recent_users(self, request):
    #     recent_users = User.objects.all().order_by('-last_login')

    #     page = self.paginate_queryset(recent_users)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)

    #     serializer = self.get_serializer(recent_users, many=True)
    #     return Response(serializer.data)

class TransationViewSet(viewsets.ModelViewSet):
    """
    Vista para la creacion de transaciones
    """
    serializer_class = TransactionSerializer
    queryset = TransactionModel.objects.all()
    http_method_names = ["post", "delete"]