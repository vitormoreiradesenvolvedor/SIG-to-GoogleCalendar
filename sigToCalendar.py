import requests
import sys
import getpass
import urllib3
from pathlib import Path
from bs4 import BeautifulSoup
from createCSV import CSV


class Schedule:
    def __init__(self, info):
        self.info = info
        self.sigURL = "https://sig.ufla.br/modulos/login/index.php"
        self.scheduleURL = "https://sig.ufla.br/modulos/alunos/utilidades/horario.php"

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Origin": "https://sig.ufla.br",
            "Referer": self.sigURL,
        })

    def getClassSchedule(self):
        pageData = self.connectToSIG()
        self.findFormAndLogin(pageData)

        print("Extracting data...")

        schedulePage = self.session.get(
            self.scheduleURL,
            verify=False,
            timeout=30,
            allow_redirects=True
        )
        schedulePage.raise_for_status()

        # Se voltou para a tela de login, a autenticação não persistiu
        if self.isLoginPage(schedulePage.text):
            print("Sessão não autenticada ao acessar a página de horários.")
            print("Tente usar e-mail institucional no lugar do login numérico.")
            sys.exit(1)

        soup = BeautifulSoup(schedulePage.text, "html.parser")
        scheduleBoard = soup.find("tbody")

        if not scheduleBoard:
            print("Não foi possível localizar a grade de horários na página.")
            print("Talvez a estrutura do SIG tenha mudado.")
            self.save_debug_html("debug_horario.html", schedulePage.text)
            sys.exit(1)

        matrix = []
        for tr in scheduleBoard.find_all("tr"):
            row = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
            if row:
                matrix.append(row)

        if not matrix:
            print("A tabela de horários foi encontrada, mas está vazia.")
            sys.exit(1)

        scheduleDict = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

        for row in matrix:
            if len(row) < 8:
                continue

            row[0] = self.correctTime(row[0])

            for i in range(1, 8):
                if row[i] != "-":
                    classAndLocation = row[i].split(" - ", 1)

                    if len(classAndLocation) == 2:
                        raw_class, location = classAndLocation
                    else:
                        raw_class, location = row[i], ""

                    classCode = raw_class.split(" ")[0]

                    abbr = soup.find("abbr", string=classCode)
                    if abbr and abbr.get("title"):
                        className = classCode + " - " + abbr["title"].split(" / ")[0]
                    else:
                        className = raw_class

                    scheduleIndex = i - 2
                    if scheduleIndex < 0:
                        scheduleIndex = 6

                    scheduleDict[scheduleIndex].append([
                        className,
                        "",
                        row[0],
                        "",
                        self.endDate(row[0]),
                        location
                    ])

        print("Data extracted!")
        return scheduleDict

    def findLoginForm(self, html):
        soup = BeautifulSoup(html, "html.parser")

        # 1) tenta pelo id antigo
        form = soup.find("form", {"id": "form_login"})
        if form:
            return form

        # 2) tenta um formulário que tenha campo de senha
        for candidate in soup.find_all("form"):
            if candidate.find("input", {"type": "password"}):
                return candidate

        return None

    def buildLoginPayload(self, form):
        payload = {}

        for field in form.find_all("input"):
            name = field.get("name")
            value = field.get("value", "")
            if name:
                payload[name] = value

        # cobre nomes de campo possíveis
        possible_login_names = ["login", "usuario", "user", "email", "username"]
        possible_password_names = ["senha", "password", "passwd"]

        found_login_field = False
        found_password_field = False

        for name in possible_login_names:
            if name in payload:
                payload[name] = self.info["login"]
                found_login_field = True

        for name in possible_password_names:
            if name in payload:
                payload[name] = self.info["password"]
                found_password_field = True

        # fallback: injeta os nomes mais prováveis
        if not found_login_field:
            payload["login"] = self.info["login"]

        if not found_password_field:
            payload["senha"] = self.info["password"]

        # alguns formulários usam submit com nomes diferentes
        if "entrar" in payload:
            payload["entrar"] = payload.get("entrar") or "Entrar"

        return payload

    def isLoginPage(self, html):
        soup = BeautifulSoup(html, "html.parser")

        has_password_input = soup.find("input", {"type": "password"}) is not None
        page_text = soup.get_text(" ", strip=True).lower()

        indicators = [
            "autenticação no sistema",
            "esqueci minha senha",
            "cadastro de usuário externo",
            "entrar com gov.br",
            "log-in",
        ]

        return has_password_input and any(ind in page_text for ind in indicators)

    def extractLoginError(self, html):
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text("\n", strip=True)

        candidates = [
            "usuário ou senha inválidos",
            "login ou senha inválidos",
            "autenticação inválida",
            "senha inválida",
            "usuário inválido",
            "erro",
        ]

        lower = text.lower()
        for c in candidates:
            if c in lower:
                return c

        return None

    def save_debug_html(self, filename, html):
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"HTML de depuração salvo em: {filename}")
        except Exception:
            pass

    def findFormAndLogin(self, formData):
        form = self.findLoginForm(formData)
        if not form:
            print("Não foi possível localizar o formulário de login.")
            self.save_debug_html("debug_login.html", formData)
            sys.exit(1)

        action = form.get("action") or self.sigURL
        if not action.startswith("http"):
            if action.startswith("/"):
                action = "https://sig.ufla.br" + action
            else:
                action = self.sigURL.rsplit("/", 1)[0] + "/" + action

        payload = self.buildLoginPayload(form)

        print("Trying to login...")

        response = self.session.post(
            action,
            data=payload,
            headers={
                "Referer": self.sigURL,
                "Origin": "https://sig.ufla.br",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            allow_redirects=True,
            verify=False,
            timeout=30
        )
        response.raise_for_status()

        if self.isLoginPage(response.text):
            error = self.extractLoginError(response.text)
            print("Unable to login.")
            if error:
                print(f"Mensagem retornada pelo SIG: {error}")
            else:
                print("O SIG continuou exibindo a página de login após o POST.")
            print("Teste também com seu e-mail institucional no campo de login.")
            self.save_debug_html("debug_login_response.html", response.text)
            sys.exit(1)

        print("Login successful")
        return response

    def connectToSIG(self):
        print("Connecting to " + self.sigURL + " ...")

        page = self.session.get(
            self.sigURL,
            verify=False,
            timeout=30,
            allow_redirects=True
        )
        page.raise_for_status()

        if page.status_code == 200:
            print("Connected!")
            return page.text

        print("Unable to connect to SIG")
        sys.exit(1)

    def endDate(self, time):
        hour = int(time.split(":")[0])
        period = time.split(":")[1]

        hour += 1

        if hour == 12:
            return f"{hour}:00 PM"
        elif period == "00 PM":
            return f"{hour}:00 PM"
        else:
            return f"{hour}:00 AM"

    def correctTime(self, time):
        hour = int(time.split(":")[0])

        if hour > 12:
            hour -= 12
            return f"{hour}:00 PM"

        return f"{hour}:00 AM"


def getInfo():
    info = {}
    info["login"] = input("Enter your SIG login: ")
    info["password"] = getpass.getpass("Enter your SIG password: ")
    info["startDate"] = input("Enter the start date (DD/MM/YYYY): ")
    info["endDate"] = input("Enter the end date (DD/MM/YYYY): ")
    info["fileName"] = "calendar.csv"
    return info


def getInfoFromFile(fileData):
    data = fileData.read().splitlines()

    info = {}
    info["login"] = data[0]
    info["password"] = data[1]
    info["startDate"] = data[2]
    info["endDate"] = data[3]
    info["fileName"] = data[4]

    return info


if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    configFile = Path("data.config")

    if configFile.exists():
        with open("data.config", encoding="utf-8") as f:
            info = getInfoFromFile(f)
    else:
        info = getInfo()

    schedule = Schedule(info)
    schedule = schedule.getClassSchedule()

    csvFile = CSV(schedule, info["startDate"], info["endDate"], info["fileName"])
    csvFile.writeFile()
