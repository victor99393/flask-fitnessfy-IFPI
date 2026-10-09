from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import json
import os
import uuid


# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_DIR = os.path.join(BASE_DIR, "static")

USERS_FILE = os.path.join(
    BASE_DIR,
    "database",
    "users.json"
)

app = Flask(
    __name__,
    static_folder=None
)


# ============================================================
# ARQUIVOS STATIC
# ============================================================

@app.route("/static/<path:filename>")
def static(filename):

    caminho = os.path.join(
        STATIC_DIR,
        filename
    )

    if os.path.isfile(caminho):

        return send_from_directory(
            STATIC_DIR,
            filename
        )

    if filename.startswith("images/"):

        nome_arquivo = os.path.basename(filename)

        caminho_devs = os.path.join(
            STATIC_DIR,
            "images",
            "devs",
            nome_arquivo
        )

        if os.path.isfile(caminho_devs):

            return send_from_directory(
                os.path.join(
                    STATIC_DIR,
                    "images",
                    "devs"
                ),
                nome_arquivo
            )

    return "Arquivo não encontrado.", 404


# ============================================================
# USUÁRIOS
# ============================================================

def carregar_usuarios():

    os.makedirs(
        os.path.dirname(USERS_FILE),
        exist_ok=True
    )

    if not os.path.exists(USERS_FILE):

        with open(
            USERS_FILE,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                [],
                arquivo,
                ensure_ascii=False,
                indent=4
            )

    try:

        with open(
            USERS_FILE,
            "r",
            encoding="utf-8"
        ) as arquivo:

            usuarios = json.load(arquivo)

    except (
        json.JSONDecodeError,
        FileNotFoundError
    ):

        usuarios = []

    alterado = False

    for usuario in usuarios:

        if not usuario.get("id"):

            usuario["id"] = gerar_id_usuario(
                usuarios
            )

            alterado = True

        if "imc" not in usuario:

            usuario["imc"] = None

            alterado = True

    if alterado:

        salvar_usuarios(usuarios)

    return usuarios


def salvar_usuarios(usuarios):

    os.makedirs(
        os.path.dirname(USERS_FILE),
        exist_ok=True
    )

    with open(
        USERS_FILE,
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            usuarios,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


def gerar_id_usuario(usuarios):

    while True:

        novo_id = "usr_" + uuid.uuid4().hex[:10]

        if not any(
            usuario.get("id") == novo_id
            for usuario in usuarios
        ):

            return novo_id


def encontrar_usuario_por_id(user_id):

    usuarios = carregar_usuarios()

    for usuario in usuarios:

        if usuario.get("id") == user_id:

            return usuario

    return None


def encontrar_usuario_por_email(email):

    usuarios = carregar_usuarios()

    email = email.strip().lower()

    for usuario in usuarios:

        usuario_email = usuario.get(
            "email",
            ""
        ).strip().lower()

        if usuario_email == email:

            return usuario

    return None


# ============================================================
# IMC
# ============================================================

def calcular_imc(peso, altura):

    if altura <= 0:

        return None

    return peso / (altura ** 2)


def classificar_imc(imc):

    if imc < 18.5:

        return "Magreza"

    elif imc < 25:

        return "Normal"

    elif imc < 30:

        return "Sobrepeso"

    else:

        return "Obesidade"


def calcular_peso_ideal(altura):

    peso_minimo = 18.5 * (altura ** 2)

    peso_maximo = 24.9 * (altura ** 2)

    return peso_minimo, peso_maximo


# ============================================================
# DEURENBERG
# ============================================================

def calcular_gordura(imc, idade, sexo):

    if sexo == "masculino":

        return (
            (1.20 * imc)
            + (0.23 * idade)
            - 16.2
        )

    if sexo == "feminino":

        return (
            (1.20 * imc)
            + (0.23 * idade)
            - 5.4
        )

    return None


def classificar_gordura(gordura, sexo):

    if gordura is None:

        return None

    if sexo == "masculino":

        if gordura < 6:
            return "Essencial"

        elif gordura < 14:
            return "Atlético"

        elif gordura < 18:
            return "Fitness"

        elif gordura < 25:
            return "Aceitável"

        else:
            return "Obesidade"

    elif sexo == "feminino":

        if gordura < 14:
            return "Essencial"

        elif gordura < 21:
            return "Atlético"

        elif gordura < 25:
            return "Fitness"

        elif gordura < 32:
            return "Aceitável"

        else:
            return "Obesidade"

    return None


def obter_recomendacao(classificacao):

    recomendacoes = {

        "Magreza":
            "Acompanhe seus indicadores e procure orientação profissional para interpretar seus resultados.",

        "Normal":
            "Continue acompanhando seus indicadores e mantendo hábitos saudáveis.",

        "Sobrepeso":
            "Acompanhe seus indicadores e considere buscar orientação profissional para avaliar seus resultados.",

        "Obesidade":
            "Considere buscar orientação de um profissional de saúde para uma avaliação individualizada."
    }

    return recomendacoes.get(classificacao)


# ============================================================
# PÁGINA INICIAL
# ============================================================

@app.route("/")
def index():

    return render_template("index.html")


# ============================================================
# SOBRE
# ============================================================

@app.route("/about")
def about():

    return render_template("about.html")


# ============================================================
# CADASTRO
# ============================================================

@app.route(
    "/cadastro",
    methods=["GET", "POST"]
)
def cadastro():

    erro = None

    if request.method == "POST":

        nome = request.form.get(
            "nome",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        senha = request.form.get(
            "senha",
            ""
        ).strip()

        idade_texto = request.form.get(
            "idade",
            ""
        ).strip()

        peso_texto = request.form.get(
            "peso",
            ""
        ).strip()

        altura_texto = request.form.get(
            "altura",
            ""
        ).strip()

        if not nome or not email or not senha:

            erro = "Preencha todos os campos obrigatórios."

            return render_template(
                "cadastro.html",
                erro=erro
            )

        if encontrar_usuario_por_email(email):

            erro = "Este e-mail já está cadastrado."

            return render_template(
                "cadastro.html",
                erro=erro
            )

        try:

            idade = int(idade_texto)
            peso = float(peso_texto)
            altura = float(altura_texto)

        except ValueError:

            erro = (
                "Informe valores válidos para idade, peso e altura."
            )

            return render_template(
                "cadastro.html",
                erro=erro
            )

        if idade <= 0:

            erro = "Informe uma idade válida."

            return render_template(
                "cadastro.html",
                erro=erro
            )

        if peso <= 0:

            erro = "Informe um peso válido."

            return render_template(
                "cadastro.html",
                erro=erro
            )

        if altura <= 0:

            erro = "Informe uma altura válida."

            return render_template(
                "cadastro.html",
                erro=erro
            )

        usuarios = carregar_usuarios()

        novo_usuario = {

            "id": gerar_id_usuario(usuarios),

            "nome": nome,

            "email": email,

            "senha": senha,

            "idade": idade,

            "peso": peso,

            "altura": altura,

            "imc": None
        }

        usuarios.append(novo_usuario)

        salvar_usuarios(usuarios)

        return redirect(
            url_for(
                "profile",
                user_id=novo_usuario["id"]
            )
        )

    return render_template(
        "cadastro.html",
        erro=erro
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    erro = None

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        senha = request.form.get(
            "senha",
            ""
        ).strip()

        usuario = encontrar_usuario_por_email(email)

        if usuario is None:

            erro = "E-mail ou senha inválidos."

            return render_template(
                "login.html",
                erro=erro
            )

        if usuario.get("senha") != senha:

            erro = "E-mail ou senha inválidos."

            return render_template(
                "login.html",
                erro=erro
            )

        return redirect(
            url_for(
                "profile",
                user_id=usuario["id"]
            )
        )

    return render_template(
        "login.html",
        erro=erro
    )


# ============================================================
# PERFIL
# ============================================================

@app.route("/profile/<user_id>")
def profile(user_id):

    usuario = encontrar_usuario_por_id(user_id)

    if usuario is None:

        return redirect(
            url_for("login")
        )

    return render_template(

        "profile.html",

        user_id=usuario.get("id"),

        nome=usuario.get(
            "nome",
            ""
        ),

        email=usuario.get(
            "email",
            ""
        ),

        idade=usuario.get(
            "idade",
            ""
        ),

        peso=usuario.get(
            "peso",
            ""
        ),

        altura=usuario.get(
            "altura",
            ""
        ),

        imc=usuario.get("imc")
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    return redirect(
        url_for("login")
    )


# ============================================================
# CALCULADORA MATEMÁTICA
# ============================================================

@app.route("/math")
def math_calculator():

    user_id = request.args.get(
        "user_id",
        ""
    )

    peso = request.args.get(
        "peso",
        ""
    )

    altura = request.args.get(
        "altura",
        ""
    )

    return render_template(

        "math.html",

        user_id=user_id,

        peso=peso,

        altura=altura
    )


# ============================================================
# RESULTADO DA CALCULADORA MATEMÁTICA
# ============================================================

@app.route("/math/<op>/<a>/<b>")
def math(op, a, b):

    user_id = request.args.get(
        "user_id",
        ""
    )

    peso = request.args.get(
        "peso",
        ""
    )

    altura = request.args.get(
        "altura",
        ""
    )

    try:

        numero_a = float(a)

        numero_b = float(b)

    except (
        ValueError,
        TypeError
    ):

        return render_template(

            "math_result.html",

            erro="Os números informados são inválidos.",

            resultado=None,

            numero_a=None,

            numero_b=None,

            simbolo="",

            nome_operacao="",

            user_id=user_id,

            peso=peso,

            altura=altura
        )

    resultado = None

    simbolo = ""

    nome_operacao = ""


    if op == "soma":

        resultado = numero_a + numero_b

        simbolo = "+"

        nome_operacao = "Soma"


    elif op == "subtracao":

        resultado = numero_a - numero_b

        simbolo = "−"

        nome_operacao = "Subtração"


    elif op == "multiplicacao":

        resultado = numero_a * numero_b

        simbolo = "×"

        nome_operacao = "Multiplicação"


    elif op == "divisao":

        simbolo = "÷"

        nome_operacao = "Divisão"

        if numero_b == 0:

            return render_template(

                "math_result.html",

                erro="Não é possível dividir por zero.",

                resultado=None,

                numero_a=numero_a,

                numero_b=numero_b,

                simbolo=simbolo,

                nome_operacao=nome_operacao,

                user_id=user_id,

                peso=peso,

                altura=altura
            )

        resultado = numero_a / numero_b


    else:

        return render_template(

            "math_result.html",

            erro="Operação inválida.",

            resultado=None,

            numero_a=numero_a,

            numero_b=numero_b,

            simbolo="",

            nome_operacao="",

            user_id=user_id,

            peso=peso,

            altura=altura
        )


    return render_template(

        "math_result.html",

        erro=None,

        resultado=resultado,

        numero_a=numero_a,

        numero_b=numero_b,

        simbolo=simbolo,

        nome_operacao=nome_operacao,

        user_id=user_id,

        peso=peso,

        altura=altura
    )


# ============================================================
# IMC
# ============================================================

@app.route("/imc/<peso>/<altura>")
def imc_sem_usuario(peso, altura):

    return calcular_imc_resultado(
        None,
        peso,
        altura
    )


@app.route("/imc/<user_id>/<peso>/<altura>")
def imc(user_id, peso, altura):

    return calcular_imc_resultado(
        user_id,
        peso,
        altura
    )


def calcular_imc_resultado(
    user_id,
    peso,
    altura
):

    usuario = None

    if user_id:

        usuario = encontrar_usuario_por_id(
            user_id
        )

        if usuario is None:

            return redirect(
                url_for("login")
            )


    # ========================================================
    # CONVERSÃO DOS VALORES
    # ========================================================

    try:

        peso = float(peso)

        altura = float(altura)

    except (
        ValueError,
        TypeError
    ):

        return render_template(

            "imc.html",

            user_id=user_id,

            nome=(
                usuario.get(
                    "nome",
                    ""
                )
                if usuario
                else ""
            ),

            email=(
                usuario.get(
                    "email",
                    ""
                )
                if usuario
                else ""
            ),

            idade=(
                usuario.get(
                    "idade",
                    ""
                )
                if usuario
                else ""
            ),

            peso=peso,

            altura=altura,

            imc=None,

            classificacao=None,

            peso_min=None,

            peso_max=None,

            marcador=0,

            gordura=None,

            gordura_classificacao=None,

            recomendacao=None,

            sexo=None,

            erro="Peso ou altura inválidos."
        )


    # ========================================================
    # VALIDAÇÃO
    # ========================================================

    if peso <= 0 or altura <= 0:

        return render_template(

            "imc.html",

            user_id=user_id,

            nome=(
                usuario.get(
                    "nome",
                    ""
                )
                if usuario
                else ""
            ),

            email=(
                usuario.get(
                    "email",
                    ""
                )
                if usuario
                else ""
            ),

            idade=(
                usuario.get(
                    "idade",
                    ""
                )
                if usuario
                else ""
            ),

            peso=peso,

            altura=altura,

            imc=None,

            classificacao=None,

            peso_min=None,

            peso_max=None,

            marcador=0,

            gordura=None,

            gordura_classificacao=None,

            recomendacao=None,

            sexo=None,

            erro="Informe valores válidos para peso e altura."
        )


    # ========================================================
    # CALCULAR IMC
    # ========================================================

    valor_imc = calcular_imc(
        peso,
        altura
    )

    classificacao = classificar_imc(
        valor_imc
    )


    # ========================================================
    # PESO IDEAL
    # ========================================================

    peso_minimo, peso_maximo = calcular_peso_ideal(
        altura
    )


    # ========================================================
    # MARCADOR
    # ========================================================

    marcador = (
        (valor_imc - 10) / 30
    ) * 100

    marcador = max(
        2,
        min(
            98,
            marcador
        )
    )


    # ========================================================
    # DADOS EXTRAS
    # ========================================================

    idade_param = request.args.get(
        "idade",
        ""
    )

    sexo = request.args.get(
        "sexo",
        ""
    ).lower()

    idade_calculo = None

    gordura = None

    gordura_classificacao = None


    if idade_param:

        try:

            idade_calculo = int(
                idade_param
            )

        except ValueError:

            idade_calculo = None


    if (
        idade_calculo is None
        and usuario
    ):

        try:

            idade_calculo = int(
                usuario.get(
                    "idade",
                    0
                )
            )

        except (
            ValueError,
            TypeError
        ):

            idade_calculo = None


    if (
        idade_calculo
        and idade_calculo > 0
        and sexo in (
            "masculino",
            "feminino"
        )
    ):

        gordura = calcular_gordura(
            valor_imc,
            idade_calculo,
            sexo
        )

        gordura_classificacao = classificar_gordura(
            gordura,
            sexo
        )


    # ========================================================
    # RECOMENDAÇÃO
    # ========================================================

    recomendacao = obter_recomendacao(
        classificacao
    )


    # ========================================================
    # ATUALIZAR USUÁRIO
    # ========================================================

    if user_id:

        usuarios = carregar_usuarios()

        for usuario_item in usuarios:

            if usuario_item.get(
                "id"
            ) == user_id:

                usuario_item["peso"] = peso

                usuario_item["altura"] = altura

                usuario_item["imc"] = round(
                    valor_imc,
                    2
                )

                if idade_calculo:

                    usuario_item["idade"] = (
                        idade_calculo
                    )

                break

        salvar_usuarios(
            usuarios
        )


    # ========================================================
    # DADOS PARA O TEMPLATE
    # ========================================================

    nome = (
        usuario.get(
            "nome",
            ""
        )
        if usuario
        else ""
    )

    email = (
        usuario.get(
            "email",
            ""
        )
        if usuario
        else ""
    )

    idade_exibicao = (
        idade_calculo
        if idade_calculo
        else (
            usuario.get(
                "idade",
                ""
            )
            if usuario
            else ""
        )
    )


    # ========================================================
    # RESULTADO DO IMC
    # ========================================================

    return render_template(

        "imc.html",

        user_id=user_id,

        nome=nome,

        email=email,

        idade=idade_exibicao,

        peso=peso,

        altura=altura,

        imc=valor_imc,

        classificacao=classificacao,

        peso_min=peso_minimo,

        peso_max=peso_maximo,

        marcador=marcador,

        gordura=gordura,

        gordura_classificacao=gordura_classificacao,

        recomendacao=recomendacao,

        sexo=sexo,

        erro=None
    )


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )