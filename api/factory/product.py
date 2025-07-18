from .base import BaseFactory
from models.product import Product

class ProductFactory(BaseFactory):
    def __init__(self):
        super().__init__(Product)

    def random_generator(self):
        data = super().random_generator()
        data['image'] = 'placeholder'
        return data

    def list_generator(self):
        """
        Override to add custom dataset
        """
        return [{
            'id': 1,
            'name': 'Diesel',
            'description': 'Diesel is a slower-burning fuel type that holds more power than regular gasoline and is typically used in bigger machines or vehicles that require more energy at a lower RPM.',
            'image': 'static/uploads/Diesel.png'
        }, {
            'id': 2,
            'name': 'Premium',
            'description': 'Premium gasoline is a high-octane fuel with an octane rating between 91 and 94, which helps improve fuel efficiency and offers optimal performance for specific vehicles. It typically costs 20 to 50 cents more per gallon than regular gasoline.',
            'image': 'static/uploads/Premium.png'
        }, {
            'id': 3,
            'name': 'Max-Clean',
            'description': 'Max-Clean is a highly concentrated, high performance fuel system cleaner and fuel stabilizer. It is specially formulated to solve problems with today\'s gasoline direct injection (GDI) engines but can be used with any type of fuel injection.',
            'image': 'static/uploads/Max-Clean.png'
        },]
