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

    Args:
        start (datetime, optional): Fecha de inicio de rango. por defecto: datetime.strptime('1/1/2020', '%m/%d/%Y').
        end (datetime, optional): Fecha de fin de rango. por defecto: datetime.strptime('1/1/2023', '%m/%d/%Y').

    Returns:
        datetime: fecha aleatoria generada dentro del rango
    """
    
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


def create_random_list_account(number_records=100):
    """
    Funcion para crear lista de cuentas random

    Args:
        number_records (int, optional): numero de registros a generar. por defecto: 100.

    Returns:
        (list, AccountModel): retorna una lista de instancias creadas
    """
    instance_account =[AccountModel(
        name=get_random_string(length=32),
        balance=random.randint(1, 389)
    ) for pos in range(number_records)]
    return AccountModel.objects.bulk_create(instance_account)


def create_random_list_transation(account_list, number_records=100):
    """ 
    Funcion para crear lista de transaciones random

    Args:
        account_list (list, AccountModel): lista de instancias de tipo account list
        number_records (int, optional): numero de registros a crear. Por defecto: 100.

    Returns:
        (list, TransactionModel): retorna una lista de instancias creadas 
    """
    instance_transation = [TransactionModel(
        amount=random.randint(1, 389),
        description=get_random_string(length=100),
        date=random_date(),
        income=True,
        account=random.choice(account_list)
    ) for pos in range(number_records)]
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
        create_random_list_account()
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
        response = self.client.put(url, {
            "name": "rename",
            "balance": new_balance_account
        }, format='json')      
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "rename")
        self.assertEqual(float(response.data["balance"]), float(new_balance_account))

    def test_delete_account(self):
        """
        test para probar la actualizacion
        """
        list_account = create_random_list_account()
        url = reverse('account-list') + "{}/".format(random.choice(list_account).id)
        response = self.client.delete(url, {}, format='json')        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_account_transaction_history(self):
        """
        test para verificar que se este creando el balance inicial al crear la cuenta
        """
        url = reverse('account-list')
        data = {        
            'name': get_random_string(length=32),
            'balance':random.randint(1, 389)
        }
        response = self.client.post(url, data, format='json') 
        url = reverse('account-list') + "{}/account_transaction_history/".format(response.data["id"])
        response_transaction_history = self.client.get(url, {}, format='json')  
        self.assertEqual(response_transaction_history.status_code, status.HTTP_200_OK)
        self.assertEqual([key for key in response_transaction_history.data["account_transaction"][0].keys()], ['id', 'amount', 'description', 'date', 'income', 'account'])
        self.assertEqual(response_transaction_history.data["account_transaction"][0]["description"], 'balance inicial')
        self.assertEqual(float(response_transaction_history.data["account_transaction"][0]["amount"]), float(data["balance"]))

    def test_account_transaction_amount(self):
        """
        test para transferir dinero de una cuenta a otra
        """
        url = reverse('account-list')
        account_one_data = {        
            'name': get_random_string(length=32),
            'balance':random.randint(1, 389)
        }
        account_one_response = self.client.post(url, account_one_data, format='json') 

        account_two_data = {        
            'name': get_random_string(length=32),
            'balance':random.randint(1, 389)
        }
        account_two_response = self.client.post(url, account_two_data, format='json')

        send_to_accountdata = {
            'from_account': account_one_response.data["id"],
            'to_account': account_two_response.data["id"], 
            'amount': account_one_data["balance"]
        }

        # se transfiere el monto
        url_transfer = reverse('account-list') + "account_transaction_amount/"        
        response_transfer = self.client.post(url_transfer, send_to_accountdata, format='json')
        self.assertEqual(response_transfer.status_code, status.HTTP_200_OK)
        self.assertEqual(response_transfer.data["message"], 'transferencia exitosa')

        # se valida que haya quedado registrada la transferencia en el remitente
        account_one_url_history = reverse('account-list') + "{}/account_transaction_history/".format(account_one_response.data["id"])
        account_one_response_transaction_history = self.client.get(account_one_url_history, {}, format='json')  
        self.assertEqual(account_one_response_transaction_history.status_code, status.HTTP_200_OK)
        self.assertEqual(len(account_one_response_transaction_history.data["account_transaction"]), 2)
        
        # se valida que haya quedado registrada la transferencia en el destino
        account_two_url_history = reverse('account-list') + "{}/account_transaction_history/".format(account_two_response.data["id"])
        account_two_response_transaction_history = self.client.get(account_two_url_history, {}, format='json')  
        self.assertEqual(account_two_response_transaction_history.status_code, status.HTTP_200_OK)
        self.assertEqual(len(account_two_response_transaction_history.data["account_transaction"]), 2)


class TransationViewSetTest(APITestCase):
    """
    test para probar las transaciones
    """

    def test_list_transation(self):
        """
        test para obtener la lista de transaciones creadas para las cuentas
        """
        list_account = create_random_list_account()
        create_random_list_transation(list_account)

        url = reverse('transaction-list')
        response = self.client.get(url, {}, format='json')        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 100)

    def test_list_transation_filter_account(self):
        """
        test para obtener la lista de transaciones filtradas por una cuenta
        """
        list_account = create_random_list_account()
        list_transation = create_random_list_transation(list_account)

        url = reverse('transaction-list')
        account = random.choice(list_transation).account.id
        response = self.client.get(url, {"account": account}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)        
        self.assertEqual(set([i["account"] for i in response.data]), {account})
    
    def test_list_transation_filter_year(self):
        """
        test para obtener la lista de transaciones filtradas por un año
        """
        list_account = create_random_list_account()
        list_transation = create_random_list_transation(list_account)

        url = reverse('transaction-list')
        year = random.choice(list_transation).date.year
        response = self.client.get(url, {"date__year": year}, format='json')        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set([datetime.strptime(i["date"], "%Y-%m-%d").year for i in response.data]), {year})

    def test_list_transation_filter_month(self):
        """
        test para obtener la lista de transaciones filtradas por un mes
        """
        list_account = create_random_list_account()
        list_transation = create_random_list_transation(list_account)

        url = reverse('transaction-list')
        month = random.choice(list_transation).date.month
        response = self.client.get(url, {"date__month": month}, format='json')        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(set([datetime.strptime(i["date"], "%Y-%m-%d").month for i in response.data]), {month})

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
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

