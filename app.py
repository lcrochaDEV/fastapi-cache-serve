from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import memcache  # Importa a biblioteca cliente Memcached
import json
import logging
from dotenv import load_dotenv
import os

load_dotenv()

MEMCACHED_SERVERS = os.getenv("MEMCACHED_SERVERS")
SERVER_PORT = os.getenv("SERVER_PORT")

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
    max_age=3600,
)

@app.get("/")
def methodGet():
   return {"API está operacional memcaced"}

# Configuração
MEMCACHED_SERVERS = [(f'{MEMCACHED_SERVERS}:{SERVER_PORT}')]
logging.basicConfig(level=logging.INFO)

# 1. Conexão Global com o Memcached
# É boa prática iniciar a conexão apenas uma vez.
try:
    mc = memcache.Client(MEMCACHED_SERVERS, debug=0)
    # Testa a conexão (opcional, mas recomendado)
    if not mc.set('_test_key_', '1'):
         logging.warning("Não foi possível conectar ou gravar no Memcached. Verifique o servidor.")
except Exception as e:
    logging.error(f"Erro ao iniciar o cliente Memcached: {e}")
    # Se a conexão falhar, mc será None ou levantará um erro nas operações
    mc = None 

# 2. Modelo Pydantic para Validação dos Dados de Entrada (POST Body)
class ItensCache(BaseModel):
    """Define o formato esperado para o corpo da requisição POST."""
    chave: str
    valor: dict  # Aceita qualquer objeto JSON como valor
    expiracao: int = 300  # Tempo em segundos 

# 3. Path Operation (Endpoint POST)
@app.post("/cache/gravar", status_code=201)
def gravar_no_memcached(itens: ItensCache):
    """
    Recebe uma requisição POST e grava os dados no servidor Memcached.
    """
    if mc is None:
        logging.error("Cliente Memcached não está inicializado.")
        # Retorna um erro amigável ao cliente HTTP
        raise HTTPException(status_code=503, detail="Serviço de Cache indisponível.")

    # 3.1. Serialização do Valor (Passo 3 do algoritmo)
    # Memcached armazena strings/bytes. Serializamos o dict (valor) para JSON.
    try:
        valor_serializado = json.dumps(itens.valor)
    except TypeError:
        # Se o valor não for serializável (o que Pydantic geralmente evita), tratar
        raise HTTPException(status_code=422, detail="Valor não é um objeto JSON válido.")

    # 3.2. Gravação no Memcached (Passo 4 do algoritmo)
    # mc.set(chave, valor, tempo_expiracao)
    sucesso = mc.set(
        itens.chave, 
        valor_serializado, 
        time=itens.expiracao
    )
    if sucesso:
        # 3.3. Retorno de Sucesso (Passo 5 do algoritmo)
        return {
            "status": "sucesso", 
            "chave_gravada": itens.chave,
            "tempo_expiracao_segundos": itens.expiracao
        }
    else:
        # Falha de gravação (ex: Memcached sem memória, chave muito longa)
        logging.error(f"Falha ao gravar chave {itens.chave} no Memcached.")
        raise HTTPException(status_code=500, detail="Falha ao armazenar dados no cache. Tente novamente.")

# 4. Path Operation (Endpoint GET)
@app.get("/cache/recuperar/{chave}")
def recuperar_do_memcached(chave: str):
    """
    Recebe uma chave e tenta recuperar o valor associado do Memcached.
    """
    if mc is None:
        raise HTTPException(status_code=503, detail="Serviço de Cache indisponível.")

    # 2. Busca no Cache
    # mc.get() retorna o valor em string/bytes ou None se não for encontrado.
    valor_serializado = mc.get(chave)

    if valor_serializado is not None:
        # 3. Cache Hit (Acerto)
        
        # O valor é desserializado de volta para um objeto Python (dicionário).
        try:
            valor_objeto = json.loads(valor_serializado)
            return {
                "status": "sucesso",
                "chave": chave,
                "origem": "memcached",
                "valor": valor_objeto
            }
        except json.JSONDecodeError:
            # Caso o dado no cache não seja um JSON válido (raro se gravado corretamente)
            logging.error(f"Erro de desserialização para a chave: {chave}")
            # Você pode deletar a chave corrompida aqui: mc.delete(chave)
            raise HTTPException(status_code=500, detail="Dado corrompido no cache.")
            
    else:
        # 4. Cache Miss (Erro)
        # A chave não foi encontrada no cache.
        raise HTTPException(status_code=404, detail=f"Chave '{chave}' não encontrada no cache.")
