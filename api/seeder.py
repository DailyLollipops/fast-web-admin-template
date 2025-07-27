from sqlmodel import select
import click
import re

from database import get_db
import factory


def snake_to_pascal(s: str) -> str:
    return ''.join(word.capitalize() for word in s.split('_'))


@click.group()
def cli():
    pass


@click.command
@click.option('-n', '--num', default=1, help='Seed n number of models')
@click.option('--no-override', is_flag=True, default=True, help='Dont save if table has data')
@click.option('--only', multiple=True, help='Only seed specific models')
def seed_random(num: int, no_override: bool, only: tuple[str]):
    if only:
        factories: list[factory.BaseFactory] = [
            getattr(factory, f'{snake_to_pascal(f)}Factory')
            for f in only
        ]
    else:
        factories: list[factory.BaseFactory] = [
            getattr(factory, f) 
            for f in factory.__all__ 
            if re.search(r'^(?!Base).+Factory$', f)
        ]

    db = next(get_db())
    all_instances = []
    for f in factories:
        instances = f().make(num)
        print(f'Generated {len(instances)} instances from {f}')
        if instances and no_override:
            if db.exec(select(instances[0].__class__)).first():
                print('Table has populated data and --no-override is set. Skipping seeding...')
                continue
        all_instances.extend(instances)

    if all_instances:
        db.add_all(all_instances)
        db.commit()


@click.command
@click.option('-n', '--num', default=None, help='Seed n number of models')
@click.option('--no-override', is_flag=True, default=True, help='Dont save if table has data')
@click.option('--only', multiple=True, help='Only seed specific models')
def seed_list(num: int, no_override: bool, only: tuple[str]):
    if only:
        factories: list[factory.BaseFactory] = [
            getattr(factory, f'{snake_to_pascal(f)}Factory')
            for f in only
        ]
    else:
        factories: list[factory.BaseFactory] = [
            getattr(factory, f) 
            for f in factory.__all__ 
            if re.search(r'^(?!Base).+Factory$', f)
        ]
    
    db = next(get_db())
    all_instances = []
    for f in factories:
        instances = f().make_from_list(num)
        print(f'Generated {len(instances)} instances from {f}')
        if instances and no_override:
            if db.exec(select(instances[0].__class__)).first():
                print('Table has populated data and --no-override is set. Skipping seeding...')
                continue
        all_instances.extend(instances)
    
    if all_instances:
        db.add_all(all_instances)
        db.commit()

cli.add_command(seed_random)
cli.add_command(seed_list)


if __name__ == '__main__':
    cli()
