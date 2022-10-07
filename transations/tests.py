import random
from random import randrange

from django.test import TestCase
from django.urls import reverse
from django.utils.crypto import get_random_string

from datetime import timedelta
from datetime import datetime

from transations.models import AccountModel, TransactionModel

from rest_framework import status
from rest_framework.test import APITestCase


def random_date(start=datetime.strptime('1/1/2020', '%m/%d/%Y'), end=datetime.strptime('1/1/2023', '%m/%d/%Y')):
    """
    Funcion para generar fecha aleatoria dentro de un rango de fechas
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


def create_random_list_account():
    """
    funcion para crear lista de cuentas random
    """
    instance_account =[AccountModel(
        name=get_random_string(length=32),
        balance=random.randint(1, 389)
    ) for pos in range(100)]
    return AccountModel.objects.bulk_create(instance_account)


def create_random_list_transation(account_list):
    """
    Funcion para crear lista de transaciones random
    """
    instance_transation = [TransactionModel(
        amount=random.randint(1, 389),
        description=get_random_string(length=100),
        date=random_date(),
        income=True,
        account=random.choice(account_list)
    ) for pos in range(100)]

    return TransactionModel.objects.bulk_create(instance_transation)


class AccountModelTest(TestCase):
    """
    Test para el modelo de cuentas
    """

    def test_create(self):
        """
        test de creacion de cuentas
        """
        instance = create_random_list_account()
        self.assertEqual(len(instance), 100)

    def test_update(self):
        """
        test actualizacion de cuentas
        """
        instance = create_random_list_account()
        name_update = get_random_string(length=32)
        instance[0].name = name_update
        instance[0].save()
        self.assertEqual(instance[0].name, name_update)

    def test_delete(self):
        """
        test eliminacion de cuentas
        """
        instance = create_random_list_account()
        instance[0].delete()
        self.assertEqual(instance[0].id, None)


class TransactionModelTest(TestCase):
    """
    Test para el modelo transation
    """

    def test_create(self):
        """
        test para probar la creacion de transaciones
        """
        instance_account = create_random_list_account()
        instance_transation = create_random_list_transation(instance_account)        
        self.assertEqual(len(instance_account), 100)
        self.assertEqual(len(instance_transation), 100)

    def test_update(self):
        """
        test para probar la actualizacion de transaciones
        """
        instance_account = create_random_list_account()
        instance_transation = create_random_list_transation(instance_account)
        new_amount = random.randint(1, 389)
        new_desctiption = get_random_string(length=100)
        new_income = True
        instance_transation[0].amount=new_amount
        instance_transation[0].description=new_desctiption
        instance_transation[0].income=new_income
        instance_transation[0].save()
        self.assertEqual(instance_transation[0].amount, new_amount)
        self.assertEqual(instance_transation[0].description, new_desctiption)
        self.assertEqual(instance_transation[0].income, new_income)


    def test_delete(self):
        """
        test para probar la actualizacion de transaciones
        """
        instance_account = create_random_list_account()
        instance_transation = create_random_list_transation(instance_account)
        instance_transation[0].delete()
        self.assertEqual(instance_transation[0].id, None)


class AccountViewSetTest(APITestCase):
    """
    Test para la vista de cuentas
    """
    def test_list_account(self):
        """
        test para obtener la lista de cuentas cuando hay datos
        """
        instance_list_account = create_random_list_account()
        url = reverse('account-list')
        response = self.client.get(url, {}, format='json')        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 100)
        self.assertEqual([i for i in response.data[0]], ["id", "name", "balance"])
    
    def test_list_account_no_data(self):
        """
        test para probar la lista de cuentas cuando no hay datos
        """
        url = reverse('account-list')
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])
    
    def test_create_account_no_data(self):
        """
        test para probar la creacion sin datos de las cuentas
        """
        url = reverse('account-list')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["name"][0].title(), 'Este Campo Es Requerido.')
        self.assertEqual(response.data["balance"][0].title(), 'Este Campo Es Requerido.')

    def test_create_account(self):
        """
        test para probar la creacion correcta de las cuentas
        """
        url = reverse('account-list')
        name = get_random_string(length=32)
        data = {        
            'name': name,
            'balance':random.randint(1, 389)
        }
        response = self.client.post(url, data, format='json')   
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], data["name"])
        self.assertEqual(float(response.data["balance"]), data["balance"])

    def test_update_account(self):
        """
        test para probar la actualizacion de las cuentas
        """
        list_account = create_random_list_account()
        url = reverse('account-list') + "{}/".format(random.choice(list_account).id)
        new_balance_account = random.randint(1, 389)
        response_update = self.client.put(url, {
            "name": "rename",
            "balance": new_balance_account
        }, format='json')      
        self.assertEqual(response_update.status_code, status.HTTP_200_OK)
        self.assertEqual(response_update.data["name"], "rename")
        self.assertEqual(float(response_update.data["balance"]), float(new_balance_account))

    def test_delete_account(self):
        """
        test para probar la actualizacion
        """
        list_account = create_random_list_account()
        url = reverse('account-list') + "{}/".format(random.choice(list_account).id)
        response_update = self.client.delete(url, {}, format='json')        
        self.assertEqual(response_update.status_code, status.HTTP_204_NO_CONTENT)


class TransationViewSetTest(APITestCase):
    """
    test para probar las transaciones
    """

    def test_list_transation(self):
        """
        test para obtener la lista de transaciones creadas para las cuentas
        """
        list_account = create_random_list_account()
        list_transations = create_random_list_transation(list_account)

        url = reverse('account-list')
        response = self.client.get(url, {}, format='json')        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 100)

    def test_create_deposit_transaction(self):
        """
        test para crear una transacion de deposito
        """
        list_account = create_random_list_account()

        account = random.choice(list_account)
        
        data = {
            'amount': 200,
            'description': get_random_string(length=100),
            'date': random_date().strftime("%Y-%m-%d"),
            'income': True,
            'account': account.id
        }

        url = reverse('transaction-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(account.balance+200, float(AccountModel.objects.get(id=account.id).balance))


    def test_create_withdrawal_transaction_without_balance(self):
        """
        test para crear una transacion de retiro sin saldo
        """
        list_account = create_random_list_account()

        data = {
            'amount': 2000,
            'description': get_random_string(length=100),
            'date': random_date().strftime("%Y-%m-%d"),
            'income': False,
            'account': random.choice(list_account).id
        }

        url = reverse('transaction-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0].title(), 'El Balance A Retirar No Puede Ser Mayor Al Disponible')
    
    def test_create_withdrawal_transaction(self):
        """
         test para crear una transacion de retiro con saldo
        """
        list_account = create_random_list_account()
        
        account = random.choice(list_account)
        
        data = {
            'amount': 1,
            'description': get_random_string(length=100),
            'date': random_date().strftime("%Y-%m-%d"),
            'income': False,
            'account': account.id
        }

        url = reverse('transaction-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(account.balance-1, float(AccountModel.objects.get(id=account.id).balance))


    def test_delete_transation(self):
        """
        test para eliminar una transacion
        """
        list_account = create_random_list_account()
        list_transation = create_random_list_transation(list_account)
        url = reverse('transaction-list') + "{}/".format(random.choice(list_transation).id)
        response = self.client.delete(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

