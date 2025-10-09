### Para Instalação no Windows 10 foi criado um Ambiente Virtual

### Instalação do ambiente Virtual

```shell
python -m venv .venv
```

### Ativação do ambiente virtual no Windows

```shell
.venv/Scripts/activate
```

### Para Instalação no Debia 12 foi criado um Ambiente Virtual
 #### Crie um ambiente virtual usando venv ou virtual env Certifique-se venv de que esteja instalado executando:
```shell
sudo apt install python3-venv
```
#### Para criar um novo ambiente virtual em um **diretório chamado env**, execute:
```shell
python3 -m venv env
```
#### Para ativar este ambiente virtual (que modifica a PATH variável de ambiente), execute:
```shell
source env/bin/activate
```
#### Agora você pode instalar uma biblioteca neste ambiente virtual:
```shell
pip install XYZ
```
Os arquivos serão instalados no env/diretório.

Se quiser sair do ambiente virtual, você pode executar:
```shell
deactivate
```

### Instalação de Bibliotecas: 
```shell
#pip install selenium
#pip install python-dotenv
#pip install fastapi
#pip install "uvicorn[standard]" ou pip install "uvicorn[all]"
```
#### Iniciando o servidor Uvincorn
```shell
uvicorn app:app --reload
```

### OBS API:
API Criada para criação e consulta de dados em cache(memcached)

### Projeto em andamento

Este projeto visa automatizar, busca e armazenamento de dados, ele é chamado por métodos CRUD, onde os dados são armazeado em um servidor memcached e consumido.

#### Endpoint\POST http://localhost:8001/cache/gravar
```json
{
    "chave": "lucas",
    "valor": {
        "textarea": "TEXTO DO CAMPO TEXTAREA",
        "tx":"RJO AM RJO AM DP*V 0001",
        "elementoA": "RJMAD01-RMD01",
        "intA": "1/1/1",
        "elementoB": "RJMAD01-RMD02",
        "intB": "1/1/2"
    },
    "expiracao": 300
}
```

### FRONT-END
#### CABEÇALHO FETCH

```js
let textarea = document.querySelector('.txtarea').value;
let desigtx = regexpAberturaderal(/\w{1,}\s\w{1,}\s\w{1,}\s\w{1,}\s\w{2}\*\w\s\d{4}|\w{1,}\s\w{1,}\s\w{1,}\s\w{1,}\s\d+\w\s\d+/gm);
let ipran = regexpAberturaderal(/IP\sRAN\/\w{2}\s\w+\/\w{2}\s\w+/gm);
let ipnodeb = regexpAberturaderal(/IP\sNODEB\/\w{2}\s\w+\/\w{2}\s\w+/gm);

let data = new Date();
let datahora = `${data.toLocaleDateString()} - ${data.getHours()}:${data.getMinutes()}`;
function regexpAberturaderal(patten){
    let capturatxt =  [... textarea.matchAll(patten)];
    if(capturatxt.length !== 0){
        return capturatxt[0][0];
    }
}

var myHeaders = new Headers({
    'Content-Type': 'application/json',
});

let bodyObj = {
    url: 'http://10.129.219.180/smart/modules/authentication',
    elementoA: 'BACAB05',
    elementoB: 'BACAB05'
}

let conectApi = async (url, obj) => {
    var options = {
      method: "POST",
      body: JSON.stringify(obj),
      headers: myHeaders,
      mode: "cors",
      cache: "default",
    };

    try{
        const conexao = await fetch(url, options)
        if(conexao.status === 200){
            const openConexao = await conexao.json();
            return openConexao;
        } 
    }catch(error){
        console.log('Falha no link!')
    }
}

conectApi('http://clr0an001372366.nt.embratel.com.br:8004/host', bodyObj)
```
#### Base de dados do arquivo .json
```json
{
    "id": 1,
    "sitecode": "",
    "end": ""
}
```

### VARIAVEL DE AMBIENTE
```.env
MEMCACHED_SERVERS=cache-serve
SERVER_PORT=11211
```