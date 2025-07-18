from .base import BaseFactory
from models.machine import Machine

class MachineFactory(BaseFactory):
    def __init__(self):
        super().__init__(Machine)

    # You can also implement your own random list_generator
    # def random_generator(self) -> dict:
    #     pass

    def list_generator(self):
        """
        Override to add custom dataset
        """
        return [{
            'id': 1,
            'branch_id': 1,
            'name': 'Buyabod Machine #1',
        }, {
            'id': 2,
            'branch_id': 1,
            'name': 'Buyabod Machine #2 (Front)',
        }, {
            'id': 3,
            'branch_id': 1,
            'name': 'Buyabod Machine #2 (Back)',
        }, {
            'id': 4,
            'branch_id': 2,
            'name': 'Lipa Machine #1 (Front)',
        }, {
            'id': 5,
            'branch_id': 2,
            'name': 'Lipa Machine #1 (Back)',
        }, {
            'id': 6,
            'branch_id': 3,
            'name': 'Sumangga Machine #1 (Front)',
        }, {
            'id': 7,
            'branch_id': 3,
            'name': 'Sumangga Machine #1 (Back)',
        }, {
            'id': 8,
            'branch_id': 4,
            'name': 'Santol Machine #1 (Front)',
        }, {
            'id': 9,
            'branch_id': 4,
            'name': 'Santol Machine #1 (Back)',
        }, {
            'id': 10,
            'branch_id': 4,
            'name': 'Santol Machine #2',
        }, {
            'id': 11,
            'branch_id': 5,
            'name': 'Tumapon Machine #1',
        }, {
            'id': 12,
            'branch_id': 6,
            'name': 'Libas Machine #1',
        }, {
            'id': 13,
            'branch_id': 7,
            'name': 'Mahunig Machine #1',
        }, {
            'id': 14,
            'branch_id': 7,
            'name': 'Mahunig Machine #2',
        }]
