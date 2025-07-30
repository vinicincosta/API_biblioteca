
from sys import exception
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from datetime import datetime
from models import *
from dateutil.relativedelta import relativedelta
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from functools import wraps

app = Flask (__name__)
app.config['JWT_SECRET_KEY'] = "03050710"
jwt = JWTManager(app)


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        current_user = get_jwt_identity()
        db_session = session_local()
        try:
            sql = select(Usuarios). where(Usuarios.cpf == current_user)
            user = db_session.execute(sql).scalar()
            if user and user.papel == 'admin':
                return fn(*args, **kwargs)
            return jsonify({'msg': 'Acesso negado: Requer privilégio de administrador'}), 403
        finally:
            db_session.close()
    return wrapper

@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    cpf = dados.get('cpf')
    senha = dados.get('senha')

    db_session = session_local()

    try:
        # Verifica se CPF e senha foram fornecidos
        if not cpf or not senha:
            return jsonify({'msg': 'CPF e senha são obrigatórios'}), 400

        # Consulta o usuário pelo CPF
        sql = select(Usuarios).where(Usuarios.cpf == cpf)
        user = db_session.execute(sql).scalar()

        # Verifica se o usuário existe e se a senha está correta
        if user and user.check_password_hash(senha):
            access_token = create_access_token(identity=cpf)  # Gera o token de acesso
            papel = user.papel  # Obtém o papel do usuário
            nome = user.nome  # Obtém o nome do usuário
            print(f"Login bem-sucedido: {nome}, Papel: {papel}")  # Diagnóstico
            return jsonify(access_token=access_token, papel=papel, nome=nome)  # Retorna o nome também

        print("Credenciais inválidas.")  # Diagnóstico
        return jsonify({'msg': 'Credenciais inválidas'}), 401

    finally:
        db_session.close()




@app.route('/cadastro', methods=['POST'])
def cadastro():
    dados = request.get_json()
    nome = dados['nome']
    cpf = dados['cpf']
    papel = dados.get('papel', 'usuario')
    senha = dados['senha']
    endereco = dados['endereco']

    if not nome or not cpf or not senha or not endereco:
        return jsonify({"msg": "Nome de usuário, CPF, senha e endereço são obrigatórios"}), 400

    # Verificação do CPF
    if len(cpf) != 11 or not cpf.isdigit():
        return jsonify({"msg": "O CPF deve conter exatamente 11 dígitos."}), 400

    db_session = session_local()
    try:
        # Verificar se o usuário já existe
        user_check = select(Usuarios).where(Usuarios.cpf == cpf)
        usuario_existente = db_session.execute(user_check).scalar()

        if usuario_existente:
            return jsonify({"msg": "Usuário já existe"}), 400

        novo_usuario = Usuarios(nome=nome, cpf=cpf, papel=papel, endereco=endereco)
        novo_usuario.set_senha_hash(senha)
        db_session.add(novo_usuario)
        db_session.commit()

        user_id = novo_usuario.id
        return jsonify({"msg": "Usuário criado com sucesso", "user_id": user_id}), 201
    except Exception as e:
        db_session.rollback()
        return jsonify({"msg": f"Erro ao registrar usuário: {str(e)}"}), 500
    finally:
        db_session.close()

@app.route('/')
def pagina_inicial():
    return 'Pagina inicial (API BIBLIOTECA)'


@app.route('/livro', methods=['GET'])
# @jwt_required()
def livro():

    # @admin_required
    """
               Listar todos os livros
               :return:Listar todos os livros cadastrados.

               ## Resposta (JSON)
                   json
               {
                   'lista_livro': lista_livro
               }

               #Erros possíveis:


               Se inserir letras retornará uma mensagem de invalidez
               """
    db_session = session_local()
    try:

        sql_livro = select(Livro)
        resultado_livro = db_session.execute(sql_livro).scalars()
        lista_livro = []
        for n in resultado_livro:
            lista_livro.append(n.serialize_livro())
            print(lista_livro[-1])
        return jsonify({
            'lista_livro': lista_livro
        })
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        db_session.close()


@app.route('/livros_disponiveis', methods=['GET'])
# @jwt_required()
    # @admin_required
def livros_disponiveis():


    """
                Listar os livros disponiveis
                :return:Listar os livros disponiveis

                ## Resposta (JSON)
                    json
                {
                    'livros_disponiveis': lista_livros
                }

                #Erros possíveis:
                Se inserir letras retornará uma mensagem de invalidez
                """
    db_session = session_local()
    try:

        livros_emprestadoss = select(Emprestimos.livro_emprestado_id).where(Emprestimos.id == Livro.id)
        lista_livros_emprestados = db_session.execute(livros_emprestadoss).scalars()
        todos_livros = db_session.execute(select(Livro)).scalars()
        print(lista_livros_emprestados)
        lista_livros = []
        for livr in todos_livros:
            if livr.id not in lista_livros_emprestados:
                lista_livros.append(livr.serialize_livro())

        return jsonify({'livros_disponiveis': lista_livros})
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        db_session.close()

# Rota Bloqueada
@app.route('/livros_emprestados', methods=['GET'])
def livros_emprestados():
    # @jwt_required()
    # @admin_required
    """
                Listar os livros emprestados
                :return:Listar os livros emprestados

                ## Resposta (JSON)
                    json
                {
                   livros_emprestados': lista_livros
                }

                #Erros possíveis:
                Se inserir letras retornará uma mensagem de invalidez
                """
    db_session = session_local()
    try:
        livros_disponiveis = select(Emprestimos.livro_emprestado_id).where(Emprestimos.id == Livro.id)
        lista_livros_disponiveis = db_session.execute(livros_disponiveis).scalars()
        todos_livro = db_session.execute(select(Livro)).scalars()
        print(lista_livros_disponiveis)
        lista_livros = []
        for livroo in todos_livro:
            if livroo.id in lista_livros_disponiveis:
                lista_livros.append(livroo.serialize_livro())

        return jsonify({'livros_emprestados': lista_livros})
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        db_session.close()

# Rota Bloqueada
@app.route('/historico_emprestimos/<int:id_usuario>', methods=['GET'])
def historico_emprestimos(id_usuario):
    # @jwt_required()
    # @admin_required
    """
        Listar os livros emprestados
        :return:Listar os livros emprestados por id_usuario
        :param id_usuario: id_usuario

        ## Resposta (JSON)
            json
        {
           livros_emprestados': lista_livros
        }

        #Erros possíveis:
        Se inserir letras retornará uma mensagem de invalidez
        """
    db_session = session_local()
    try:
        try:
            id_usuari = int(id_usuario)
            emprestimo_usuario = db_session.execute(select(Emprestimos).
                                                    where(
                Emprestimos.usuario_emprestado_id == id_usuari)).scalars().all()

        except ValueError:
            return jsonify({
                'error': 'Valor inserido invalido'
            })

        if not id_usuari:

            return jsonify({
                "error": "Este usuario não existe"
            })

        if not emprestimo_usuario:
            return jsonify({
                "error": "Este usuario não realizou empréstimos"
            })
        #
        # if emprestimo_usuario == id_usuario:
        #     return jsonify({'ERROR': 'Este usuario Ja existe'})

        else:
            emprestimo_livros = []
            for emprestimos in emprestimo_usuario:
                emprestimo_livros.append(emprestimos.serialize_emprestimo())

        return jsonify({
            "usuário": id_usuario,
            "historico_emprestimos": emprestimo_livros
        })

    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        db_session.close()

# Rota Bloqueada
@app.route('/usuario', methods=['GET'])
# @jwt_required()
# @admin_required

def usuario():


    """
        Listar todos os usuario
        :return:Listar todos os usuario

        ## Resposta (JSON)
            json
        {
            'lista_usuario': lista_usuario
        }

        #Erros possíveis:
        Se inserir letras retornará uma mensagem de invalidez
        """
    db_session = session_local()
    try:
        sql_usuario = select(Usuarios)
        resultado_usuario = db_session.execute(sql_usuario).scalars()
        lista_usuario = []
        for n in resultado_usuario:
            lista_usuario.append(n.serialize_usuario())
            print(lista_usuario[-1])
        return jsonify({
            'lista_usuario': lista_usuario
        })
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        db_session.close()

# Rota Bloqueada
@app.route('/emprestimo', methods=['GET'])
def emprestimo():
    # @jwt_required()
    # @admin_required
    """
           Listar todos os emprestimos
           :return:Listar todos os emprestimos

           ## Resposta (JSON)
               json
           {
               'lista_emprestimo': lista_emprestimo
           }

           #Erros possíveis:
           Se inserir letras retornará uma mensagem de invalidez
           """
    db_session = session_local()
    try:
        sql_emprestimo = select(Emprestimos)
        resultado_emprestimo = db_session.execute(sql_emprestimo).scalars()
        lista_emprestimo = []
        for n in resultado_emprestimo:
            lista_emprestimo.append(n.serialize_emprestimo())
            print(lista_emprestimo[-1])
        return jsonify({
            'lista_emprestimo': lista_emprestimo
        })
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        db_session.close()

# Rota Bloqueada
@app.route('/novo_livro', methods=['POST'])
def criar_livro():
    # @jwt_required()
    # @admin_required
    """
               Cadastrar um novo livro
               :return: Cadastrar novo livro

               ## Resposta (JSON)
                   json
               {
                resultado = [{
                    "titulo": titulo,
                    "autor": autor,
                    "ISBN": ISBN,
                    "resumo": resumo
                    {"success": "Livro cadastrado com sucesso!"}]
                    return jsonify(resultado)
               }
   """
    db_session = session_local()
    try:
        # quando clicar no botao de salva
        dados_livro = request.get_json()

        if not 'titulo' in dados_livro or not 'autor' in dados_livro or not 'ISBN' in dados_livro or not 'ISBN' in dados_livro or not 'leitura' in dados_livro:
            return jsonify({
                'error': 'Campo inexistente'
            })

        if dados_livro['titulo'] == "" or dados_livro['autor'] == "" or dados_livro['ISBN'] == "" or dados_livro[
            'resumo'] == "" or dados_livro['leitura'] == "":
            return jsonify({
                "error": "Preencher todos os campos"
            })

        else:
            titulo = dados_livro['titulo']
            autor = dados_livro['autor']
            ISBN = dados_livro['ISBN']
            resumo = dados_livro['resumo']
            leitura = dados_livro['leitura']
            form_novo_livro = Livro(titulo=titulo,
                                    autor=autor,
                                    ISBN=int(ISBN),
                                    resumo=resumo,
                                    leitura=leitura
                                    )
            print(form_novo_livro)
            form_novo_livro.save(db_session)

            resultado = {
                "id": form_novo_livro.id,
                "titulo": titulo,
                "autor": autor,
                "ISBN": ISBN,
                "resumo": resumo,
                "leitura": leitura,
                "success": "Livro cadastrado com sucesso!"
            }
            # dentro do url sempre chamar função
            return jsonify(resultado), 201

    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        db_session.close()


# Rota Bloqueada
@app.route('/novo_usuario', methods=['POST'])
def criar_usuario():
    # @jwt_required()
    # @admin_required
    """
          Cadastrar um novo usuario
          :return: Cadastrar novo usuario

          ## Resposta (JSON)
              json
          {
            resultado = [{
            "nome": nome,
            "cpf": cpf,
            "endereco": endereco,
            {"success": "Usuario cadastrado com sucesso!"}]
            return jsonify(resultado)
            }
    """
    db_session = session_local()
    try:
        dados_usuario = request.get_json()
        # print(dados_usuario)
        # print(dados_usuario["cpf"])
        # quando clicar no botao de salva
        if not "cpf" in dados_usuario or not "nome" in dados_usuario or not "endereco" in dados_usuario:
            return jsonify({
                'error': 'Campo inexistente'
            })

        if dados_usuario["cpf"] == "" or dados_usuario["nome"] == "" or dados_usuario["endereco"] == "":
            return jsonify({
                "error": "Preencher todos os campos"
            })


        else:
            nome = dados_usuario['nome']
            cpf = dados_usuario['cpf']
            endereco = dados_usuario['endereco']

            form_novo_usuario = Usuarios(nome=nome,
                                         cpf=cpf,
                                         endereco=endereco,
                                         )

            print(form_novo_usuario)
            cpf_existente = db_session.execute(select(Usuarios).filter_by(cpf=int(cpf))).scalar()
            if cpf_existente:
                return jsonify({'Este cpf já é existente'})
            form_novo_usuario.save(db_session)
            # db_session.close()
            # return jsonify({ })
            resultado = {
                "id": form_novo_usuario.id,
                "nome": nome,
                "cpf": cpf,
                "endereco": endereco,
                "success": "Usuario cadastrado com sucesso!"
            }
            # dentro do url sempre chamar função
            return jsonify(resultado), 201
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        db_session.close()


@app.route('/novo_emprestimo', methods=['POST'])
def criar_emprestimo():
    """
    Cadastrar um novo empréstimo
    """
    db_session = session_local()
    try:
        dados_emprestimo = request.get_json()

        # Validação dos campos obrigatórios
        campos_obrigatorios = ["data_de_emprestimo", "data_de_devolucao", "livro_emprestado_id", "usuario_emprestado_id"]
        for campo in campos_obrigatorios:
            if not dados_emprestimo.get(campo):
                return jsonify({'error': f'O campo "{campo}" é obrigatório'}), 400

        # Conversão de dados
        data_de_emprestimo = datetime.strptime(dados_emprestimo['data_de_emprestimo'], '%d-%m-%Y')
        data_de_devolucao = datetime.strptime(dados_emprestimo['data_de_devolucao'], '%d-%m-%Y')
        livro_emprestado_id = int(dados_emprestimo['livro_emprestado_id'])
        usuario_emprestado_id = int(dados_emprestimo['usuario_emprestado_id'])

        # Verificar se o livro está emprestado no momento
        livro_ja_emprestado = db_session.execute(
            select(Emprestimos).where(Emprestimos.livro_emprestado_id == livro_emprestado_id)
        ).scalar()

        if livro_ja_emprestado:
            # Verifica se o status do livro é "devolvido"
            if livro_ja_emprestado.status != "Devolvido":
                return jsonify({"error": "Livro já está emprestado!"}), 400

        # Verificar se o usuário existe
        usuario = db_session.execute(
            select(Usuarios).where(Usuarios.id == usuario_emprestado_id)
        ).scalar()

        if not usuario:
            return jsonify({"error": "Usuário não encontrado!"}), 400

        # Verificar se o livro existe
        livro = db_session.execute(
            select(Livro).where(Livro.id == livro_emprestado_id)
        ).scalar()

        if not livro:
            return jsonify({'error': 'Livro não encontrado'}), 400

        # Determinar o status
        status = 'Ativo'
        data_atual = datetime.now()

        # Verifica se a data de devolução é maior que a data atual
        # if data_de_devolucao < data_atual:
        #     status = 'Atrasado'

        # Criar o empréstimo
        novo_emprestimo = Emprestimos(
            data_de_emprestimo=data_de_emprestimo.strftime('%d-%m-%Y'),
            data_de_devolucao=data_de_devolucao.strftime('%d-%m-%Y'),
            livro_emprestado_id=livro_emprestado_id,
            usuario_emprestado_id=usuario_emprestado_id,
            status=status
        )

        novo_emprestimo.save(db_session)

        resultado = {
            "success": "Empréstimo cadastrado com sucesso!"
        }

        return jsonify(resultado), 201

    except Exception as e:
        db_session.rollback()
        print(e)
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()

# Rota Bloqueada
@app.route('/editar_livro/<id_livro>', methods=['PUT'])
def editar_livro(id_livro):
    # @jwt_required()
    # @admin_required
    """
                editar um livro
                :return: Editar livro
                :param id_livro:id_livro

                ## Resposta (JSON)
                    json
                {
                  resultado = [{
                        "titulo": livro_resultado.titulo,
                        "autor": livro_resultado.autor,
                        "ISBN": livro_resultado.isbn,
                        "resumo": livro_resultado.resumo,
                  }
         """
    db_session = session_local()
    try:
        dados_editar_livro = request.get_json()

        # busca de acordo com o id, usando o db_session
        livro_resultado = db_session.execute(select(Livro).filter_by(id=int(id_livro))).scalar()
        print(livro_resultado)
        # verifica se existe
        if not livro_resultado:
            return jsonify({
                "error": "Livro não encontrado"
            }), 400

        if not 'titulo' in dados_editar_livro or not 'autor' in dados_editar_livro or not 'ISBN' in dados_editar_livro or not 'ISBN' in dados_editar_livro or not 'leitura' in dados_editar_livro:
            return jsonify({
                'error': 'Campo inexistente'
            }), 400

        if dados_editar_livro['titulo'] == "" or dados_editar_livro['autor'] == "" or dados_editar_livro['ISBN'] == "" or dados_editar_livro['resumo'] == "" or dados_editar_livro['leitura'] == "":
            return jsonify({
                "error": "Preencher todos os campos"
            }), 400

        else:
            # atualiza os dados
            livro_resultado.titulo = dados_editar_livro['titulo']
            livro_resultado.autor = dados_editar_livro['autor']
            livro_resultado.isbn = dados_editar_livro['ISBN']
            livro_resultado.resumo = dados_editar_livro['resumo']
            livro_resultado.leitura = dados_editar_livro['leitura']
            # salva os dados alterados
            livro_resultado.save(db_session)

            resultado = {
                "id_livro": livro_resultado.id,
                "titulo": livro_resultado.titulo,
                "autor": livro_resultado.autor,
                "ISBN": livro_resultado.isbn,
                "resumo": livro_resultado.resumo,
                "leitura": livro_resultado.leitura,
                "success": "Livro editado com sucesso!"
            }

            # dentro do url sempre chamar função
            return jsonify(resultado), 200

    except ValueError:
        return jsonify({
            'error': 'Valor inserido invalido'
        }), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()

# Rota Bloqueada
@app.route('/editar_usuario/<id_usuario>', methods=['PUT'])
def editar_usuario(id_usuario):
    # @jwt_required()
    # @admin_required
    """
                   editar usuario
                   :return: Editar Usuario
                   :param id_usuario:id_usuario

                   ## Resposta (JSON)
                       json
                   {
                     resultado = [{
                        "nome": usuario_resultado.nome,
                        "cpf": usuario_resultado.cpf,
                        "endereco": usuario_resultado.endereco
                     }
             """
    db_session = session_local()
    try:
        dados_editar_usuario = request.get_json()
        # busca de acordo com o id, usando o db_session
        usuario_resultado = db_session.execute(select(Usuarios).filter_by(id=int(id_usuario))).scalar()
        print(usuario_resultado)
        # verifica se existe
        if not usuario_resultado:
            return jsonify({
                "error": "Usuário não encontrado"
            }),400

        # verificação dos dados
        if not "cpf" in dados_editar_usuario or not "nome" in dados_editar_usuario or not "endereco" in dados_editar_usuario:
            return jsonify({
                'error': 'Campo inexistente'
            }),400

        if dados_editar_usuario["cpf"] == "" or dados_editar_usuario["nome"] == "" or dados_editar_usuario[
            "endereco"] == "":
            return jsonify({
                "error": "Preencher todos os campos"
            }),400

        else:
            # atualiza os dados
            usuario_resultado.nome = dados_editar_usuario['nome']
            usuario_resultado.cpf = dados_editar_usuario['cpf']
            usuario_resultado.endereco = dados_editar_usuario['endereco']
            usuario_resultado.save(db_session)
            # salva os dados alterados
            resultado = {
                "id_usuario": usuario_resultado.id,
                "nome": usuario_resultado.nome,
                "cpf": usuario_resultado.cpf,
                "endereco": usuario_resultado.endereco,
                "success": "Usuario editado com sucesso!"
            }

            # dentro do url sempre chamar função
            return jsonify(resultado), 200

    except ValueError:
        return jsonify({
            'error': 'Valor inserido invalido'
        }), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:  # Finaliza a sessão
        db_session.close()

# Rota Bloqueada
@app.route('/editar_emprestimo/<id_emprestimo>', methods=['PUT'])
def editar_emprestimo(id_emprestimo):
    # @jwt_required()
    # @admin_required
    """
           editar emprestimo
           :return: Editar emprestimo
           :param id_emprestimo:id_emprestimo

           ## Resposta (JSON)
               json
           {
             resultado = [{
                   "data_de_emprestimo": emprestimo_resultado.data_de_emprestimo,
                    "data_de_devolucao": emprestimo_resultado.data_de_devolucao,
                    "livro_emprestado_id": emprestimo_resultado.livro_emprestado_id,
                    "usuario_emprestado_id": emprestimo_resultado.usuario_emprestado_id,
             }
     """
    db_session = session_local()
    try:
        dados_editar_emprestimo = request.get_json()
        # busca de acordo com o id, usando o db_session
        emprestimo_resultado = db_session.execute(select(Emprestimos).filter_by(id=int(id_emprestimo))).scalar()
        print(emprestimo_resultado)
        # verifica se existe
        if not emprestimo_resultado:
            return jsonify({
                "error": "Emprestimo não encontrado"
            }),400

        emprestimo_resultado.status = dados_editar_emprestimo['status']
        # Verificar se o usuário existe
        usuario = db_session.execute(
            select(Usuarios).where(Usuarios.id == emprestimo_resultado.usuario_emprestado_id)
        ).scalar()

        if not usuario:
            return jsonify({"error": "Usuário não encontrado!"})

        # Verificar se o livro existe
        livro = db_session.execute(
            select(Livro).where(Livro.id == emprestimo_resultado.livro_emprestado_id)
        ).scalar()

        if not livro:
            return jsonify({'error': 'Este livro não existe'})
        else:
            # atualiza os dados
            # emprestimo_resultado.data_de_emprestimo = dados_editar_emprestimo['data_de_emprestimo']
            # emprestimo_resultado.data_de_devolucao = dados_editar_emprestimo['data_de_devolucao']
            # emprestimo_resultado.livro_emprestado_id = dados_editar_emprestimo['livro_emprestado_id']
            # emprestimo_resultado.usuario_emprestado_id = dados_editar_emprestimo['usuario_emprestado_id']
            emprestimo_resultado.status = dados_editar_emprestimo['status']
            # salva os dados alterados
            emprestimo_resultado.save(db_session)

            resultado = {
                "status": emprestimo_resultado.status,
                "success": "Empréstimo editado com sucesso!"
            }, 200

            # dentro do url sempre chamar função
            return jsonify(resultado)

    except ValueError:
        return jsonify({
            'error': 'Valor inserido invalido'
        }), 400

    except Exception as e:
        return jsonify({"error": str(e)})
    finally:  # Finaliza a sessão
        db_session.close()


# Rota Bloqueada
@app.route('/get_usuario/<id_usuario>', methods=['GET'])
def get_usuario(id_usuario):
    # @jwt_required()
    # @admin_required
    """
              buscar usuario
              :return: Buscar usuario
              :param id_usuario:id_usuario

              ## Resposta (JSON)
                  json
              {
                resultado = [{
                   'id': usuario.id,
                    'nome': usuario.nome,
                    'cpf': usuario.cpf,
                    'endereco': usuario.endereco,
                }
    """
    db_session = session_local()
    try:
        usuario = db_session.execute(select(Usuarios).filter_by(id=int(id_usuario))).scalar()

        if not usuario:
            return jsonify({
                "erro": 'usuário não encontrado'
            })

        return jsonify({
            "success": "Usuario encontrado com sucesso",
            'id': usuario.id,
            "nome": usuario.nome,
            'cpf': usuario.cpf,
            'endereco': usuario.endereco,
        }), 200
    except ValueError:
        return jsonify({
            'error': 'Valor inserido invalido'
        })
    finally:
        db_session.close()

# Rota Bloqueada
@app.route('/get_livro/<id_livro>', methods=['GET'])
def get_livro(id_livro):
    # @jwt_required()
    # @admin_required
    """
                  buscar livro
                  :return: Buscar livro
                  :param id_livro:id_livro

                  ## Resposta (JSON)
                      json
                  {
                    resultado = [{
                    'id': livro.id,
                    'Titulo': livro.titulo,
                    'Autor': livro.autor,
                    'resumo': livro.resumo,
                    'isbn': livro.ISBN,

                    }
    """
    db_session = session_local()
    try:
        livro = db_session.execute(select(Livro).filter_by(id=int(id_livro))).scalar()

        if not livro:
            return jsonify({
                "erro": 'livro não encontrado'
            })

        return jsonify({
            "sucess": "Livro buscado com sucesso",
            'id': livro.id,
            'Titulo': livro.titulo,
            'Autor': livro.autor,
            'resumo': livro.resumo,
            'isbn': livro.ISBN,

        })
    except ValueError:
        return jsonify({
            'error': 'Valor inserido invalido'
        })
    finally:
        db_session.close()


# @app.route('/get_emprestimo/<id_emprestimo>', methods=['GET'])
# def get_emprestimo(id_emprestimo):
#     emprestimos = db_session.execute(select(Emprestimos).filter_by(id=int(id_emprestimo))).scalar()
#
#     if not emprestimos:
#         return jsonify({'error': 'Empréstimo não encontrado'})
#
#     return jsonify({
#         "sucess": "Emprestimo buscado com sucesso",
#         'id': Emprestimos.id,
#         'data de emprestimo': Emprestimos.data_de_emprestimo,
#         'data de devolução': Emprestimos.data_de_devolucao,
#         'Livros emprestados': Emprestimos.livro_emprestado_id,
#         'Usuário emprestimo': Emprestimos.usuario_emprestado_id,
#     })

@app.route('/deletar_usuario/<id_usuario>', methods=['DELETE'])
def deletar_usuario(id_usuario):
    """
          deletar usuario
          :return: deletar usuario
          :param id_usuario:id_usuario

          ## Resposta (JSON)
              json
          {
             return jsonify({'success': "Usuario deletado com sucesso"})

            }
        """
    usuario_resultado = db_session.execute(select(Usuarios).filter_by(id=id_usuario)).scalar()

    if not usuario_resultado:
        return jsonify({'erro': "Usuario não encontrado"})
    usuario_resultado.delete_usuario()
    return jsonify({'success': "Usuario deletado com sucesso"})


@app.route('/deletar_livro/<id_livro>', methods=['DELETE'])
def deletar_livro(id_livro):
    """
             deletar livro
             :return: deletar livro
             :param id_livro:id_livro

             ## Resposta (JSON)
                 json
             {
                return jsonify({'success': "Livro deletado com sucesso"})
               }
           """
    livro_resultado = db_session.execute(select(Livro).filter_by(id=int(id_livro))).scalar()

    if not livro_resultado:
        return jsonify({'error': 'Livro não encontrado'})
    livro_resultado.delete_livro()
    return jsonify({'success': "Livro deletado com sucesso"})


@app.route('/calcular_devolucao/<data_de_emprestimo>+<prazo>', methods=['GET'])
def calcular_devolucao(data_de_emprestimo, prazo):
    try:
        # Converte a data de empréstimo para um objeto datetime
        data_emprestimo = datetime.strptime(data_de_emprestimo, '%d-%m-%Y')

        # Calcula a data de devolução com base na data de empréstimo
        data_calculada = data_emprestimo + relativedelta(days=int(prazo))

        return jsonify({
            "devolucao": data_calculada.strftime('%d-%m-%Y'),
        }), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 400




if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)


# create table EMPRESTIMOS
# (
#     id                    SERIAL not null
#         primary key,
#     data_de_emprestimo    VARCHAR not null,
#     data_de_devolucao     VARCHAR not null,
#     livro_emprestado_id   INTEGER
#         references LIVROS(id),
#     usuario_emprestado_id INTEGER
#         references USUARIOS(id)
# );


# create table LIVROS
# (
#     id     SERIAL not null
#         primary key,
#     titulo TEXT not null,
#     autor  TEXT not null,
#     ISBN   INTEGER not null,
#     resumo TEXT not null
# );
#
# create table USUARIOS
# (
#     id       SERIAL not null
#         primary key,
#     nome     VARCHAR not null,
#     cpf      VARCHAR not null,
#     endereco VARCHAR not null
# );







@app.route("/validade/<data_str>/<valor>/<unidade>", methods=["GET"])
def calcular_validade(data_str, valor, unidade, ):
    """
    Calcula a data de validade de um produto com base na data de fabricação e no tempo informado.

    :param data_str: Ano da data de fabricação./ Mês da data de fabricação./Dia da data de fabricação.
    :param valor: Quantidade de tempo a adicionar.
    :param unidade: Unidade de tempo (dias, semanas, meses, anos).

    :return: JSON contendo a data de cadastro, validade em diferentes unidades e data de vencimento.
    """
    try:
        data_entrada = datetime.strptime(data_str, '%d-%m-%Y')

        # Criar a data de fabricação
        data_fabricacao = datetime(data_entrada.year, data_entrada.month, data_entrada.day)

        # Definir os incrementos com base na unidade fornecida
        unidades_validas = {
            "dias": relativedelta(days=int(valor)),
            "semanas": relativedelta(weeks=int(valor)),
            "meses": relativedelta(months=int(valor)),
            "anos": relativedelta(years=int(valor)),
        }

        # data atual
        data_atual = datetime.now()

        # Calcular a data de validade
        data_validade = data_fabricacao + unidades_validas[unidade]

        # Calcular validade em todas as unidades
        diferenca_dias = (data_validade - data_fabricacao).days
        diferenca_semanas = diferenca_dias // 7
        diferenca_meses = diferenca_dias // 30
        diferenca_anos = diferenca_dias // 365

        # Retornar resposta JSON
        return jsonify({
            'data_atual': data_atual.strftime("%d/%m/%Y | %H:%M:%S"),
            "data_validade": data_validade.strftime("%d/%m/%Y"),
            'data de cadastro': data_fabricacao.strftime("%d/%m/%Y | %H:%M:%S"),
            "validade": {
                "dias": diferenca_dias,
                "semanas": diferenca_semanas,
                "meses": diferenca_meses,
                "anos": diferenca_anos
            },

        })

    except ValueError:
        return jsonify({"erro": "Os parâmetros inseridos são inválidos!"}), 400