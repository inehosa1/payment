from django.contrib import admin
from transations.models import AccountModel, TransactionModel



class DataViewOnlyAdmin(admin.ModelAdmin):
    """
    Clase base para desativar todos los permisos menos de lectura en el administrador
    """

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AccountModel)
class AccountAdmin(DataViewOnlyAdmin):
    """
    Clase para la administracion de cuentas
    """
    list_display = ('name', 'balance')

    
@admin.register(TransactionModel)
class TransactionAdmin(DataViewOnlyAdmin):
    """
    Clase para la administracion de transaciones
    """
    list_display = ('amount', 'description', 'date', 'income', 'account')
    