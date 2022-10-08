from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class AccountModel(models.Model):
    """
    Modelo para cuentas
    """
    name = models.CharField("Nombre de cuenta", max_length=50, unique=True)
    balance =  models.DecimalField("Balance", max_digits=8, decimal_places=2)

    def __str__(self):
        return "Nombre: {} Balance: {}".format(self.name, self.balance)

    class Meta:	
        verbose_name = 'Cuenta'
        verbose_name_plural = 'Cuentas'


class TransactionModel(models.Model):
    """
    Modelo para las transaciones
    """
    amount =  models.DecimalField("Balance", validators=[MinValueValidator(0)], max_digits=8, decimal_places=2)
    description = models.TextField("Descripcion")
    date = models.DateField("Fecha de transacion")
    income = models.BooleanField("Tipo de transacion")
    account = models.ForeignKey(AccountModel, on_delete=models.CASCADE, verbose_name="Cuenta de la transacion", related_name='account_transaction')

    def balance_adjustment_on_delete(self, instance):
        """
        Funcion para ajustar el saldo cuando se elimine una transacion
        
        Args:
            instance (TransactionModel): instancia de la transaction para obtener la cuenta y ajustar el saldo
        """

        instance_account = instance.account
        if not instance.income:
            instance_account.balance = instance_account.balance + instance.amount
        else:
            instance_account.balance = instance_account.balance - instance.amount        

        instance_account.save()

    def delete(self):
        """
        Se sobreescribe funcion para ajustar balance
        """
        self.balance_adjustment_on_delete(self)
        super().delete()

    class Meta:	
        verbose_name = 'Transacion'
        verbose_name_plural = 'Transaciones'
        ordering = ['date']