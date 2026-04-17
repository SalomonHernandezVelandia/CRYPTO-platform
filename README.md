# 📊 Crypto Trading Dashboard & Signal Engine

Este proyecto es una plataforma de análisis de mercado cripto que combina datos históricos, métricas en tiempo real y lógica cuantitativa para generar señales de compra y venta.

---

# 🪙 Activos soportados

Actualmente el sistema trabaja con los siguientes pares:

* BTCUSDT (Bitcoin)
* ETHUSDT (Ethereum)
* XRPUSDT
* SOLUSDT
* DOGEUSDT
* ADAUSDT
* LINKUSDT
* AVAXUSDT
* HBARUSDT
* SHIBUSDT
* PEPEUSDT

---

# 📈 Tendencia (Trend)

La tendencia se calcula usando medias móviles:

* MA 20 (media rápida)
* MA 50 (media lenta)

## Posibles estados:

### 📈 Alcista (bullish)

**Condición:**
MA20 > MA50

**Interpretación:**

* El precio está en una fase de crecimiento
* Mayor probabilidad de continuación al alza
* Favorece compras en retrocesos

---

### 📉 Bajista (bearish)

**Condición:**
MA20 < MA50

**Interpretación:**

* El precio está en caída
* Mayor probabilidad de continuación bajista
* Favorece ventas o evitar compras

---

# 🌍 Contexto de mercado

El sistema clasifica el mercado en 3 estados:

---

### 🔵 Tendencial (trending)

**Condición:**
Movimiento direccional claro

**Interpretación:**

* Mercado con dirección definida
* Estrategias de seguimiento de tendencia funcionan mejor

---

### 🟠 Lateral (ranging)

**Condición:**
Rango estrecho y baja expansión

**Interpretación:**

* Precio se mueve entre soporte y resistencia
* Ideal para comprar en mínimos y vender en máximos

---

### 🔴 Volátil (volatile)

**Condición:**
Alta desviación estándar del precio

**Interpretación:**

* Movimientos bruscos
* Mayor riesgo
* Señales menos confiables

---

# 💰 Funding Rate

## ¿Qué es?

Es el costo que pagan los traders en contratos perpetuos (futuros).

* Lo pagan los LONGS o los SHORTS dependiendo del mercado

## ¿De dónde se obtiene?

* API de Binance (futuros)
* Se guarda en `data/raw/binance/funding_rate/`

---

## Interpretación:

### Funding > 0

👉 Los LONGS pagan a los SHORTS

* Mercado sobrecomprado
* Posible corrección bajista

---

### Funding < 0

👉 Los SHORTS pagan a los LONGS

* Mercado sobrevendido
* Posible rebote alcista

---

### Funding ≈ 0

👉 Mercado neutral

* Sin sesgo claro

---

# 🧪 Métricas de Backtesting

---

## 📊 Retorno (Return)

**Qué es:**
Rentabilidad total del sistema

**Interpretación:**

* Alto → estrategia rentable
* Bajo/negativo → estrategia deficiente

---

## 🎯 Win Rate

**Qué es:**
Porcentaje de operaciones ganadoras

**Interpretación:**

* Alto (>60%) → consistencia
* Bajo → muchas pérdidas

---

## 📉 Drawdown

**Qué es:**
Máxima caída desde un pico

**Interpretación:**

* Alto → alto riesgo
* Bajo → sistema estable

---

## ⚖️ Sharpe Ratio

**Qué es:**
Relación riesgo/retorno

**Interpretación:**

* > 1 → bueno
* > 2 → excelente
* < 1 → débil

---

## 🔄 Trades

**Qué es:**
Número total de operaciones

**Interpretación:**

* Muy alto → sobreoperación
* Muy bajo → pocas oportunidades

---

# 🧠 Sistema de Score (Señales)

El sistema asigna un puntaje basado en múltiples factores:

---

## Factores evaluados:

* Precio vs VWAP
* Tendencia
* Funding Rate
* Order Book
* Posición en rango (soporte/resistencia)

---

## Resultado:

### 🟢 STRONG BUY (score ≥ 3)

Fuerte señal de compra

---

### 🟢 BUY (score ≥ 1)

Señal moderada de compra

---

### 🟡 HOLD (score = 0)

Sin ventaja clara

---

### 🔴 SELL (score ≤ -1)

Señal moderada de venta

---

### 🔴 STRONG SELL (score ≤ -3)

Fuerte señal de venta

---

# 📚 Order Book

## ¿Qué es?

Libro de órdenes en tiempo real:

* Bids → órdenes de compra
* Asks → órdenes de venta

Se obtiene desde:

* API de Binance (`get_order_book`)

---

## Métricas clave

---

### 🟢 Bid Volume

**Qué es:**
Volumen total de órdenes de compra

**Interpretación:**

* Alto → fuerte interés comprador
* Posible soporte

---

### 🔴 Ask Volume

**Qué es:**
Volumen total de órdenes de venta

**Interpretación:**

* Alto → presión vendedora
* Posible resistencia

---

### ⚖️ Imbalance

**Fórmula:**

Imbalance = Bid Volume / (Bid + Ask)

---

## Interpretación:

### > 0.55

🟢 Dominio comprador
→ posible subida

---

### < 0.45

🔴 Dominio vendedor
→ posible caída

---

### 0.45 - 0.55

🟡 Mercado balanceado

---

# 📊 Order Book Depth (Gráfica)

Muestra:

* Línea verde → acumulado de compras
* Línea roja → acumulado de ventas

---

## Cómo leerla:

### 🔼 Paredes grandes (walls)

* Grandes acumulaciones de volumen
* Actúan como soporte o resistencia

---

### 📉 Pendiente pronunciada

* Alta liquidez en ese nivel

---

### ⚠️ Zonas planas

* Baja liquidez → movimientos rápidos posibles

---

# 🚀 Conclusión

Este sistema combina:

* Análisis técnico
* Microestructura de mercado
* Datos de derivados (funding)
* Backtesting

Para generar señales más robustas que el análisis tradicional.

---


CRYPTO-platform/
│
├── alerts/
│   ├── telegram/
│   │   └── notifier.py        # Envía mensajes
│   └── manager.py             # decide cuándo alertar
│
├── analytics/
│   ├── indicators/
│   ├── statistics/
│   ├── reports/
│   │   └── plot_prices.py      # Para graficar Bitcoin
│   └── signals/                # NUEVO (CLAVE)
│       ├── signal_engine.py
│       ├── scoring.py
│       └── rules.py
│
├── backtesting/
│   └── backtester.py/
│
├── app/
│   └── dashboard.py            # Graficar el comportamiento de las monedas          
│
├── data/
│   ├── features/                   # datos crudos (raw API)
│   ├── processed/                  # datos limpios
│   └── raw/  
│       └── binance /
│           ├── BTCUSD.csv      # Donde se guardan los datos de Bitcoin historicos
│           ├── ETHUSD.csv      
│           ├── ...     
│           └── funding_rate /
│               ├── ETHUSD.csv     
│               └── ...
│
├── exchange_API/
│   └── binance/
│       └── client.py           # Donde se adquieren los datos desde binance       
│
├── jobs/
│   ├── fetch_binance_data.py   # El script principal para correr todo el codigo de extraccion
│   └── run_signals.py          # ejecuta el sistema en vivo
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

python -m jobs.run_signal


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