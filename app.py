from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from sqlalchemy import select
from flask_pydantic_spec import FlaskPydanticSpec
from datetime import datetime
from dateutil.relativedelta import relativedelta
from models import *
app = Flask(__name__)
@app.route('/')
def pagina_inicial():
    return 'Pagina inicial (API BIBLIOTECA)'

@app.route('/livro', methods=['GET'])
def livro():
    sql_livro = select(Livro)
    resultado_livro= db_session.execute(sql_livro).scalars()
    lista_livro= []
    for n in resultado_livro:
        lista_livro.append(n.serialize_livro())
        print(lista_livro[-1])
    return jsonify({
        'lista_livro': lista_livro
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
            return jsonify({"error":"Preencher todos os campos"} )
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
            form_usuario_emprestado_id = request.form['form_usuario_emprestado_id']
            form_novo_emprestimo = Emprestimos(data_de_emprestimo=data_de_emprestimo,
                                    data_de_devolucao=data_de_devolucao,
                                    livro_emprestado_id=int(livro_emprestado_id),
                                    usuario_emprestado_id=int(form_usuario_emprestado_id)

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
                "livro_emprestado_id": livro_emprestado_id,
                "usuario_emprestado_id": form_usuario_emprestado_id ,


            })




@app.route('/editar_livro/<int:id_livro>', methods=['POST', 'GET'])
def editar_livro(id_livro):
    # busca de acordo com o id, usando o db_session
    livro_resultado = db_session.execute(select(Livro).filter_by(id=int(id_livro))).scalar()
    print(livro_resultado)
    # verifica se existe
    if not livro_resultado:
        return jsonify({
            "error" ,"Livro não encontrado"
        })

    if request.method == 'POST':
        # valida os dados recebidos
        if not request.form.get('form_titulo'):
            return jsonify({
                "error": "Preencher campo" })
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
            try:
                # atualiza os dados
                livro_resultado.titulo = request.form.get('form_titulo')
                livro_resultado.autor = request.form.get('form_autor')
                livro_resultado.isbn = request.form.get('form_ISBN')
                livro_resultado.resumo = request.form.get('form_resumo')
                # salva os dados alterados
                livro_resultado.save()

                return redirect(url_for('livro'))
            except Exception:
                flash(f"Erro {Exception}", "error")
    return jsonify({
        "sucess": "Livro atualizado com sucesso",
        'titulo': livro_resultado.titulo,
        'autor': livro_resultado.autor,
        'ISBN': livro_resultado.ISBN,
        'resumo': livro_resultado.resumo,

    })


@app.route('/editar_usuario/<int:id_usuario>', methods=['POST', 'GET'])
def editar_usuario(id_usuario):
    # busca de acordo com o id, usando o db_session
    usuario_resultado = db_session.execute(select(Usuarios).filter_by(id=int(id_usuario))).scalar()
    print(usuario_resultado)
    # verifica se existe
    if not usuario_resultado:
        return jsonify({
            "error", "Livro não encontrado"
        })

    if request.method == 'POST':
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
            try:
                # atualiza os dados
                usuario_resultado.nome = request.form.get('form_nome')
                usuario_resultado.cpf = request.form.get('form_cpf')
                usuario_resultado.enderco = request.form.get('form_endereco')

                # salva os dados alterados
                usuario_resultado.save()

                return redirect(url_for('usuario'))
            except Exception:
                flash(f"Erro {Exception}", "error")
    return jsonify({
        "sucess": "Usuario atualizado com sucesso",
        'nome': usuario_resultado.nome,
        'cpf': usuario_resultado.cpf,
        'endereco': usuario_resultado.endereco,

    })


@app.route('/get_usuario/<id_usuario>', methods=['GET'])
def get_usuario(id_usuario):
    usuario = db_session.execute(select(Usuarios).filter_by(id=int(id_usuario))).scalar()


    if not usuario:
        return jsonify({
            "erro":'usuário não encontrado'
        })

    return jsonify({
        "success": "Usuario encontrado com sucesso",
        'id': usuario.id,
        'nome': usuario.nome,
        'cpf': usuario.cpf,
        'endereco': usuario.endereco,
    })


@app.route('/get_livro/<id_livro>', methods=['GET'])
def get_livro(id_livro):
    livro = db_session.execute(select(Livro).filter_by(id=int(id_livro))).scalar()

    if not livro:
        return jsonify({
            "erro":'livro não encontrado'
        })

    return jsonify({
        "sucess": "Livro buscado com sucesso",
        'id': livro.id,
        'Titulo': livro.titulo,
        'Autor': livro.autor,
        'resumo': livro.resumo,
        'isbn': livro.ISBN,

    })


@app.route('/get_emprestimo/<id_emprestimo>', methods=['GET'])
def get_emprestimo(id_emprestimo):
    emprestimos = db_session.execute(select(Emprestimos).filter_by(id=int(id_emprestimo))).scalar()

    return jsonify({
        "sucess": "Emprestimo buscado com sucesso",
        'id': Emprestimos.id,
        'data de emprestimo': Emprestimos.data_de_emprestimo,
        'data de devolução': Emprestimos.data_de_devolucao,
        'Livros emprestados': Emprestimos.livro_emprestado_id,
        'Usuário emprestimo': Emprestimos.usuario_emprestado_id,
    })


if __name__ == '__main__':
    app.run(debug=True)
