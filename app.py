import schedule
import time
import threading
from flask import Flask, jsonify, render_template_string
from faucet_claimer import MonadFaucetClaimer
import os
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Estado global para tracking
class AppState:
    def __init__(self):
        self.last_execution = None
        self.last_result = None
        self.next_execution = None
        self.total_executions = 0
        self.successful_claims = 0
        self.wallet_address = os.getenv('WALLET_ADDRESS', 'No configurada')

state = AppState()

def run_faucet_claim():
    """Función que ejecuta el claim"""
    try:
        state.last_execution = datetime.now()
        state.total_executions += 1
        
        wallet_address = os.getenv('WALLET_ADDRESS')
        if not wallet_address:
            logger.error("❌ No wallet address configured")
            state.last_result = "no_wallet_configured"
            return
        
        logger.info(f"🚀 Ejecutando claim #{state.total_executions}")
        claimer = MonadFaucetClaimer(wallet_address)
        result = claimer.run_claim()
        
        state.last_result = result
        if result == "success":
            state.successful_claims += 1
            
        logger.info(f"🎯 Claim result: {result}")
        
        # Calcular próxima ejecución
        state.next_execution = datetime.now() + timedelta(hours=4)
        
    except Exception as e:
        logger.error(f"❌ Error en claim: {str(e)}")
        state.last_result = f"error: {str(e)}"

def start_scheduler():
    """Inicia el scheduler en un hilo separado"""
    logger.info("📅 Iniciando scheduler - ejecución cada 4 horas")
    
    # Ejecutar cada 4 horas
    schedule.every(4).hours.do(run_faucet_claim)
    
    # Calcular próxima ejecución inicial
    state.next_execution = datetime.now() + timedelta(hours=4)
    
    # Ejecutar una vez al inicio después de 1 minuto
    schedule.every(1).minutes.do(lambda: [run_faucet_claim(), schedule.cancel_job(schedule.jobs[0])][1]).tag('initial')
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Revisar cada minuto

# HTML Template para la interfaz web
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🎯 MONAD Faucet Auto Claimer</title>
    <meta http-equiv="refresh" content="60">
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #1a1a1a; color: #fff; }
        .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
        .status-card { background: #2a2a2a; border-radius: 10px; padding: 20px; margin: 20px 0; border-left: 5px solid #4CAF50; }
        .error { border-left-color: #f44336; }
        .warning { border-left-color: #ff9800; }
        .info { border-left-color: #2196F3; }
        .button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; margin: 10px 5px; }
        .button:hover { background: #45a049; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-item { background: #333; padding: 15px; border-radius: 8px; text-align: center; }
        .code { background: #000; padding: 10px; border-radius: 5px; font-family: monospace; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 MONAD Faucet Auto Claimer</h1>
        <p>Ejecutándose automáticamente cada 4 horas</p>
    </div>
    
    <div class="stats">
        <div class="stat-item">
            <h3>📊 Estadísticas</h3>
            <p><strong>Ejecuciones totales:</strong> {{ state.total_executions }}</p>
            <p><strong>Claims exitosos:</strong> {{ state.successful_claims }}</p>
            <p><strong>Wallet:</strong> {{ state.wallet_address[:10] }}...{{ state.wallet_address[-8:] if state.wallet_address != 'No configurada' else 'No configurada' }}</p>
        </div>
        
        <div class="stat-item">
            <h3>⏰ Tiempos</h3>
            <p><strong>Última ejecución:</strong><br>
            {{ state.last_execution.strftime('%Y-%m-%d %H:%M:%S UTC') if state.last_execution else 'Nunca' }}</p>
            <p><strong>Próxima ejecución:</strong><br>
            {{ state.next_execution.strftime('%Y-%m-%d %H:%M:%S UTC') if state.next_execution else 'No programada' }}</p>
        </div>
        
        <div class="stat-item">
            <h3>📈 Estado Actual</h3>
            <p><strong>Último resultado:</strong></p>
            {% if state.last_result == 'success' %}
                <span style="color: #4CAF50;">✅ Claim exitoso</span>
            {% elif state.last_result == 'already_claimed' %}
                <span style="color: #ff9800;">⏳ Ya reclamado (normal)</span>
            {% elif state.last_result == 'connection_error' %}
                <span style="color: #f44336;">❌ Error de conexión</span>
            {% elif state.last_result %}
                <span style="color: #f44336;">❌ {{ state.last_result }}</span>
            {% else %}
                <span style="color: #888;">➖ Sin ejecuciones aún</span>
            {% endif %}
        </div>
    </div>
    
    <div class="status-card info">
        <h3>🎮 Controles</h3>
        <a href="/claim-now" class="button">🚀 Ejecutar Claim Ahora</a>
        <a href="/" class="button" style="background: #2196F3;">🔄 Recargar Página</a>
        <p><small>La página se actualiza automáticamente cada 60 segundos</small></p>
    </div>
    
    <div class="status-card">
        <h3>📋 Información</h3>
        <p><strong>🕐 Frecuencia:</strong> Cada 4 horas automáticamente</p>
        <p><strong>🎯 Endpoint manual:</strong> <code>/claim-now</code></p>
        <p><strong>📊 API Health:</strong> <code>/health</code></p>
        <p><strong>⏰ Hora actual:</strong> {{ current_time }}</p>
    </div>
</body>
</html>
'''

@app.route('/')
def dashboard():
    """Dashboard principal"""
    return render_template_string(HTML_TEMPLATE, 
                                state=state, 
                                current_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'))

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "MONAD Faucet Claimer running",
        "timestamp": datetime.now().isoformat(),
        "wallet_configured": bool(os.getenv('WALLET_ADDRESS')),
        "last_execution": state.last_execution.isoformat() if state.last_execution else None,
        "last_result": state.last_result,
        "next_execution": state.next_execution.isoformat() if state.next_execution else None,
        "total_executions": state.total_executions,
        "successful_claims": state.successful_claims
    })

@app.route('/claim-now')
def manual_claim():
    """Endpoint para ejecutar claim manualmente"""
    try:
        logger.info("🎮 Ejecución manual solicitada")
        run_faucet_claim()
        return jsonify({
            "status": "success",
            "message": "Claim ejecutado manualmente",
            "result": state.last_result,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"❌ Error en ejecución manual: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/stats')
def stats():
    """Estadísticas en JSON"""
    return jsonify({
        "wallet_address": state.wallet_address,
        "last_execution": state.last_execution.isoformat() if state.last_execution else None,
        "last_result": state.last_result,
        "next_execution": state.next_execution.isoformat() if state.next_execution else None,
        "total_executions": state.total_executions,
        "successful_claims": state.successful_claims,
        "success_rate": (state.successful_claims / state.total_executions * 100) if state.total_executions > 0 else 0
    })

if __name__ == '__main__':
    logger.info("🚀 Iniciando MONAD Faucet Auto Claimer")
    
    # Verificar configuración
    wallet_address = os.getenv('WALLET_ADDRESS')
    if not wallet_address:
        logger.warning("⚠️  WALLET_ADDRESS no configurada - configúrala en las variables de entorno")
    else:
        logger.info(f"✅ Wallet configurada: {wallet_address[:10]}...{wallet_address[-8:]}")
    
    # Iniciar scheduler en background
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    # Iniciar Flask app
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🌐 Servidor web iniciando en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
