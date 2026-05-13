import time

from apscheduler.schedulers.background import BackgroundScheduler

from jobs.fetch_binance_data import main as fetch_data
from alerts.telegram.listener import check_telegram_updates
from jobs.run_fast_alerts import run_fast_alerts
from jobs.run_signal import run


# ==========================================
# SCHEDULER
# ==========================================
scheduler = BackgroundScheduler()


# ==========================================
# ACTUALIZAR DATOS CADA 15M
# ==========================================
scheduler.add_job(
    fetch_data,
    "interval",
    minutes=15
)


# ==========================================
# FAST ALERTS CADA 15M
# ==========================================
scheduler.add_job(
    run_fast_alerts,
    "interval",
    minutes=15
)


# ==========================================
# SISTEMA COMPLETO CADA 2H
# ==========================================
scheduler.add_job(
    run,
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
# EJECUCIÓN INICIAL
# ==========================================
print("🚀 Primera actualización inmediata...")
# ACTUALIZAR DATOS
fetch_data()
print("✅ Datos actualizados")

# ENVIAR ANÁLISIS COMPLETO INICIAL
print("📊 Ejecutando análisis inicial...")
run()
print("✅ Análisis inicial enviado")


# ==========================================
# START
# ==========================================
scheduler.start()

print("🚀 Scheduler iniciado...")


while True:
    time.sleep(60)