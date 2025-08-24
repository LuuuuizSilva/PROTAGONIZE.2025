from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

# Cria o aplicativo Flask, que é a base do nosso site.
app = Flask(__name__)
# A 'chave secreta' é usada para manter as sessões seguras, como o login da instituição.
app.secret_key = 'chave_secreta_super_segura' 

# Função para conectar ao banco de dados.
# Pense nisso como abrir um livro de endereços digital.
def get_db_connection():
    return pymysql.connect(
        host='localhost', # Onde o banco de dados está. 'localhost' significa no seu próprio computador.
        user='root',      # O nome de usuário para acessar o banco.
        password='',      # A senha, que neste caso está vazia.
        db='protagonize'  # O nome do banco de dados que estamos usando.
    )

# A rota principal do site, que é a página inicial (/).
@app.route('/')
def index():
    # O site exibe a página principal 'index.html'.
    return render_template('index.html')

# Rota para cadastrar um voluntário (estudante).
# A rota aceita tanto a visualização da página ('GET') quanto o envio do formulário ('POST').
@app.route('/cadastrar_estudante', methods=['GET', 'POST'])
def cadastrar_estudante():
    # Se o formulário foi enviado (método 'POST').
    if request.method == 'POST':
        # Pega as informações do formulário (nome, cpf, etc.).
        nome = request.form['nome']
        cpf = request.form['cpf']
        email = request.form['email']
        telefone = request.form['telefone']
        idade = request.form['idade']
        endereco = request.form['endereco']
        
        # Conecta ao banco de dados.
        conn = get_db_connection()
        # Salva as informações do voluntário na tabela 'estudantes'.
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO estudantes (nome, cpf, email, telefone, idade, endereco) VALUES (%s, %s, %s, %s, %s, %s)", 
                (nome, cpf, email, telefone, idade, endereco))
                # Confirma que os dados foram salvos.
                conn.commit()
        # Redireciona o usuário de volta para a página inicial.
        return redirect(url_for('index'))
    # Se a página foi apenas acessada (método 'GET'), exibe o formulário de cadastro.
    return render_template('cadastrar_estudante.html')

# Rota para cadastrar uma instituição.
# Também aceita visualização da página ('GET') e envio do formulário ('POST').
@app.route('/cadastrar_instituicao', methods=['GET', 'POST'])
def cadastrar_instituicao():
    # Se o formulário foi enviado.
    if request.method == 'POST':
        # Pega as informações da instituição.
        nome = request.form['nome']
        cnpj = request.form['cnpj']
        endereco = request.form ['endereco']
        telefone = request.form['telefone']
        descricao = request.form['descricao']
        senha = request.form['senha']
        
        # Conecta ao banco de dados.
        conn = get_db_connection()
        # Salva as informações na tabela 'instituicoes'.
        with conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO instituicoes (nome, cnpj, endereco, telefone, descricao, senha) VALUES (%s, %s, %s, %s, %s, %s)", 
                (nome, cnpj, endereco, telefone, descricao, senha))
                # Confirma a gravação dos dados.
                conn.commit()
        # Redireciona para a página inicial.
        return redirect(url_for('index'))
    # Se a página foi apenas acessada, exibe o formulário de cadastro.
    return render_template('cadastrar_instituicao.html')

# Rota de login para as instituições.
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Se o formulário de login foi enviado.
    if request.method == 'POST':
        # Pega o CNPJ e a senha do formulário.
        cnpj = request.form['login_acesso']
        senha = request.form['senha_acesso']
        
        # Conecta ao banco de dados para verificar as credenciais.
        conn = get_db_connection()
        
        with conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                # Busca a instituição no banco de dados com o CNPJ e a senha fornecidos.
                query = "SELECT * FROM instituicoes WHERE cnpj = %s AND senha = %s"
                cursor.execute(query, (cnpj, senha))
                resultado = cursor.fetchone()

            # Se encontrou uma instituição (login bem-sucedido).
            if resultado:
                # Salva o CNPJ em uma sessão, como um 'crachá' de acesso.
                session['cnpj'] = resultado['cnpj'] 
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    # Busca a lista de voluntários para exibir na tela.
                    cursor.execute("SELECT nome, endereco, idade FROM estudantes")
                    estudantes = cursor.fetchall()
                # Exibe a página de login com a lista de voluntários e uma mensagem de sucesso.
                return render_template('login.html', estudantes=estudantes, sucesso="Login realizado com sucesso!")
            else:
                # Se não encontrou (login falhou), exibe uma mensagem de erro na mesma página.
                return render_template('login.html', erro="CNPJ ou senha incorretos.")
    # Se a página de login foi acessada sem o envio do formulário, ela é exibida normalmente.
    return render_template('login.html')

# Rota para a página de planos.
@app.route('/planos')
def planos():
    # Apenas exibe a página 'planos.html'.
    return render_template('planos.html', descricao=( 
        "Uma parceria que gera impacto social. "
        "Ao fazer parte do Protagonize, sua instituição não apenas preenche vagas de voluntariado," 
        "mas investe em um ciclo de transformação social. Você oferece uma oportunidade real para que pessoas da periferia apliquem seus conhecimentos e ganhem experiência, enquanto sua equipe recebe o apoio de talentos motivados e engajados."
        ))

# Rota para a página de contrato.
@app.route('/contrato')
def contrato():
    # Verifica se a instituição está logada (se o 'crachá' existe na sessão).
    if 'cnpj' in session:
        # Se estiver, exibe a página de contrato.
        return render_template('contrato.html')
    # Se não estiver logada, redireciona para a página de login.
    return redirect(url_for('login'))

# Rota para sair da conta.
@app.route('/logout')
def logout():
    # Remove o 'crachá' (CNPJ) da sessão.
    session.pop('cnpj', None)
    # Redireciona para a página inicial.
    return redirect(url_for('index'))

# Inicia o servidor do aplicativo.
if __name__ == '__main__':
    # 'debug=True' permite que o programa se reinicie automaticamente quando você fizer uma mudança, útil para testes.
    app.run(debug=True)