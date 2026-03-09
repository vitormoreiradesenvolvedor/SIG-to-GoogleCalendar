# SIG-to-GoogleCalendar

## Um script em Python para pegar os horários de aula do SIG e converter para um arquivo `.csv` para ser usado no Google Agenda

[English Documentation](https://github.com/vitormoreiradesenvolvedor/SIG-to-GoogleCalendar/blob/master/docs/englishDoc.md)

### Pré-requisitos

Você precisa de Python 3.x.x para rodar esse script.

### Instalação

Clone o repositório e entre na pasta do projeto.

Depois, é fortemente recomendado criar e ativar um ambiente virtual (`venv`) antes de instalar as dependências.

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Agora instale as dependências com:

```bash
pip install -r requeriments.txt
```

### Rodando

Com o ambiente virtual ativado, rode no terminal:

```bash
python3 sigToCalendar.py
```

Você vai precisar fornecer algumas informações para rodar o script:

* Login - Seu login do SIG
* Password - Sua senha do SIG
* Start Date - A partir de qual dia você quer replicar seus horários
* End Date - Até que dia você quer replicar seus horários

Depois disso, um arquivo `.csv` vai ser gerado. Vá em `calendar.google.com > Importar > Selecionar um arquivo do seu computador` e escolha o arquivo `.csv` gerado.

É fortemente recomendado criar uma nova agenda para importar o arquivo `.csv`.

### Contribuindo

Sinta-se à vontade para dar feedback, abrir novas issues e pull requests.
