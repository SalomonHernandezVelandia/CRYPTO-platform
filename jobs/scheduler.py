import time

from apscheduler.schedulers.background import BackgroundScheduler

from jobs.fetch_binance_data import main as fetch_data
from alerts.telegram.listener import check_telegram_updates
from jobs.run_fast_alerts import run_fast_alerts


# ==========================================
# SCHEDULER
# ==========================================
scheduler = BackgroundScheduler()


# ==========================================
# DESCARGAR + ANALIZAR
# ==========================================
scheduler.add_job(
    fetch_data,
    "interval",
    hours=2
)


# ==========================================
# ESCUCHAR TELEGRAM
# ==========================================
scheduler.add_job(
    check_telegram_updates,
    "interval",
    seconds=30
)


# ==========================================
# ALERTAS RÁPIDAS
# ==========================================
scheduler.add_job(
    run_fast_alerts,
    "interval",
    minutes=15
)


# ==========================================
# EJECUCIÓN INMEDIATA AL INICIAR
# ==========================================
print("🚀 Primera actualización inmediata...")

fetch_data()

print("✅ Primera actualización completada")


# ==========================================
# START SCHEDULER
# ==========================================
scheduler.start()

print("🚀 Scheduler iniciado...")


# Mantener vivo
while True:
    time.sleep(60)