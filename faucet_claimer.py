import requests
import json
import time
from datetime import datetime
import os
import sys

class MonadFaucetClaimer:
    def __init__(self, wallet_address):
        self.wallet_address = wallet_address
        self.api_url = "https://faucet.morkie.xyz/api/monad"
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "es",
            "content-type": "application/json",
            "origin": "https://faucet.morkie.xyz",
            "referer": "https://faucet.morkie.xyz/monad",
            "sec-ch-ua": '"Not;A=Brand";v="99", "Google Chrome";v="139", "Chromium";v="139"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        }
    
    def claim_faucet(self):
        payload = {"address": self.wallet_address}
        
        try:
            print(f"🌐 Haciendo request a: {self.api_url}")
            print(f"📦 Payload: {json.dumps(payload)}")
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            print(f"📡 Status Code: {response.status_code}")
            
            # Mostrar contenido raw para debugging
            response_text = response.text
            print(f"📄 Raw Response (primeros 200 chars): {response_text[:200]}")
            
            if not response_text.strip():
                return response.status_code, {"error": "Respuesta vacía del servidor"}
            
            # Intentar parsear JSON
            try:
                response_data = response.json()
                return response.status_code, response_data
            except json.JSONDecodeError as e:
                return response.status_code, {
                    "error": f"Respuesta no es JSON válido: {str(e)}",
                    "raw_response": response_text[:500]
                }
            
        except requests.exceptions.Timeout:
            return None, {"error": "Timeout - La API no respondió en 30 segundos"}
        except requests.exceptions.ConnectionError:
            return None, {"error": "Error de conexión - No se pudo conectar a la API"}
        except requests.exceptions.RequestException as e:
            return None, {"error": f"Error en request: {str(e)}"}
    
    def format_time(self, seconds):
        """Convierte segundos a formato legible"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
    
    def run_claim(self):
        print(f"🚀 Intentando claim para wallet: {self.wallet_address}")
        print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("-" * 60)
        
        status_code, response_data = self.claim_faucet()
        
        if status_code is None:
            print(f"❌ ERROR DE CONEXIÓN: {response_data.get('error')}")
            return "connection_error"
        
        print(f"📡 Status Code Final: {status_code}")
        
        if status_code == 200 and response_data.get("success"):
            # Claim exitoso
            print("✅ CLAIM EXITOSO!")
            print(f"💰 Cantidad recibida: {response_data.get('amountReceived')} MONAD")
            print(f"🔗 Transaction Hash: {response_data.get('transactionHash')}")
            print(f"⭐ Tier: {response_data.get('tier')}")
            print(f"💳 Balance Morkie: {response_data.get('morkieBalance')}")
            
            next_claim = response_data.get('nextClaimAvailable')
            if next_claim:
                next_time = datetime.fromtimestamp(next_claim / 1000)
                print(f"⏳ Próximo claim disponible: {next_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            return "success"
            
        elif status_code == 429 or response_data.get("type") == "wallet_limit":
            # Wallet ya reclamó recientemente
            print("⏳ WALLET YA RECLAMÓ RECIENTEMENTE (Esto es normal)")
            print(f"📝 Mensaje: {response_data.get('message')}")
            
            remaining_time = response_data.get('remainingTime', 0)
            if remaining_time > 0:
                print(f"⏰ Tiempo restante: {self.format_time(remaining_time)}")
            
            next_claim = response_data.get('nextClaimAvailable')
            if next_claim:
                next_time = datetime.fromtimestamp(next_claim / 1000)
                print(f"⏳ Próximo claim: {next_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            return "already_claimed"
            
        else:
            # Otro tipo de error
            print(f"❌ ERROR EN CLAIM")
            print(f"📝 Mensaje: {response_data.get('message', 'Error desconocido')}")
            if "raw_response" in response_data:
                print(f"🔍 Respuesta raw: {response_data['raw_response']}")
            return "unexpected_error"

# Para compatibilidad cuando se ejecuta directamente
def main():
    wallet_address = os.getenv('WALLET_ADDRESS')
    if len(sys.argv) > 1:
        wallet_address = sys.argv[1]
    
    if not wallet_address:
        print("❌ ERROR: No se proporcionó wallet address")
        sys.exit(1)
    
    claimer = MonadFaucetClaimer(wallet_address)
    result = claimer.run_claim()
    print(f"🎯 RESULTADO: {result}")

if __name__ == "__main__":
    main()
