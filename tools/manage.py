import importlib
import os
import secrets
import subprocess
import sys

import click
from jinja2 import Environment, Template
from sqlmodel import SQLModel
from textblob import TextBlob


sys.path.append(os.path.dirname(os.path.dirname(__file__)))

def create_env_file(app_name: str, outfile: str):
    app_key = secrets.token_hex(32)
    with open('tools/templates/env.j2') as f:
        template_content = f.read()

    template = Template(template_content)
    output = template.render(app_name=app_name, app_key=app_key)

    with open(outfile, "w") as file:
        file.write(output)

def create_compose_file(app_name: str, outfile: str):
    with open('tools/templates/docker-compose.yml.j2') as f:
        template_content = f.read()

    template = Template(template_content)
    output = template.render(app_name=app_name)

    with open(outfile, "w") as file:
        file.write(output)

def create_caddy_file(app_name: str, domain: str, outfile: str):
    with open('tools/templates/Caddyfile.j2') as f:
        template_content = f.read()

    template = Template(template_content)
    output = template.render(app_name=app_name, domain=domain)

    with open(outfile, "w") as file:
        file.write(output)


@click.group()
def cli():
    pass


@click.command()
@click.argument('app_name')
@click.option('--outfile', '-n', default='.env', help='Output file location')
def generate_env(app_name: str, outfile: str):
    create_env_file(app_name, outfile)


@click.command()
@click.argument('app_name')
@click.option('--outfile', '-n', default='docker-compose.yml', help='Output file location')
def generate_compose_file(app_name: str, outfile: str):
    create_compose_file(app_name, outfile)


@click.command()
@click.argument('app_name')
@click.option('-d', '--domain', default=':80', help='Domain, localhost default')
@click.option('--outfile', '-n', default='Caddyfile.conf', help='Output file location')
def generate_caddy_config(app_name: str, domain: str, outfile: str):
    create_caddy_file(app_name, domain, outfile)


@click.command()
@click.argument('app_name')
@click.option('-d', '--domain', default=':80', help='Domain, localhost default')
def bootstrap(app_name: str, domain: str):
    create_env_file(app_name, '.env')
    create_compose_file(app_name, 'docker-compose.yml')
    create_caddy_file(app_name, domain, 'Caddyfile.conf')


@click.command()
@click.argument('message')
def create_migration(message: str):
    result = subprocess.run([
        'docker',
        'compose',
        'exec',
        'api',
        'alembic',
        'revision',
        '--autogenerate',
        '-m',
        message
    ], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)


@click.command()
def run_migration():
    result = subprocess.run([
        'docker',
        'compose',
        'exec',
        'api',
        'alembic',
        'upgrade',
        'head',
    ], capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)


@click.command()
@click.argument('model')
@click.option('--create-login-required', '-clr', is_flag=True, default=False, help='Require login for CREATE route')
@click.option('--read-login-required', '-rlr', is_flag=True, default=False, help='Require login for READ route')
@click.option('--update-login-required', '-ulr', is_flag=True, default=False, help='Require login for UPDATE route')
@click.option('--delete-login-required', '-dlr', is_flag=True, default=False, help='Require login for DELETE route')
def generate_model_route(
    model: str,
    create_login_required: bool,
    read_login_required: bool,
    update_login_required: bool,
    delete_login_required: bool
):
    built_ins = ['user', 'notification']
    if model in built_ins:
        raise Exception('Cannot generate routes for built in models')

    module_name = model.lower()
    module = importlib.import_module(f'api.models.{module_name}')
    model_name = ''.join(word.capitalize() for word in model.split('_'))
    model: SQLModel = getattr(module, model_name)
    route_name = TextBlob(module_name).words[0].pluralize()

    with open('tools/templates/crud_template.py.j2') as f:
        template_content = f.read()

    def getattr_filter(obj, attr, default=None):
        return getattr(obj, attr, default)

    env = Environment()
    env.filters["getattr"] = getattr_filter
    template = env.from_string(template_content)
    output = template.render(
        module=module_name,
        model=model,
        route_name=route_name,
        create_login_required=create_login_required,
        read_login_required=read_login_required,
        update_login_required=update_login_required,
        delete_login_required=delete_login_required
    )

    with open(f"api/routes/{module_name}.py", "w") as file:
        file.write(output)


@click.command()
@click.argument('model')
def generate_model_factory(
    model: str,
):
    with open('tools/templates/factory.py.j2') as f:
        template_content = f.read()

    def getattr_filter(obj, attr, default=None):
        return getattr(obj, attr, default)
    
    module_name = model.lower()
    module = importlib.import_module(f'api.models.{module_name}')
    model_name = ''.join(word.capitalize() for word in model.split('_'))
    model: SQLModel = getattr(module, model_name)
    env = Environment()
    env.filters["getattr"] = getattr_filter
    template = env.from_string(template_content)
    output = template.render(model=model, module=module_name)
    with open(f"api/factory/{module_name}.py", "w") as file:
        file.write(output)


@click.command()
@click.argument('from_generator')
@click.option('-n', '--num', default=None, help='Seed n number of models')
@click.option('--no-override', is_flag=True, default=True, help='Dont save if table has data')
@click.option('--only', multiple=True, help='Only seed specific models')
def seed(from_generator, num, no_override, only):
    """
    Seed database

    :param from_generator: data seed generator (can be `random` or `list`)
    """
    cmd = [
        'docker',
        'compose',
        'exec',
        'api',
        'python',
        'seeder.py',
        f'seed-{from_generator}',
    ]
    if num:
        cmd.extend(['-n', num])
    if not no_override:
        cmd.append('--no-override')
    if only:
        for o in only:
            cmd.extend(['--only', o])
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)


cli.add_command(generate_env)
cli.add_command(generate_compose_file)
cli.add_command(generate_caddy_config)
cli.add_command(bootstrap)
cli.add_command(create_migration)
cli.add_command(run_migration)
cli.add_command(generate_model_route)
cli.add_command(generate_model_factory)
cli.add_command(seed)

if __name__ == '__main__':
    cli()
