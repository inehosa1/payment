from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class AccountModel(models.Model):
    """
    Modelo para cuentas
    """
    name = models.CharField("Nombre de cuenta", max_length=50)
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

    class Meta:	
        verbose_name = 'Transacion'
        verbose_name_plural = 'Transaciones'
        ordering = ['date']