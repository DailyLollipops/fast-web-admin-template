from .base import BaseFactory
from models.audit import Audit

class AuditFactory(BaseFactory):
    def __init__(self):
        super().__init__(Audit)

    # You can also implement your own random list_generator
    # def random_generator(self) -> dict:
    #     pass

    def list_generator(self):
        """
        Override to add custom dataset
        """
        return []
