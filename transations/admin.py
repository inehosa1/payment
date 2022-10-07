from django.contrib import admin
from transations.models import AccountModel, TransactionModel

@admin.register(AccountModel)
class AccountAdmin(admin.ModelAdmin):
    """
    Clase para la administracion de cuentas
    """
    list_display = ('name', 'balance')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(TransactionModel)
class TransactionAdmin(admin.ModelAdmin):
    """
    Clase para la administracion de transaciones
    """
    list_display = ('amount', 'description', 'date', 'income', 'account')
    

    def has_add_permission(self, request):
        return  

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False