from datetime import datetime
from faker import Faker
from sqlmodel import SQLModel

class BaseFactory:
    def __init__(self, model: type[SQLModel]):
        self.model = model

    def random_generator(self) -> dict:
        faker = Faker()
        faker_methods = [m for m in dir(faker) if not m.startswith('_')]

        data = {}
        for column, info in self.model.model_fields.items():
            if not info.is_required() or info.default_factory:
                continue

            if column in faker_methods:
                method = getattr(faker, column)
                data[column] = method()
                continue

            if info.annotation == str:
                data[column] = faker.text()

            elif info.annotation == int:
                data[column] = faker.random_number()

            elif info.annotation == float:
                data[column] = float(faker.pydecimal())

            elif info.annotation == bool:
                data[column] = faker.boolean()

            elif info.annotation == datetime:
                data[column] = faker.date_time()

        return data

    def list_generator(self) -> list[dict]:
        return []

    def make(self, num: int = 1) -> list[SQLModel]:
        instances = [self.model(**self.random_generator()) for _ in range(num)]
        return instances
    
    def make_from_list(self, num: int | None = None) -> list[SQLModel]:
        data = self.list_generator()
        if not num or num >= len(data):
            return [self.model(**d) for d in data]
        
        return [self.model(**d) for d in data[:num]]


if __name__ == '__main__':
    from sqlmodel import Field

    class Sample(SQLModel):
        id: int = Field(default=None, primary_key=True)
        title: str = Field(...)
        description: str = Field(...)
        latitude: float = Field(...)
        longitude: float = Field(...)
        created_at: datetime = Field(default_factory=lambda: datetime.now())
        updated_at: datetime = Field(
            default_factory=lambda: datetime.now(), 
            sa_column_kwargs={'onupdate': lambda: datetime.now()}
        )

    factory = BaseFactory(Sample)
    model = factory.make(4)
    print(model)
