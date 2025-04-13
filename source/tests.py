import unittest
import os
from source.database import Database
import sqlite3
from source.transactions import TransactionManager

class TestTransactions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_db = 'test_finance.db'
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
        
        cls.db = Database()
        cls.db.conn = sqlite3.connect(cls.test_db)
        cls.db._init_db()
        
        cls.db.add_user('testuser', 'testpass')
        cls.user_id = 1 
    
    def test_add_transaction(self):
        tm = TransactionManager(self.user_id)
        tm.add_transaction('income', 'salary', 1000)
        transactions = tm.get_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0][3], 'salary')
    
    @classmethod
    def tearDownClass(cls):
        cls.db.conn.close()
        os.remove(cls.test_db)

if __name__ == '__main__':
    unittest.main()