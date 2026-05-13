<p align="center">
  <img src="assets/Bitcoin_Portada.png" width="100%"/>
</p>

# Crypto Trading Dashboard & Signal Engine

Este proyecto es una plataforma de análisis de mercado cripto que combina datos históricos, métricas en tiempo real y lógica cuantitativa para generar señales de compra y venta.

---

## 🪙 Activos soportados

Actualmente el sistema trabaja con los siguientes pares:

| BTCUSDT (Bitcoin)      | ETHUSDT (Ethereum)       | XRPUSDT             |
|------------------------|--------------------------|---------------------|
| SOLUSDT (Solana)       | DOGEUSDT (Dogecoin)      | ADAUSDT (Cardano)   |
| LINKUSDT (Chainlink)   | XLMUSDT (Stellar)        | AVAXUSDT (Avalanche)|
| HBARUSDT (Hedera)      | SHIBUSDT (Shiba Inu)     | PEPEUSDT            | 

---

## 📈 Tendencia (Trend)
La tendencia se calcula usando medias móviles:
* MA 20 (media rápida)
* MA 50 (media lenta)


|               | 📈 Alcista (bullish) | 📉 Bajista (bearish)|
|---------------|----------------------|----------------------|
| Condición     | MA20 > MA50          | MA20 < MA50          |
| Interpretación| El precio está en una fase de crecimiento, Mayor probabilidad de continuación al alza, Favorece compras en retrocesos| El precio está en caída, Mayor probabilidad de continuación bajista, Favorece ventas o evitar compras|


---

## 🌍 Contexto de mercado

El sistema clasifica el mercado en 3 estados:

---
|               |🔵 Tendencial (trending)     |🟠 Lateral (ranging)            |🔴 Volátil (volatile)             |
|---------------|-----------------------------|---------------------------------|-----------------------------------|
| Condición     | Movimiento direccional claro| Rango estrecho y baja expansión |Alta desviación estándar del precio|
| Interpretación| Mercado con dirección definida, Estrategias de seguimiento de tendencia funcionan mejor| Precio se mueve entre soporte y resistencia, Ideal para comprar en mínimos y vender en máximos|Movimientos bruscos, Mayor riesgo, Señales menos confiables |

---

## 💰 Funding Rate

Es el costo que pagan los traders en contratos perpetuos (futuros).
* Lo pagan los LONGS o los SHORTS dependiendo del mercado
* API de Binance (futuros)
* Se guarda en `data/raw/binance/funding_rate/`

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
│   │   ├── listener.py                 # Recibe comandos de Telegram, interfaz del bot
│   │   └── notifier.py                 # Envía mensajes a Telegram, Usa API de Telegram
│   └── manager.py                      # Construye el mensaje, Formatea texto bonito para Telegram
│
├── analytics/                          # Todos los calculos
│   ├── backtesting/
│   │   ├── backtester.py               # Simula estrategia en el pasado
│   │   └── service.py                  # Solo ejecuta el backtester
│   ├── chart/
│   │   ├── output/
│   │   ├── chart_builder.py 
│   │   └── plotters.py                 # Construye gráfico completo, es el grafico principal
│   ├── indicators/
│   │   ├── market_indicators.py        # Añade columnas al DataFrame, VWAP, MA20, MA50, tendencia, contexto, etc, Base de todo el análisis
│   │   ├── orderbook.py                # Analiza libro de órdenes
│   │   ├── swings.py                   # Detecta picos y valles reales, esto define soportes y resistencias
│   │   └── weighted_levels.py          # Calcula niveles inteligentes
│   ├── signals/                
│   │   ├── signal_engine.py
│   │   └── market_context.py           # Añade inteligencia macro
│   └── pipeline.py                     # Este es el corazón del sistema, devuelve TODO listo para usar
│
├── app/
│   └── dashboard.py                    # Interfaz visual (Streamlit)         
│
├── data/
│   ├── features/ 
│   ├── portfolio/  
│   │   ├── active_positions.json   
│   │   ├── manager.py     
│   │   ├── storage.py                  # Guarda y carga datos JSON, acceso a datos, persistencia
│   │   └── trade_history.json                 
│   ├── processed/                      # Datos limpios
│   └── raw/  
│       └── binance /
│           ├── BTCUSD.csv              # Donde se guardan los datos de Bitcoin historicos
│           ├── ETHUSD.csv      
│           ├── ...     
│           └── funding_rate /
│               ├── ETHUSD.csv     
│               └── ...      
│
├── jobs/
│   ├── fetch_binance_data.py           # Descarga datos de Binance, solo descarga datos nuevos, evita duplicados
│   ├── run_faser_alert.py              # Revisa movimientos rapidos, detecta velas enormes y volatilidad, manda alertas instantaneas.
│   ├── run_signals.py                  # Sistema en vivo, es el bot trader
│   └── scheduler.py                    # Automatizador total, cerebro de horarios para diferentes acciones de run.
│
├── processing/
│   └── cleaning/
│       └── save_raw.py                 # Guarda datos en CSV
│
├── src/
│   ├── api/                            
│   │   ├── binance/
│   │   │   └── client.py               # Conecta con Binance
│   └── config/                         
│       ├── paths.py
│       └── settings.py                 # Símbolos, intervalos, trades de ejemplo
│
├── .gitignore
└── README.md


cd "G:\PYTHON\Proyectos Personales\CRYPTO-platform"

python -m jobs.scheduler

python -m streamlit run app/dashboard.py


python -m jobs.fetch_binance_data
python -m alerts.telegram.listener