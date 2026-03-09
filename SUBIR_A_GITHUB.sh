#!/bin/bash
# ─────────────────────────────────────────────────────────────────
# Script para crear el repo en GitHub y subir todos los archivos
# Ejecutar UNA SOLA VEZ desde la carpeta github-repo/
# ─────────────────────────────────────────────────────────────────

GH_TOKEN="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"
GH_USER="jolacruz7"
REPO_NAME="sistema-consignacion-inventario"

echo "🔧 Creando repositorio en GitHub..."
curl -s -X POST \
  -H "Authorization: token $GH_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.github.com/user/repos \
  -d "{
    \"name\": \"$REPO_NAME\",
    \"description\": \"Dashboard HTML interactivo + automatizacion Python para gestion de inventario en consignacion. KPIs, facturas, credito y stock en un solo archivo.\",
    \"private\": false,
    \"auto_init\": false
  }"

echo ""
echo "📁 Inicializando git..."
git init
git add .
git commit -m "feat: sistema de gestión de inventario en consignación

- Dashboard HTML interactivo (Chart.js, modo oscuro/claro, auth SHA-256)
- Script Python para actualización automática desde Excel
- KPIs: total adeudado, crédito disponible, stock, rotación
- Estados de facturas calculados dinámicamente por JS
- Planilla Excel de conteo físico de inventario
- CLAUDE.md como spec de agente de datos funcional"

git branch -M main
git remote add origin https://$GH_TOKEN@github.com/$GH_USER/$REPO_NAME.git
git push -u origin main

echo ""
echo "✅ Listo: https://github.com/$GH_USER/$REPO_NAME"
