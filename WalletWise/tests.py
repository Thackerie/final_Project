from django.test import TestCase

from .models import User, Dashboard, Funds, FundsChange, MonthBudget

# Create your tests here.

class ModelsTestCase(TestCase):

    def setUp(self):

        #Create User1 nd related objects
        self.user1 = User.objects.create(username="user1", password="password123")

        #Create dashboard
        self.dashboard1 = Dashboard.objects.create(owner=self.user1)

        #Create monthly Budgets
        self.month1U1 = MonthBudget.objects.create(dashboard=self.dashboard1) 

        #Create Funds objects
        self.funds1U1 = Funds.objects.create(budget=self.month1U1, title="Funds1", amount=2000)
        self.funds2U1 = Funds.objects.create(budget=self.month1U1, title="Funds2", amount=-1000)
        self.funds2U1 = Funds.objects.create(budget=self.month1U1, title="Funds2", amount=50)

        #Create Income objects
        self.income1U1 = FundsChange.objects.create(budget=self.month1U1, title="Income1", amount=500)
        self.income1U1 = FundsChange.objects.create(budget=self.month1U1, title="Income2", amount=200)

        #Create Expenses objects
        self.expense1U1 = FundsChange.objects.create(budget=self.month1U1, title="Expense1", amount=-400)
        self.expense1U1 = FundsChange.objects.create(budget=self.month1U1, title="Expense2", amount=-900)

        #Create User2 and related objects
        self.user2 = User.objects.create(username="user2", password="password123")
        #Create dashboard
        self.dashboard2 = Dashboard.objects.create(owner=self.user2)

        #Create monthly Budgets
        self.month1U2 = MonthBudget.objects.create()
        self.month2U2 = MonthBudget.objects.create()

    def testDashboard(self):
        self.assertTrue(self.dashboard1.isValid())
        self.assertFalse(self.dashboard2.isValid())

