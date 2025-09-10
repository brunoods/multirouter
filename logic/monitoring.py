# logic/monitoring.py
"""
Módulo para a lógica de monitorização contínua de dispositivos.
"""
import time
import threading
from logic.connection import connect_and_read_config
from logic.alerts_manager import check_alerts

class MonitorThread:
    def __init__(self, app, interval_seconds):
        self.app = app
        self.interval = interval_seconds
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        """O loop que corre em segundo plano."""
        while not self._stop_event.is_set():
            connect_and_read_config(self.app, is_monitoring_thread=True, alert_callback=check_alerts)
            self._stop_event.wait(self.interval)

    def start(self):
        self.thread.start()

    def stop(self):
        self._stop_event.set()

def toggle_monitoring(app):
    """Inicia ou para o ciclo de monitorização."""
    overview_page = app.frames[app.pages["OverviewPage"]]
    
    if not hasattr(app, 'monitoring_thread') or not app.monitoring_thread.thread.is_alive():
        try:
            interval = int(overview_page.interval_entry.get())
            if interval < 10:
                app.status_label.config(text="Intervalo mínimo é 10 segundos.")
                return
        except ValueError:
            app.status_label.config(text="Intervalo inválido. Por favor, insira um número.")
            return

        app.monitoring_thread = MonitorThread(app, interval)
        app.monitoring_thread.start()
        
        overview_page.monitor_button.config(text="Parar Monitorização")
        app.status_label.config(text=f"Monitorização iniciada. A atualizar a cada {interval} segundos.")
    
    else:
        app.monitoring_thread.stop()
        overview_page.monitor_button.config(text="Iniciar Monitorização")
        app.status_label.config(text="Monitorização parada.")