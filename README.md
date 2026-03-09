# 📦 Sistema de Gestión de Inventario en Consignación

Dashboard interactivo + automatización de reportes para el control de mercancía en consignación entre distribuidor y proveedor. Proyecto real adaptado como demo.

---

## 🖥️ Demo

> **Contraseña del demo:** `demo1234`

Abre `reporte/Reporte_Demo.html` directamente en el navegador — no requiere servidor ni instalación.

---

## 🧩 ¿Qué resuelve este proyecto?

Una empresa distribuidora recibe mercancía en **consignación** de un proveedor: vende los productos y liquida al costo lo que efectivamente vendió. El reto: llevar control claro de:

- ¿Cuánto le debo al proveedor hoy?
- ¿Cuánto crédito me queda disponible?
- ¿Qué facturas están por vencer o en prórroga?
- ¿Qué productos se agotaron o están en stock crítico?

Este sistema responde todo eso desde un solo archivo HTML + un script Python que lo actualiza desde Excel.

---

## ⚙️ Stack técnico

| Capa | Tecnología |
|---|---|
| Dashboard / UI | HTML5 · CSS3 · JavaScript vanilla |
| Gráficos | Chart.js |
| Autenticación | SHA-256 client-side |
| Actualización datos | Python 3 · openpyxl |
| Documentos | python-docx · openpyxl |
| Fuente de datos | Excel (.xlsx) |

**Sin dependencias de servidor.** El reporte es un único archivo `.html` autocontenido.

---

## 🚀 Funcionalidades

### Dashboard principal
- **5 KPIs** en tiempo real: total adeudado, abono, crédito a favor, valor consignado, stock actual
- **3 gráficos interactivos**: distribución por categoría (donut), top 10 productos (barras horizontales), flujo consignado vs. vendido vs. stock (barras agrupadas)
- Tabla de productos con **56 referencias**, agrupadas por categoría
- Barra de rotación por producto con semáforo visual (rojo/verde/azul según % vendido)
- **Filtro de búsqueda** en tiempo real sobre toda la tabla

### Estado de facturas
- Tabla de facturas con **cálculo dinámico de estados via JavaScript**:
  - `VIGENTE` → `POR VENCER` (≤7 días) → `EN PRÓRROGA` (30d–45d) → `VENCIDA`
- Los días restantes se recalculan automáticamente cada vez que se abre el reporte
- Barra visual de utilización de línea de crédito

### Novedades de inventario
- Modal emergente con alertas automáticas al iniciar sesión
- Detecta productos agotados, stock crítico y top ventas del período

### UX
- Modo oscuro / claro con persistencia en `localStorage`
- Diseño responsive (mobile-first)
- Autenticación con contraseña (hash SHA-256)

---

## 📁 Estructura del proyecto

```
├── reporte/
│   ├── Reporte_Demo.html       # Dashboard completo (demo con datos ficticios)
│   └── update_html.py          # (ver scripts/)
├── scripts/
│   └── update_html.py          # Script Python para actualizar el HTML desde Excel
├── plantillas/
│   └── Conteo_Fisico_Template.xlsx  # Planilla de conteo físico de inventario
└── README.md
```

---

## 🔄 Cómo actualizar el reporte

```bash
# Instalar dependencia
pip install openpyxl

# Actualizar el HTML con nuevos datos del Excel
python scripts/update_html.py
```

El script lee `Movimientos_Consignacion.xlsx` (hoja `Principal`) y reconstruye:
- Todo el tbody de la tabla de productos
- Los 5 KPIs del dashboard
- Los 3 datasets de Chart.js
- La fecha de actualización

### Lógica de negocio implementada

```python
# Lo que el distribuidor le debe al proveedor (al precio de costo)
subtotal_adeudado = PRECIO_UNIT_COSTO × TOTAL_UND_VENDIDAS

# Stock actual valorado
stock_costo = EXISTENCIA_EMPAQUES × MINIMO_VENTA × PRECIO_UNIT_COSTO

# Crédito disponible (descuenta lo ya pagado)
credito_disponible = linea_credito - (total_facturado - total_abonado)

# Rotación
pct_rotacion = TOTAL_UND_VENDIDAS / UND_RECIBIDAS × 100
```

---

## 📊 Planilla de Conteo Físico

`plantillas/Conteo_Fisico_Template.xlsx` — lista todos los productos con su stock en sistema. El personal de almacén ingresa el conteo físico en la columna amarilla y la diferencia se calcula automáticamente.

| Columna | Contenido |
|---|---|
| D (azul) | Stock en sistema — pre-llenado |
| E (amarilla) | Conteo físico — rellenar manualmente |
| F (verde) | Diferencia calculada automáticamente |
| G | Observaciones libres |

---

## 🤖 Agente de datos con Claude

El archivo `CLAUDE.md` define el comportamiento de un **agente de datos funcional** que puede:
- Analizar la cartera de facturas y alertar vencimientos
- Calcular KPIs de rotación e inventario crítico
- Sugerir órdenes de compra basadas en movimientos reales
- Generar documentos (OC, RFQ, informes) en `.docx`

---

## 📸 Capturas

### Modo oscuro
![Dashboard modo oscuro](https://via.placeholder.com/800x400/0f172a/60a5fa?text=Dashboard+Modo+Oscuro)

### Modo claro
![Dashboard modo claro](https://via.placeholder.com/800x400/f8fafc/1d4ed8?text=Dashboard+Modo+Claro)

---

## 📄 Licencia

Proyecto personal / portafolio. Los datos mostrados son ficticios.

---

