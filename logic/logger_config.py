# logic/logger_config.py
import logging
import os

def setup_logging():
    """
    Configura o sistema de logging para a aplicação.

    Cria um ficheiro de log chamado 'app.log' no diretório principal
    e formata as mensagens para incluir data, hora, nível e a mensagem.
    """
    # Garante que o diretório de logs existe (opcional)
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Configuração básica do logging
    logging.basicConfig(
        level=logging.INFO,  # Nível mínimo de mensagens a serem registadas
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(os.path.join(log_directory, "app.log")),
            logging.StreamHandler()  # Para também mostrar no terminal
        ]
    )