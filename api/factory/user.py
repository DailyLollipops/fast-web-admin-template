from .base import BaseFactory
from models.user import User

class UserFactory(BaseFactory):
    def __init__(self):
        super().__init__(User)

    # You can also implement your own random list_generator
    # def random_generator(self) -> dict:
    #     pass

    def list_generator(self):
        """
        Override to add custom dataset
        """
        return [{
            'email': 'owner@petromaxx.com',
            'password': '$2b$12$vLK.RU0oqJhzxIcevxkf/.HSZJm0uUvgzb8PQKQjpHaiDEN47zxg6', # password
            'name': 'Owner',
            'role': 'owner',
            'verified': True,
        }, {
            'email': 'superadmin@petromaxx.com',
            'password': '$2b$12$vLK.RU0oqJhzxIcevxkf/.HSZJm0uUvgzb8PQKQjpHaiDEN47zxg6', # password
            'name': 'Super Admin',
            'role': 'admin',
            'verified': True,
        }, {
            'email': 'admininvetory@petromaxx.com',
            'password': '$2b$12$vLK.RU0oqJhzxIcevxkf/.HSZJm0uUvgzb8PQKQjpHaiDEN47zxg6', # password
            'name': 'Inventory Admin',
            'role': 'admin_inventory',
            'verified': True,
        }, {
            'email': 'adminsales@petromaxx.com',
            'password': '$2b$12$vLK.RU0oqJhzxIcevxkf/.HSZJm0uUvgzb8PQKQjpHaiDEN47zxg6', # password
            'name': 'Sales Admin',
            'role': 'admin_sales',
            'verified': True,
        }, {
            'email': 'pumpattendant.01@petromaxx.com',
            'password': '$2b$12$vLK.RU0oqJhzxIcevxkf/.HSZJm0uUvgzb8PQKQjpHaiDEN47zxg6', # password
            'name': 'Pump Attendant 1',
            'role': 'pump_attendant',
            'verified': True,
        }, {
            'email': 'pumpattendant.02@petromaxx.com',
            'password': '$2b$12$vLK.RU0oqJhzxIcevxkf/.HSZJm0uUvgzb8PQKQjpHaiDEN47zxg6', # password
            'name': 'Pump Attendant 2',
            'role': 'pump_attendant',
            'verified': True,
        }, {
            'email': 'pumpattendant.03@petromaxx.com',
            'password': '$2b$12$vLK.RU0oqJhzxIcevxkf/.HSZJm0uUvgzb8PQKQjpHaiDEN47zxg6', # password
            'name': 'Pump Attendant 3',
            'role': 'pump_attendant',
            'verified': True,
        }, {
            'email': 'pumpattendant.04@petromaxx.com',
            'password': '$2b$12$vLK.RU0oqJhzxIcevxkf/.HSZJm0uUvgzb8PQKQjpHaiDEN47zxg6', # password
            'name': 'Pump Attendant 4',
            'role': 'pump_attendant',
            'verified': True,
        }]
