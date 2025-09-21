# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
#     "jinja2",
# ]
# ///
import os
import secrets
from pathlib import Path

import click
from jinja2 import Template


TEMPLATES_DIR = (Path(__file__).parent / 'templates')


def create_env_file(app_name: str, outfile: str):
    tpl_path = (TEMPLATES_DIR / 'env.j2')
    with open(tpl_path) as f:
        template_content = f.read()

    secret_key = secrets.token_urlsafe(32)
    template = Template(template_content)
    output = template.render(app_name=app_name, app_key=secret_key)

    with open(outfile, 'w') as file:
        file.write(output)


def create_compose_file(app_name: str, outfile: str):
    tpl_path = (TEMPLATES_DIR / 'docker-compose.yml.j2')
    with open(tpl_path) as f:
        template_content = f.read()

    template = Template(template_content)
    output = template.render(app_name=app_name)

    with open(outfile, 'w') as file:
        file.write(output)


def create_caddy_file():
    tpl_path = (TEMPLATES_DIR / 'Caddyfile.j2')
    config_path = Path(__file__).parent.parent / 'provision' / 'caddy'
    os.makedirs(config_path, exist_ok=True)
    with open(tpl_path) as f:
        template_content = f.read()

    template = Template(template_content)

    output = template.render(domain='localhost', prod=False)
    with open(config_path / 'Caddyfile.local', 'w') as file:
        file.write(output)

    output = template.render(domain='domain.com', prod=True)
    with open(config_path / 'Caddyfile.prod', 'w') as file:
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
def generate_caddy_config():
    create_caddy_file()


@click.command()
@click.argument('app_name')
def bootstrap(app_name: str):
    create_env_file(app_name, '.env')
    create_compose_file(app_name, 'docker-compose.yml')
    create_caddy_file()


cli.add_command(generate_env)
cli.add_command(generate_compose_file)
cli.add_command(generate_caddy_config)
cli.add_command(bootstrap)


if __name__ == '__main__':
    cli()
