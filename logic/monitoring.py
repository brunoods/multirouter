"""
Módulo responsável pela monitorização periódica do estado dos dispositivos.
"""

import threading
from logic.connection import get_connection_status


class Monitoring:
    """Gere a tarefa de monitorização de dispositivos em segundo plano."""

    def __init__(self, app, interval=60):
        """
        Inicializa o monitor.

        Args:
            app: A instância principal da aplicação.
            interval (int): O intervalo em segundos entre cada verificação.
        """
        self.app = app
        self.interval = interval
        self.running = False
        self.thread = None

    def start(self):
        """Inicia a monitorização."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print("Monitorização iniciada.")

    def stop(self):
        """Para a monitorização."""
        self.running = False
        if self.thread:
            print("A parar a monitorização...")
            self.thread.join()  # Espera a thread terminar
            print("Monitorização parada.")

    def _run(self):
        """O loop principal que executa a verificação de status."""
        while self.running:
            devices = self.app.inventory_manager.get_devices()
            status_list = []
            for device in devices:
                status = get_connection_status(device)
                status_list.append(f"{device.get('ip')}: {status}")

            # Atualiza a UI na thread principal
            self.app.after(0, self._update_ui, status_list)

            # Espera pelo próximo intervalo (verificando self.running)
            for _ in range(self.interval):
                if not self.running:
                    break
                threading.Event().wait(1)

    def _update_ui(self, status_list):
        """Atualiza a página de visão geral com o status dos dispositivos."""
        overview_page = self.app.pages.get("overview")
        if overview_page:
            overview_page.update_monitoring_status(status_list)
