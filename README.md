CRYPTO-platform/
│
├── analytics/
│   ├── indicators/
│   ├── statistics/
│   └── reports/
│       └── plot_prices.py      # Para graficar Bitcoin
│
├── app/
│   └── dashboard.py            # Graficar el comportamiento de las monedas          
│
├── data/
│   ├── features/                   # datos crudos (raw API)
│   ├── processed/                  # datos limpios
│   └── raw/  
│       └── binance /
│           └── BTCUSD.csv      # Donde se guardan los datos de Bitcoin historicos
│
├── exchange_API/
│   └── binance/
│       └── client.py           # Donde se adquieren los datos desde binance       
│
├── jobs/
│   └── fetch_binance_data.py   # El script principal para correr todo el codigo de extraccion
│
├── monitoring/
│   ├── alerts/
│   └── logging/
│
├── processing/
│   ├── cleaning/
│       └── save_raw.py         # Para guardar los datos descargdos
│   ├── transformations/
│   └── feature_engineering/
│
│
├── .gitignore
└── README.md


cd "G:\PYTHON\Proyectos Personales\CRYPTO-platform"
python -m streamlit run app/dashboard.py


1. 📊 Históricos (CSV)
OHLCV
Open Interest
Funding Rate
2. ⚡ Tiempo real
Order Book
Liquidations
3. 🧠 Derivados
Volume Profile (lo calculas tú)



*1. 📊 Volume Profile
No solo volumen total, sino volumen por precio
Te permite detectar:
Zonas donde el mercado “acepta” precio (soporte/resistencia real)
👉 Endpoint útil:
aggTrades o reconstrucción desde trades


*2. 📉 Order Book (profundidad de mercado)
Órdenes de compra/venta en tiempo real
Te da:
Zonas de liquidez
“muros” de compra/venta
👉 Endpoint:
/api/v3/depth

*3. 📈 Open Interest (si usas futuros)
Cuánto dinero hay en posiciones abiertas
Te permite detectar:
Acumulación
Posibles liquidaciones
👉 Endpoint (futuros):
/fapi/v1/openInterest

*4. 💥 Liquidations (MUY potente)
Dónde están siendo liquidados traders
Te da:
Zonas donde el precio “va a buscar liquidez”

*5. 📊 Funding Rate (futuros)
Sentimiento del mercado
Muy positivo → mercado sobrecomprado
Muy negativo → sobrevendido

===ESTADISTICAS===
🔵 MA 20 (rápida)
Sigue el precio muy de cerca
Detecta cambios rápidos
Son medias móviles (Moving Averages):
MA 20 → promedio de los últimos 20 periodos
MA 50 → promedio de los últimos 50 periodos
👉 En tu caso (1H):
MA 20 = últimas 20 horas
MA 50 = últimas 50 horas

🟣 MA 50 (lenta)
Más estable
Define tendencia general

📊 Interpretación clave
📈 Tendencia alcista
Precio arriba de ambas
MA20 encima de MA50
👉 Mercado fuerte

📉 Tendencia bajista
Precio debajo de ambas
MA20 debajo de MA50
👉 Mercado débil

⚠️ Mercado lateral
Las líneas se cruzan constantemente
Precio las atraviesa todo el tiempo
👉 No hay dirección clara (zona peligrosa)




🔥 1. VWAP (OBLIGATORIO)
Precio promedio ponderado por volumen
Te dice:
Precio “justo” del mercado
🟢 Precio por ENCIMA de VWAP
👉 mercado “caro”
compradores dominan
presión alcista
💡 institucionales:
no les gusta comprar aquí

🔴 Precio por DEBAJO de VWAP
👉 mercado “barato”
vendedores dominan
presión bajista
💡 institucionales:
buscan comprar aquí

⚖️ Precio CERCA del VWAP
👉 equilibrio
mercado justo
zona de consenso






🔥 2. Bandas de volatilidad (tipo Bollinger)
En vez de solo líneas:
Media
desviación estándar
desviación estándar
Te da:
Zonas dinámicas de sobrecompra/sobreventa

🔥 3. ATR (Average True Range)
Mide volatilidad real
Te sirve para:
Saber si un movimiento es “grande” o normal
Ajustar stops automáticamente

🔥 4. Zonas de soporte/resistencia reales
No promedios → zonas
Cómo hacerlo:
Agrupar precios donde hay:
muchos rebotes
alto volumen

🔥 5. Market Structure (MUY PRO)
Ya empezaste con swings… ahora mejora:
Detecta:
Higher High (HH)
Higher Low (HL)
Lower High (LH)
Lower Low (LL)
👉 Eso te dice tendencia REAL