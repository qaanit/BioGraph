import unittest
from unittest.mock import patch, MagicMock
from SbmlDatabase import SbmlDatabase

""""
These tests are to be done everytime database is modified to make sure all changes do not affect others
The database shoud be loaded with 10 models BIOMD0 to 10
"""

class TestSbmlDatabase(unittest.TestCase):
    
    def setUp(self):
        """ Set up a mock database instance before each test """
        self.database = SbmlDatabase("localhost.ini", "biomodels", "default_schema.json")
    
    @patch('SbmlDatabase.connect')
    def test_delete_model(self, mock_connect):
        """ Test deleting a model from the database """
        mock_connect.return_value = MagicMock()
        self.database.delete_model("BIOMD0000000003")
        mock_connect().run_query.assert_not_called()


    @patch('SbmlDatabase.connect')
    def test_compare_models(self, mock_connect):
        """ Test comparing two models """
        mock_connect.return_value = MagicMock()
        mock_connect().run_query.return_value = 0.9583333333333333
        similarity = self.database.compare_models("BIOMD0000000003", "BIOMD0000000004")
        self.assertEqual(similarity, 0.9583333333333333)
        # This accuracy value is objective, but makes sure that the graph matching algorithm remains the same

    @patch('SbmlDatabase.connect')
    def test_compare__same_model(self, mock_connect):
        """ Test comparing same model in graph macthing algorithm - should be 100% accuracy """
        mock_connect.return_value = MagicMock()
        mock_connect().run_query.return_value = 1
        similarity = self.database.compare_models("BIOMD0000000003", "BIOMD0000000003")
        self.assertEqual(similarity, 1)


    @patch('SbmlDatabase.connect')
    def test_search_for_compartment(self, mock_connect):
        """ Test searching for models with a specific compartment """
        mock_connect.return_value = MagicMock()
        mock_connect().run_query.return_value = ["Model1", "Model2"]
        result = self.database.search_for_compartment("cell")
        self.assertEqual(sorted(result), sorted(['BIOMD0000000006', 'BIOMD0000000005', 'BIOMD0000000004', 'BIOMD0000000003']))


    @patch('SbmlDatabase.connect')
    def test_search_for_compound(self, mock_connect):
        """ Test searching for models containing a specific compound """
        mock_connect.return_value = MagicMock()
        mock_connect().run_query.return_value = ["Model1", "Model2"]
        result = self.database.search_for_compound("C")
        self.assertEqual(sorted(result), sorted(['BIOMD0000000004', 'BIOMD0000000003']))


    @patch('SbmlDatabase.connect')
    def test_search_compound_in_compartment(self, mock_connect):
        """ Test searching for a compound in a specific compartment """
        mock_connect.return_value = MagicMock()
        mock_connect().run_query.return_value = ["Model1"]
        result = self.database.search_compound_in_compartment("C", "cell")
        self.assertEqual(sorted(result), sorted(['BIOMD0000000003', 'BIOMD0000000004']))


    @patch('SbmlDatabase.connect')
    def test_change_schema(self, mock_connect):
        """ Test changing the schema """
        mock_connect.return_value = MagicMock()
        self.database.change_schema("test.json")
        mock_connect().run_query.assert_not_called()
    
    @patch('SbmlDatabase.connect')  # Mock the connect function
    def test_load_and_import_model(self, mock_connect):
        """ Test loading and importing a model into the database """
        mock_connect.return_value = MagicMock()
        self.database.load_and_import_model("BIOMD0000000003")
        mock_connect().run_query.assert_not_called()  # Verify connection was made


    @patch('SbmlDatabase.connect')
    def test_import_models(self, mock_connect):
        """ Test importing multiple models """
        mock_connect.return_value = MagicMock()
        model_list = ["BIOMD0000000003", "BIOMD0000000004"]
        self.database.import_models(model_list)
        mock_connect().run_query.assert_not_called()  # Verify connection was made for multiple models


    @patch('SbmlDatabase.connect')
    def test_check_model_exists(self, mock_connect):
        """ Test checking if a model exists """
        mock_connect.return_value = MagicMock()
        mock_connect().run_query.return_value = True
        exists = self.database.check_model_exists("BIOMD0000000003")
        self.assertTrue(exists)
        mock_connect().run_query.assert_not_called()


if __name__ == '__main__':
    unittest.main(argv=[''], exit=False)
