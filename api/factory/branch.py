from .base import BaseFactory
from models.branch import Branch

class BranchFactory(BaseFactory):
    def __init__(self):
        super().__init__(Branch)

    # You can also implement your own random list_generator
    # def random_generator(self) -> dict:
    #     pass

    def list_generator(self):
        """
        Override to add custom dataset
        """
        return [{
            'id': 1,
            'name': 'Buyabod Branch',
            'province': 'Marinduque',
            'municipality': 'Sta. Cruz',
            'barangay': 'Buyabod',
        }, {
            'id': 2,
            'name': 'Lipa Branch',
            'province': 'Marinduque',
            'municipality': 'Sta. Cruz',
            'barangay': 'Lipa',
        }, {
            'id': 3,
            'name': 'Sumangga Branch',
            'province': 'Marinduque',
            'municipality': 'Mogpog',
            'barangay': 'Sumangga',
        }, {
            'id': 4,
            'name': 'Santol Branch',
            'province': 'Marinduque',
            'municipality': 'Boac',
            'barangay': 'Santol',
        }, {
            'id': 5,
            'name': 'Tumapon Branch',
            'province': 'Marinduque',
            'municipality': 'Boac',
            'barangay': 'Tumapon',
        }, {
            'id': 6,
            'name': 'Libas Branch',
            'province': 'Marinduque',
            'municipality': 'Buenavista',
            'barangay': 'Libas',
        }, {
            'id': 7,
            'name': 'Mahunig Branch',
            'province': 'Marinduque',
            'municipality': 'Gasan',
            'barangay': 'Mahunig',
        },]
