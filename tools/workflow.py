# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
#     "jinja2",
#     "textblob",
# ]
# ///
import importlib.util
import inspect
import subprocess
from pathlib import Path

import click
from jinja2 import Environment
from textblob import TextBlob


BASE_PATH = Path(__file__).parent.parent
ROUTES_DIR = (BASE_PATH / 'api' / 'routes')
MODELS_DIR = (BASE_PATH / 'api' / 'database' / 'models')
FACTORY_DIR = (BASE_PATH / 'api' / 'database' / 'factory')
TEMPLATES_DIR = (BASE_PATH / 'tools' / 'templates')


def get_model_from_model_files(model: str):
    module_file = model.lower() + '.py'
    module_path = (MODELS_DIR / module_file)
    model_name = ''.join(word.capitalize() for word in model.split('_'))
    spec = importlib.util.spec_from_file_location(model.lower(), module_path)
    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec) # type: ignore
    spec.loader.exec_module(module)
    classes = {
        name: obj
        for name, obj in inspect.getmembers(module, inspect.isclass)
        if obj.__module__ == module.__name__
    }
    model_cls = classes.get(model_name)
    if not model_cls:
        raise Exception(f'No class named {model_name}')

    return model_cls


@click.group()
def cli():
    pass


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
    built_ins = ['user', 'notification', 'application_setting', 'role_access_control']
    if model in built_ins:
        raise Exception('Cannot generate routes for built in models')

    route_name = TextBlob(model.lower()).words[0].pluralize() # type: ignore
    model_cls = get_model_from_model_files(model)

    template_file = (TEMPLATES_DIR / 'crud_template.py.j2')
    with open(template_file) as f:
        template_content = f.read()

    env = Environment()
    template = env.from_string(template_content)
    output = template.render(
        module=model.lower(),
        model=model_cls,
        route_name=route_name,
        create_login_required=create_login_required,
        read_login_required=read_login_required,
        update_login_required=update_login_required,
        delete_login_required=delete_login_required
    )

    output_path = (ROUTES_DIR / f'{model}.py')
    with open(output_path, 'w') as file:
        file.write(output)

    rules = ['I001']
    cmd = ['uv', 'run', 'ruff', 'check']
    for rule in rules:
        cmd.extend(['--select', rule])
    cmd.extend(['--fix', str(output_path.resolve())])
    subprocess.run(cmd, cwd=BASE_PATH, check=True)


@click.command()
@click.argument('model')
def generate_model_factory(model: str):
    template_file = (TEMPLATES_DIR / 'factory.py.j2')
    with open(template_file) as f:
        template_content = f.read()
    
    model_cls = get_model_from_model_files(model)

    env = Environment()
    template = env.from_string(template_content)
    output = template.render(
        model=model_cls,
        module=model.lower()
    )

    output_path = (FACTORY_DIR / f'{model}.py')
    with open(output_path, "w") as file:
        file.write(output)


cli.add_command(generate_model_route)
cli.add_command(generate_model_factory)


if __name__ == '__main__':
    cli()
