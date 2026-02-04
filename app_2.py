import email
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

PRAZO_MAXIMO_DIAS = 20

def roles_required(*roles):
    """
        Decorator: roles_required(roles...)
        ----------------------------------------------------
        Restringe o acesso da rota aos papéis (roles) informados.

         Como funciona:
            - Lê o JWT atual
            - Busca o usuário pelo email (identity)
            - Verifica se o papel do usuário está na lista de roles permitidos
            - Caso positivo → permite o acesso
            - Caso negativo → retorna 403

         Exemplo de uso:
            @app.route('/admin')
            @jwt_required()
            @roles_required('admin', 'gerente')
            def rota_admin():
                return "Somente admins"
        """

    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            current_user = get_jwt_identity()
            db = session_local()
            try:
                sql = select(Usuarios).where(Usuarios.email == current_user)
                user = db.execute(sql).scalar()
                if user and user.papel in roles:
                    return fn(*args, **kwargs)
                return jsonify(msg="Acesso negado: privilégios insuficientes"), 403
            finally:
                db.close()

        return decorated

    return wrapper


@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    email = dados.get('email')
    senha = dados.get('senha')

    db_session = session_local()

    try:
        # Verifica se CPF e senha foram fornecidos
        if not email or not senha:
            return jsonify({'msg': 'Email e senha são obrigatórios'}), 400

        # Consulta o usuário pelo Email
        sql = select(Usuarios).where(Usuarios.email == email)
        user = db_session.execute(sql).scalar()

        # Verifica se o usuário existe e se a senha está correta
        if user and user.check_password_hash(senha):
            access_token = create_access_token(
                identity=email,
                additional_claims={
                    'id_usuario': user.id_usuario,
                    "papel": user.papel,
                }
            )  # Gera o token de acesso
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
    email = dados['email']
    papel = dados.get('papel', 'usuario')
    senha = dados['senha']
    endereco = dados['endereco']


    status_user = "Ativo"

    if not nome or not email or not senha or not cpf or not endereco  :
        return jsonify({"msg": "É necessário preencher todos os campos"}), 400


    #  Se o papel for admin → valida CPF
    if papel == "admin" or "usuario":
        if not cpf or len(cpf) != 11 or not cpf.isdigit():
            return jsonify({"msg": "O CPF deve conter exatamente 11 dígitos numéricos."}), 400
    else:
        #  Se não for admin → ignora CPF e zera para evitar lixo
        cpf = None
    db_session = session_local()

    try:
        # Verificar se o usuário já existe
        user_check = select(Usuarios).where(Usuarios.email == email)
        usuario_existente = db_session.execute(user_check).scalar()

        if usuario_existente:
            return jsonify({"msg": "Usuário já existe"}), 400

        novo_usuario = Usuarios(
            nome=nome,
            cpf=cpf,
            endereco=endereco,
            papel=papel,
            email=email,
            status_user=status_user
        )

        novo_usuario.set_senha_hash(senha)
        db_session.add(novo_usuario)
        db_session.commit()

        user_id = novo_usuario.id_usuario
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

        livros_emprestadoss = select(Emprestimos.livro_emprestado_id).where(Emprestimos.id == Livro.id_livro)
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
        livros_disponiveis = select(Emprestimos.livro_emprestado_id).where(Emprestimos.id == Livro.id_livro)
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
# @app.route('/emprestimo', methods=['GET'])
# def emprestimo():
#     # @jwt_required()
#     # @admin_required
#     """
#            Listar todos os emprestimos
#            :return:Listar todos os emprestimos
#
#            ## Resposta (JSON)
#                json
#            {
#                'lista_emprestimo': lista_emprestimo
#            }
#
#            #Erros possíveis:
#            Se inserir letras retornará uma mensagem de invalidez
#            """
#     db_session = session_local()
#     try:
#         sql_emprestimo = select(Emprestimos)
#         resultado_emprestimo = db_session.execute(sql_emprestimo).scalars()
#         lista_emprestimo = []
#         for n in resultado_emprestimo:
#             lista_emprestimo.append(n.serialize_emprestimo())
#             print(lista_emprestimo[-1])
#         return jsonify({
#             'lista_emprestimo': lista_emprestimo
#         })
#     except Exception as e:
#         return jsonify({"error": str(e)})
#     finally:
#         db_session.close()


@app.route('/emprestimo', methods=['GET'])
def emprestimo():
    db_session = session_local()
    try:
        # 🔥 Atualiza devoluções vencidas
        devolver_emprestimos_vencidos(db_session)

        resultado = db_session.execute(select(Emprestimos)).scalars()
        lista = [e.serialize_emprestimo() for e in resultado]

        return jsonify({"lista_emprestimo": lista})

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db_session.close()

def devolver_emprestimos_vencidos(db_session):
    hoje = datetime.now().date()

    emprestimos = db_session.execute(
        select(Emprestimos)
        .where(Emprestimos.status == "Ativo")
    ).scalars().all()

    for emp in emprestimos:
        data_prevista = datetime.strptime(emp.data_de_devolucao, '%d-%m-%Y').date()

        if data_prevista < hoje:
            emp.status = "Devolvido"
            # ❌ NÃO altera a data_de_devolucao
            # (ela já representa o prazo máximo)

    db_session.commit()


@app.route('/devolver_emprestimo/<int:id_emprestimo>', methods=['PUT'])
def devolver_emprestimo(id_emprestimo):
    db_session = session_local()
    try:
        emprestimo = db_session.query(Emprestimos).filter_by(
            id_emprestimo=id_emprestimo
        ).first()

        if not emprestimo:
            return jsonify({"error": "Empréstimo não encontrado"}), 404

        if emprestimo.status != "Ativo":
            return jsonify({
                "error": "Empréstimo não está ativo",
                "status_atual": emprestimo.status
            }), 400

        # 🔥 ALTERAÇÃO REAL
        emprestimo.status = "Devolvido"
        emprestimo.data_de_devolucao = datetime.now().strftime('%d-%m-%Y')

        db_session.add(emprestimo)   # 🔴 ESSENCIAL
        db_session.commit()

        return jsonify({
            "success": "Livro devolvido com sucesso",
            "status": emprestimo.status,
            "data_devolucao": emprestimo.data_de_devolucao
        }), 200

    except Exception as e:
        db_session.rollback()
        print("ERRO REAL DEVOLUÇÃO:", e)
        return jsonify({"error": str(e)}), 400
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
                "id": form_novo_livro.id_livro,
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
        if (not "cpf" in dados_usuario or not "nome" in dados_usuario or not "endereco" in dados_usuario or not
        "status_user" in dados_usuario ):
            return jsonify({
                'error': 'Campo inexistente'
            })

        if dados_usuario["cpf"] == "" or dados_usuario["nome"] == "" or dados_usuario["endereco"] == "" or dados_usuario["status_user"] == "":
            return jsonify({
                "error": "Preencher todos os campos"
            })


        else:
            nome = dados_usuario['nome']
            cpf = dados_usuario['cpf']
            endereco = dados_usuario['endereco']
            status_user = dados_usuario['status_user']

            form_novo_usuario = Usuarios(nome=nome,
                                         cpf=cpf,
                                         endereco=endereco,
                                         status_user=status_user
                                         )

            print(form_novo_usuario)
            cpf_existente = db_session.execute(select(Usuarios).filter_by(cpf=int(cpf))).scalar()
            if cpf_existente:
                return jsonify({'Este cpf já é existente'})
            form_novo_usuario.save(db_session)
            # db_session.close()
            # return jsonify({ })
            resultado = {
                "id": form_novo_usuario.id_usuario,
                "nome": nome,
                "cpf": cpf,
                "endereco": endereco,
                "status_user": status_user,
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
    db_session = session_local()
    try:
        dados = request.get_json()

        campos = ["livro_emprestado_id", "usuario_emprestado_id"]
        for campo in campos:
            if not dados.get(campo):
                return jsonify({'error': f'O campo "{campo}" é obrigatório'}), 400

        # 📌 Data do empréstimo é sempre HOJE
        data_emprestimo = datetime.now()
        data_devolucao = data_emprestimo + relativedelta(days=PRAZO_MAXIMO_DIAS)

        livro_id = int(dados['livro_emprestado_id'])
        usuario_id = int(dados['usuario_emprestado_id'])

        # Livro já emprestado?
        emprestimo_ativo = db_session.execute(
            select(Emprestimos)
            .where(Emprestimos.livro_emprestado_id == livro_id)
            .where(Emprestimos.status == "Ativo")
        ).scalar()

        if emprestimo_ativo:
            return jsonify({"error": "Livro já está emprestado!"}), 400

        novo = Emprestimos(
            data_de_emprestimo=data_emprestimo.strftime('%d-%m-%Y'),
            data_de_devolucao=data_devolucao.strftime('%d-%m-%Y'),
            livro_emprestado_id=livro_id,
            usuario_emprestado_id=usuario_id,
            status="Ativo"
        )

        novo.save(db_session)

        return jsonify({
            "success": "Empréstimo criado com sucesso!",
            "data_emprestimo": data_emprestimo.strftime('%d-%m-%Y'),
            "data_devolucao": data_devolucao.strftime('%d-%m-%Y'),
            "prazo_maximo": PRAZO_MAXIMO_DIAS
        }), 201

    except Exception as e:
        db_session.rollback()
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
                "id_livro": livro_resultado.id_livro,
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
        if (not "cpf" in dados_editar_usuario or not "nome" in dados_editar_usuario or not "endereco" in dados_editar_usuario
                or not "status_user" in dados_editar_usuario or not "email" in dados_editar_usuario):
            return jsonify({
                'error': 'Campo inexistente'
            }),400

        if dados_editar_usuario["cpf"] == "" or dados_editar_usuario["nome"] == "" or dados_editar_usuario[
            "endereco"] == "" or dados_editar_usuario["email"] == "":
            return jsonify({
                "error": "Preencher todos os campos"
            }),400

        else:
            # atualiza os dados
            usuario_resultado.nome = dados_editar_usuario['nome']
            usuario_resultado.cpf = dados_editar_usuario['cpf']
            usuario_resultado.email = dados_editar_usuario['email']
            usuario_resultado.endereco = dados_editar_usuario['endereco']
            usuario_resultado.status_user = dados_editar_usuario['status_user']
            usuario_resultado.save(db_session)
            # salva os dados alterados
            resultado = {
                "id_usuario": usuario_resultado.id_usuario,
                "nome": usuario_resultado.nome,
                "email": usuario_resultado.email,
                "cpf": usuario_resultado.cpf,
                "endereco": usuario_resultado.endereco,
                "status_user":usuario_resultado.status_user,
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
@app.route('/editar_emprestimo/<int:id_emprestimo>', methods=['PUT'])
def editar_emprestimo(id_emprestimo):
    db_session = session_local()
    try:
        dados = request.get_json()

        # 🔥 AQUI ESTÁ A CORREÇÃO REAL
        emprestimo = db_session.query(Emprestimos).filter_by(
            id=id_emprestimo
        ).first()

        if not emprestimo:
            return jsonify({"error": "Empréstimo não encontrado"}), 404

        if dados.get("status") == "Devolvido":
            emprestimo.status = "Devolvido"
            emprestimo.data_de_devolucao = datetime.now().strftime('%d-%m-%Y')

        db_session.add(emprestimo)
        db_session.commit()

        return jsonify({
            "success": "Empréstimo atualizado com sucesso",
            "id_emprestimo": emprestimo.id,
            "status": emprestimo.status,
            "data_de_devolucao": emprestimo.data_de_devolucao
        }), 200

    except Exception as e:
        db_session.rollback()
        print("ERRO EDITAR EMPRÉSTIMO:", e)
        return jsonify({"error": str(e)}), 400
    finally:
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
            'id': usuario.id_usuario,
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
            'id': livro.id_livro,
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

# @app.route('/deletar_usuario/<id_usuario>', methods=['DELETE'])
# def deletar_usuario(id_usuario):
#     """
#           deletar usuario
#           :return: deletar usuario
#           :param id_usuario:id_usuario
#
#           ## Resposta (JSON)
#               json
#           {
#              return jsonify({'success': "Usuario deletado com sucesso"})
#
#             }
#         """
#     usuario_resultado = db_session.execute(select(Usuarios).filter_by(id=id_usuario)).scalar()
#
#     if not usuario_resultado:
#         return jsonify({'erro': "Usuario não encontrado"})
#     usuario_resultado.delete_usuario()
#     return jsonify({'success': "Usuario deletado com sucesso"})
#
#
# @app.route('/deletar_livro/<id_livro>', methods=['DELETE'])
# def deletar_livro(id_livro):
#     """
#              deletar livro
#              :return: deletar livro
#              :param id_livro:id_livro
#
#              ## Resposta (JSON)
#                  json
#              {
#                 return jsonify({'success': "Livro deletado com sucesso"})
#                }
#            """
#     livro_resultado = db_session.execute(select(Livro).filter_by(id=int(id_livro))).scalar()
#
#     if not livro_resultado:
#         return jsonify({'error': 'Livro não encontrado'})
#     livro_resultado.delete_livro()
#     return jsonify({'success': "Livro deletado com sucesso"})



@app.route('/calcular_devolucao/<data_de_emprestimo>', methods=['GET'])
def calcular_devolucao(data_de_emprestimo):
    try:
        data_emprestimo = datetime.strptime(data_de_emprestimo, '%d-%m-%Y')
        data_devolucao = data_emprestimo + relativedelta(days=PRAZO_MAXIMO_DIAS)

        return jsonify({
            "devolucao": data_devolucao.strftime('%d-%m-%Y'),
            "prazo_maximo": PRAZO_MAXIMO_DIAS
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 400



if __name__ == "__main__":
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )



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



