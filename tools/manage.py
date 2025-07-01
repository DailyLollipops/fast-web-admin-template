from jinja2 import Environment, Template
from sqlmodel import SQLModel
import click
import importlib
import os
import secrets
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))


@click.group()
def cli():
    pass

@click.command()
@click.argument('app_name')
@click.option('--outfile', '-n', default='.env', help='Output file location')
def generate_env(app_name: str, outfile: str):
    app_key = secrets.token_hex(32)
    with open('tools/templates/env.j2', 'r') as f:
        template_content = f.read()

    template = Template(template_content)
    output = template.render(app_name=app_name, app_key=app_key)

    with open(outfile, "w") as file:
        file.write(output)

@click.command()
@click.argument('app_name')
@click.option('--outfile', '-n', default='docker-compose.yml', help='Output file location')
def generate_compose_file(app_name: str, outfile: str):
    with open('tools/templates/docker-compose.yml.j2', 'r') as f:
        template_content = f.read()

    template = Template(template_content)
    output = template.render(app_name=app_name)

    with open(outfile, "w") as file:
        file.write(output)

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

    with open('tools/templates/crud_template.py.j2', 'r') as f:
        template_content = f.read()

    def getattr_filter(obj, attr, default=None):
        return getattr(obj, attr, default)

    env = Environment()
    env.filters["getattr"] = getattr_filter
    template = env.from_string(template_content)
    output = template.render(
        module=module_name,
        model=model,
        create_login_required=create_login_required,
        read_login_required=read_login_required,
        update_login_required=update_login_required,
        delete_login_required=delete_login_required
    )

    with open(f"api/routes/{module_name}.py", "w") as file:
        file.write(output)

cli.add_command(generate_env)
cli.add_command(generate_compose_file)
cli.add_command(generate_model_route)

if __name__ == '__main__':
    cli()
