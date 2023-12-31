from django.test import TestCase

from .models import User, Dashboard, Funds, FundsChange, MonthBudget

# Create your tests here.

class ModelsTestCase(TestCase):

    def setUp(self):

        #Create User1 nd related objects
        self.user1 = User.objects.create(username="user1", password="password123")

        #Create dashboard 1
        self.dashboard1 = Dashboard.objects.create(owner=self.user1)

        #Create monthly Budgets 1
        self.month1U1 = MonthBudget.objects.create(dashboard=self.dashboard1) 

        #Create Funds objects 1
        self.funds1U1 = Funds.objects.create(budget=self.month1U1, title="Funds1", amount=2000)
        self.funds2U1 = Funds.objects.create(budget=self.month1U1, title="Funds2", amount=-1000)
        self.funds3U1 = Funds.objects.create(budget=self.month1U1, title="Funds3", amount=50)

        #Create Income objects 1
        self.income1U1 = FundsChange.objects.create(budget=self.month1U1, title="Income1", amount=500, is_expense=False, destination_id=1)
        self.income2U1 = FundsChange.objects.create(budget=self.month1U1, title="Income2", amount=200, is_expense=False, destination_id=1)

        #Create Expenses objects 1
        self.expense1U1 = FundsChange.objects.create(budget=self.month1U1, title="Expense1", amount=-400, is_expense=True, destination_id=1)
        self.expense2U1 = FundsChange.objects.create(budget=self.month1U1, title="Expense2", amount=-900, is_expense=True, destination_id=1)



        #Create User2 and related objects
        self.user2 = User.objects.create(username="user2", password="password123")

        #Create dashboard 2
        self.dashboard2 = Dashboard.objects.create(owner=self.user2)

        #Create monthly Budgets 2
        self.month1U2 = MonthBudget.objects.create(dashboard=self.dashboard2)
        self.month2U2 = MonthBudget.objects.create(dashboard=self.dashboard2)

        #Create Funds objects 1
        self.funds1U2 = Funds.objects.create(budget=self.month1U2, title="Funds1", amount=2000)

        #Create Income objects 2 for monthly budget 1U2
        self.income1U2 = FundsChange.objects.create(budget=self.month1U2, title="Income1", amount=500, is_expense=False, destination_id=1)

        #Create INVALID income object
        self.income2U2 = FundsChange.objects.create(budget=self.month1U2, title="Income2", amount=200, is_expense=True, destination_id=1)

        



    def testDashboard(self):
        self.assertTrue(self.dashboard1.isValid())
        self.assertFalse(self.dashboard2.isValid())

    def testBudget1(self):
        #tests if the isValid function works
        self.assertTrue(self.month1U1.isValid())
        self.assertFalse(self.month1U2.isValid())

    def testBudget1(self):
        #test the property functions of the MonthBudget model

        #self.assertEqual(self.month1U1.all_funds, 1050.0)
        self.assertEqual(self.month1U1.total_Expenses, -1300.0)
        self.assertEqual(self.month1U1.total_Income, 700.0)

        #self.assertEqual(self.month1U1.total_Funds, 450.0)