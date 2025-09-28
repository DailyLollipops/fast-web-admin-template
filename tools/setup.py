# /// script
# requires-python = '>=3.12'
# dependencies = [
#     'bcrypt[cryptography]',
#     'click',
#     'jinja2',
# ]
# ///
import os
import secrets
from pathlib import Path

import bcrypt
import click
from jinja2 import Template


TEMPLATES_DIR = (Path(__file__).parent / 'templates')


def create_env_file(app_name: str, jaeger_username: str, jaeger_password: str, outfile: str):
    tpl_path = (TEMPLATES_DIR / 'env.j2')
    with open(tpl_path) as f:
        template_content = f.read()

    secret_key = secrets.token_urlsafe(32)
    template = Template(template_content)
    hashed = bcrypt.hashpw(jaeger_password.encode(), bcrypt.gensalt()).decode()
    output = template.render(
        app_name=app_name,
        app_key=secret_key,
        jaeger_username=jaeger_username,
        jaeger_password=jaeger_password,
        jaeger_password_hash=hashed.replace('$', '$$'),
    )

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


def create_compose_shared_file(app_name: str, outfile: str):
    tpl_path = (TEMPLATES_DIR / 'docker-compose.shared.yml.j2')
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

    output = template.render(domain='localhost', prod=False)
    with open(config_path / 'Caddyfile.shared', 'w') as file:
        file.write(output)


@click.group()
def cli():
    pass


@click.command()
@click.argument('app_name')
@click.option('--jaeger-username', prompt=True, help='Jaeger admin username')
@click.option('--jaeger-password', prompt=True, hide_input=True, confirmation_prompt=True, help='Jaeger admin password')
@click.option('--outfile', '-n', default='.env', help='Output file location')
def generate_env(app_name: str, jaeger_username: str, jaeger_password: str, outfile: str):
    create_env_file(app_name, jaeger_username, jaeger_password, outfile)


@click.command()
@click.argument('app_name')
@click.option('--outfile', '-n', default='docker-compose.yml', help='Output file location')
def generate_compose_file(app_name: str, outfile: str):
    create_compose_file(app_name, outfile)


@click.command()
@click.argument('app_name')
@click.option('--outfile', '-n', default='docker-compose.shared.yml', help='Output file location')
def generate_compose_shared_file(app_name: str, outfile: str):
    create_compose_shared_file(app_name, outfile)


@click.command()
def generate_caddy_config():
    create_caddy_file()


@click.command()
@click.argument('app_name')
@click.option('--jaeger-username', prompt=True, help='Jaeger admin username')
@click.option('--jaeger-password', prompt=True, hide_input=True, confirmation_prompt=True, help='Jaeger admin password')
def bootstrap(app_name: str, jaeger_username: str, jaeger_password: str):
    create_env_file(app_name, jaeger_username, jaeger_password, '.env')
    create_compose_file(app_name, 'docker-compose.yml')
    create_compose_shared_file(app_name, 'docker-compose.shared.yml')
    create_caddy_file()


@click.command()
@click.option('--username', prompt=True, help='New Jaeger admin username')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='New Jaeger admin password')
@click.option('--env-file', '-f', default='.env', help='Path to .env file')
def update_jaeger_credentials(username: str, password: str, env_file: str):
    env_path = Path(env_file)
    if not env_path.exists():
        raise FileNotFoundError(f'{env_file} not found')

    lines = env_path.read_text().splitlines()
    new_lines = []

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    hashed = hashed.replace('$', '$$')

    for line in lines:
        if line.startswith('JAEGER_USER='):
            new_lines.append(f'JAEGER_USER={username}')
        elif line.startswith('JAEGER_PASSWORD='):
            new_lines.append(f'JAEGER_PASSWORD={password}')
        elif line.startswith('JAEGER_PASSWORD_HASH='):
            new_lines.append(f'JAEGER_PASSWORD_HASH="{hashed}"')
        else:
            new_lines.append(line)

    env_path.write_text('\n'.join(new_lines) + '\n')
    click.echo(f'Updated Jaeger credentials in {env_file}')


cli.add_command(generate_env)
cli.add_command(generate_compose_file)
cli.add_command(generate_compose_shared_file)
cli.add_command(generate_caddy_config)
cli.add_command(bootstrap)
cli.add_command(update_jaeger_credentials)


if __name__ == '__main__':
    cli()
