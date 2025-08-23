# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "aiomysql",
# ]
# ///

# pyright: reportCallIssue=false
import re

import click
from database import factory
from database.engine import get_sync_session
from sqlmodel import select


def snake_to_pascal(s: str) -> str:
    return ''.join(word.capitalize() for word in s.split('_'))


@click.group()
def cli():
    pass


@click.command
@click.option('-n', '--num', default=1, help='Seed n number of models')
@click.option('--force', is_flag=True, default=False, help='Force save data if table has data')
@click.option('--only', multiple=True, help='Only seed specific models')
def seed_random(num: int, force: bool, only: tuple[str] | None = None):
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

    with get_sync_session() as session:
        all_instances = []
        for f in factories:
            instances = f().make(num)
            print(f'Generated {len(instances)} instances from {f}')
            if instances and not force:
                if session.exec(select(instances[0].__class__)).first():
                    print('Table has populated data and --force is not set. Skipping seeding...')
                    continue
            all_instances.extend(instances)

        if all_instances:
            session.add_all(all_instances)
            session.commit()


@click.command
@click.option('-n', '--num', default=None, help='Seed n number of models')
@click.option('--force', is_flag=True, default=False, help='Force save data if table has data')
@click.option('--only', multiple=True, help='Only seed specific models')
def seed_list(num: int, force: bool, only: tuple[str] | None = None):
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
    
    with get_sync_session() as session:
        all_instances = []
        for f in factories:
            instances = f().make_from_list(num)
            print(f'Generated {len(instances)} instances from {f}')
            if instances and not force:
                if session.exec(select(instances[0].__class__)).first():
                    print('Table has populated data and --force is not set. Skipping seeding...')
                    continue
            all_instances.extend(instances)
        
        if all_instances:
            session.add_all(all_instances)
            session.commit()

cli.add_command(seed_random)
cli.add_command(seed_list)


if __name__ == '__main__':
    cli()
