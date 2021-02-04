from waitress import serve
from result_linker.logger import logger
from result_linker.app import create_app

serve(create_app(config_filename="config.py"), host='0.0.0.0', port=2323, threads = 10)