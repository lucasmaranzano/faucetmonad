# 🎯 MONAD Faucet Auto Claimer - Railway

Automatiza el claim del faucet MONAD cada 4 horas usando Railway.

## 🚀 Deploy en Railway

1. **Fork este repositorio**
2. **Ve a https://railway.app**
3. **New Project → Deploy from GitHub repo**
4. **Selecciona este repositorio**
5. **Agrega variable de entorno:**
   - `WALLET_ADDRESS`: Tu wallet address
6. **Deploy automático**

## 🌐 Endpoints

- `/` - Dashboard web con estadísticas
- `/health` - Health check (JSON)
- `/claim-now` - Ejecutar claim manual
- `/stats` - Estadísticas (JSON)

## 📊 Características

- ✅ Ejecución automática cada 4 horas
- ✅ Dashboard web con estadísticas en tiempo real
- ✅ Ejecución manual via web
- ✅ Logs detallados
- ✅ Auto-restart en caso de errores
- ✅ Interfaz responsive

## 🎮 Uso

Una vez deployado, visita tu URL de Railway para ver el dashboard.

La aplicación se ejecutará automáticamente cada 4 horas.
