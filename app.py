from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from models import *

app = Flask(__name__)


@app.route('/')
def pagina_inicial():
    return 'Pagina inicial (API BIBLIOTECA)'


@app.route('/livro', methods=['GET'])
def livro():
    sql_livro = select(Livro)
    resultado_livro = db_session.execute(sql_livro).scalars()
    lista_livro = []
    for n in resultado_livro:
        lista_livro.append(n.serialize_livro())
        print(lista_livro[-1])
    return jsonify({
        'lista_livro': lista_livro
    })


@app.route('/livros_disponiveis', methods=['GET'])
def livros_disponiveis():
    livros_emprestadoss = select(Emprestimos.livro_emprestado_id).where(Emprestimos.id == Livro.id)
    lista_livros_emprestados = db_session.execute(livros_emprestadoss).scalars()
    todos_livros = db_session.execute(select(Livro)).scalars()
    print(lista_livros_emprestados)
    lista_livros = []
    for livr in todos_livros:
        if livr.id not in lista_livros_emprestados:
            lista_livros.append(livr.serialize_livro())

    return jsonify({'livros_disponiveis': lista_livros})


@app.route('/livros_emprestados', methods=['GET'])
def livros_emprestados():
    livros_disponiveis = select(Emprestimos.livro_emprestado_id).where(Emprestimos.id == Livro.id)
    lista_livros_disponiveis = db_session.execute(livros_disponiveis).scalars()
    todos_livro = db_session.execute(select(Livro)).scalars()
    print(lista_livros_disponiveis)
    lista_livros = []
    for livroo in todos_livro:
        if livroo.id in lista_livros_disponiveis:
            lista_livros.append(livroo.serialize_livro())

    return jsonify({'livros_emprestados': lista_livros})


@app.route('/historico_emprestimos/<int:id_usuario>', methods=['GET'])
def historico_emprestimos(id_usuario):
    try:
        id_usuari = int(id_usuario)
        emprestimo_usuario = db_session.execute(select(Emprestimos).
                                                where(Emprestimos.usuario_emprestado_id == id_usuari)).scalars().all()

    except ValueError:
        return jsonify({
        'error': 'Valor inserido invalido'
    })

    if not emprestimo_usuario:
        return jsonify({
            "error": "Este usuario não existe"
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




@app.route('/usuario', methods=['GET'])
def usuario():
    sql_usuario = select(Usuarios)
    resultado_usuario = db_session.execute(sql_usuario).scalars()
    lista_usuario = []
    for n in resultado_usuario:
        lista_usuario.append(n.serialize_usuario())
        print(lista_usuario[-1])
    return jsonify({
        'lista_usuario': lista_usuario
    })


@app.route('/emprestimo', methods=['GET'])
def emprestimo():
    sql_emprestimo = select(Emprestimos)
    resultado_emprestimo = db_session.execute(sql_emprestimo).scalars()
    lista_emprestimo = []
    for n in resultado_emprestimo:
        lista_emprestimo.append(n.serialize_emprestimo())
        print(lista_emprestimo[-1])
    return jsonify({
        'lista_emprestimo': lista_emprestimo
    })


@app.route('/novo_livro', methods=['POST'])
def criar_livro():
    # quando clicar no botao de salva
    if request.method == "POST":

        if (not request.form['form_titulo'] or not request.form['form_autor']
                or not request.form['form_ISBN'] or not request.form['form_resumo']):
            print('teste')
            return jsonify({"error": "Preencher todos os campos"})
        else:
            titulo = request.form['form_titulo']
            autor = request.form['form_autor']
            ISBN = request.form['form_ISBN']
            resumo = request.form['form_resumo']
            form_novo_livro = Livro(titulo=titulo,
                                    autor=autor,
                                    ISBN=int(ISBN),
                                    resumo=resumo
                                    )
            print(form_novo_livro)
            form_novo_livro.save()
            # db_session.close()
            # return jsonify({ })

            # dentro do url sempre chamar função

            return jsonify({
                "success": "Livro cadastrado com sucesso!",
                'titulo': form_novo_livro.titulo,
                'autor': form_novo_livro.autor,
                'ISBN': form_novo_livro.ISBN,
                'resumo': form_novo_livro.resumo,
            })


@app.route('/novo_usuario', methods=['POST'])
def criar_usuario():
    # quando clicar no botao de salva
    if request.method == "POST":

        if (not request.form['form_nome'] or not request.form['form_cpf']
                or not request.form['form_endereco']):
            print('teste')
            return jsonify({"error": "Preencher todos os campos"})
        else:
            nome = request.form['form_nome']
            cpf = request.form['form_cpf']
            endereco = request.form['form_endereco']
            form_novo_usuario = Usuarios(nome=nome,
                                         cpf=cpf,
                                         endereco=endereco,
                                         )

            print(form_novo_usuario)
            cpf_existente = db_session.execute(select(Usuarios).filter_by(cpf=int(cpf))).scalar()
            if cpf_existente:
                return jsonify({'Este cpf já é existente'})
            form_novo_usuario.save()
            # db_session.close()
            # return jsonify({ })

            # dentro do url sempre chamar função

            return jsonify({
                "success": "Usuario cadastrado com sucesso!",
                "nome": form_novo_usuario.nome,
                "cpf": form_novo_usuario.cpf,
                "endereco": form_novo_usuario.endereco,
            })


@app.route('/novo_emprestimo', methods=['POST'])
def criar_emprestimo():
    # quando clicar no botao de salva
    if request.method == "POST":

        if (not request.form['form_data_de_emprestimo'] or not request.form['form_data_de_devolucao']
                or not request.form['form_livro_emprestado_id'] or not request.form['form_usuario_emprestado_id']):
            print('teste')
            return jsonify({"error": "Preencher todos os campos"})
        else:
            data_de_emprestimo = request.form['form_data_de_emprestimo']
            data_de_devolucao = request.form['form_data_de_devolucao']
            livro_emprestado_id = request.form['form_livro_emprestado_id']
            usuario_emprestado_id = request.form['form_usuario_emprestado_id']
            form_novo_emprestimo = Emprestimos(data_de_emprestimo=data_de_emprestimo,
                                               data_de_devolucao=data_de_devolucao,
                                               livro_emprestado_id=int(livro_emprestado_id),
                                               usuario_emprestado_id=int(usuario_emprestado_id)

                                               )
            print(form_novo_emprestimo)
            form_novo_emprestimo.save()
            # db_session.close()
            # return jsonify({ })

            # dentro do url sempre chamar função

            return jsonify({
                "success": "Usuario cadastrado com sucesso!",
                "data_de_emprestimo": data_de_emprestimo,
                "data_de_devolucao": data_de_devolucao,
                "livro_emprestado_id": int(livro_emprestado_id),
                "usuario_emprestado_id": int(usuario_emprestado_id)

            })


@app.route('/editar_livro/<id_livro>', methods=['PUT'])
def editar_livro(id_livro):
    try:
        # busca de acordo com o id, usando o db_session
        livro_resultado = db_session.execute(select(Livro).filter_by(id=int(id_livro))).scalar()
        print(livro_resultado)
        # verifica se existe
        if not livro_resultado:
            return jsonify({
                "error": "Livro não encontrado"
            })
            # valida os dados recebidos
        if not request.form.get('form_titulo'):
            return jsonify({
                "error": "Preencher campo"})
        elif not request.form.get('form_autor'):
            return jsonify({
                "error": "Preencher campo"})
        elif not request.form.get('form_ISBN'):
            return jsonify({
                "error": "Preencher campo"})
        elif not request.form.get('form_resumo'):
            return jsonify({
                "error": "Preencher campo"})
        else:
            # atualiza os dados
            livro_resultado.titulo = request.form.get('form_titulo')
            livro_resultado.autor = request.form.get('form_autor')
            livro_resultado.isbn = request.form.get('form_ISBN')
            livro_resultado.resumo = request.form.get('form_resumo')
            # salva os dados alterados
            livro_resultado.save()

            return jsonify({
                "sucess": "Livro atualizado com sucesso",
                'titulo': livro_resultado.titulo,
                'autor': livro_resultado.autor,
                'ISBN': livro_resultado.ISBN,
                'resumo': livro_resultado.resumo,

            })
    except ValueError:
        return jsonify({
            'error': 'Valor inserido invalido'
        })


@app.route('/editar_usuario/<id_usuario>', methods=['PUT'])
def editar_usuario(id_usuario):
    try:
        # busca de acordo com o id, usando o db_session
        usuario_resultado = db_session.execute(select(Usuarios).filter_by(id=int(id_usuario))).scalar()
        print(usuario_resultado)
        # verifica se existe
        if not usuario_resultado:
            return jsonify({
                "error": "Livro não encontrado"
            })

        # valida os dados recebidos
        if not request.form.get('form_nome'):
            return jsonify({
                "error": "Preencher campo"})
        elif not request.form.get('form_cpf'):
            return jsonify({
                "error": "Preencher campo"})
        elif not request.form.get('form_endereco'):
            return jsonify({
                "error": "Preencher campo"})
        else:
            # atualiza os dados
            usuario_resultado.nome = request.form.get('form_nome')
            usuario_resultado.cpf = request.form.get('form_cpf')
            usuario_resultado.endereco = request.form.get('form_endereco')

            # salva os dados alterados

            return jsonify({
                "sucess": "Usuario atualizado com sucesso",
                'nome': usuario_resultado.nome,
                'cpf': usuario_resultado.cpf,
                'endereco': usuario_resultado.endereco,

            })
    except ValueError:
        return jsonify({
            'error': 'Valor inserido invalido'
        })


@app.route('/editar_emprestimo/<id_emprestimo>', methods=['PUT'])
def editar_emprestimo(id_emprestimo):
    try:
        # busca de acordo com o id, usando o db_session
        emprestimo_resultado = db_session.execute(select(Emprestimos).filter_by(id=int(id_emprestimo))).scalar()
        print(emprestimo_resultado)
        # verifica se existe
        if not emprestimo_resultado:
            return jsonify({
                "error": "Emprestimo não encontrado"
            })

        # valida os dados recebidos
        if not request.form.get('form_data_de_emprestimo'):
            return jsonify({
                "error": "Preencher campo"})
        elif not request.form.get('form_data_de_devolucao'):
            return jsonify({
                "error": "Preencher campo"})
        elif not request.form.get('form_livro_emprestado_id'):
            return jsonify({
                "error": "Preencher campo"})
        elif not request.form.get('form_usuario_emprestado_id'):
            return jsonify({
                "error": "Preencher campo"
            })

        else:
            # atualiza os dados
            emprestimo_resultado.data_de_emprestimo = request.form.get('form_data_de_emprestimo')
            emprestimo_resultado.data_de_devolucao = request.form.get('form_data_de_devolucao')
            emprestimo_resultado.livro_emprestado_id = request.form.get('form_livro_emprestado_id')
            emprestimo_resultado.usuario_emprestado_id = request.form.get('form_usuario_emprestado_id')

            # salva os dados alterados
            emprestimo_resultado.save()

            return jsonify({
                "sucess": "Emprestimo atualizado com sucesso",
                'data de emprestimo': emprestimo_resultado.data_de_emprestimo,
                'data de devolução': emprestimo_resultado.data_de_devolucao,
                'livro emprestado id': emprestimo_resultado.livro_emprestado_id,
                'usuario emprestado': emprestimo_resultado.usuario_emprestado_id,

            })
    except ValueError:
        return jsonify({
            'error': 'Valor inserido invalido'
        })


@app.route('/get_usuario/<id_usuario>', methods=['GET'])
def get_usuario(id_usuario):
    try:
        usuario = db_session.execute(select(Usuarios).filter_by(id=int(id_usuario))).scalar()

        if not usuario:
            return jsonify({
                "erro": 'usuário não encontrado'
            })

        return jsonify({
            "success": "Usuario encontrado com sucesso",
            'id': usuario.id,
            'nome': usuario.nome,
            'cpf': usuario.cpf,
            'endereco': usuario.endereco,
        })
    except ValueError:
        return jsonify({
            'error': 'Valor inserido invalido'
        })


@app.route('/get_livro/<id_livro>', methods=['GET'])
def get_livro(id_livro):
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
    usuario_resultado = db_session.execute(select(Usuarios).filter_by(id=id_usuario)).scalar()

    if not usuario_resultado:
        return jsonify({'erro': "Usuario não encontrado"})
    usuario_resultado.delete_usuario()
    return jsonify({'success': "Usuario deletado com sucesso"})


@app.route('/deletar_livro/<id_livro>', methods=['DELETE'])
def deletar_livro(id_livro):
    livro_resultado = db_session.execute(select(Livro).filter_by(id=int(id_livro))).scalar()

    if not livro_resultado:
        return jsonify({'error': 'Livro não encontrado'})
    livro_resultado.delete_livro()
    return jsonify({'success': "Livro deletado com sucesso"})


if __name__ == '__main__':
    app.run(debug=True)
