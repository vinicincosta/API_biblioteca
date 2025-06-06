# importar bibliotecas
from sqlite3 import Date

from flask import Flask
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, declarative_base
from datetime import datetime

# VERCEL
from dotenv import load_dotenv
import os # criar variavel de ambiente '.env'
import configparser # criar arquivo de configuração 'config.ini'

# Configurar banco vercel
# Ler variavel de ambiente
load_dotenv()
# Carregue as configurações do banco de dados
url_ = os.environ.get('DATABASE_URL')
print(f'modo1: {url_}')

# Carregue o arquivo de configuração
config = configparser.ConfigParser()
config.read('config.ini')
#Obtenha as configurações do banco de dados
database_url = config['database']['url']
print(f'modo2:{database_url}')

engine = create_engine('sqlite:///nome.sqlite3')
# engine = create_engine(database_url)
#db_session = scoped_session(sessionmaker(bind=engine))- ANTIGO
session_local = sessionmaker(bind=engine)



Base = declarative_base()
# Base.query = db_session.query_property()

class Livro(Base):
    __tablename__ = 'LIVROS'
    id = Column(Integer, primary_key=True)

    titulo = Column(String, nullable=False)
    autor = Column(String, nullable=False)
    ISBN = Column(Integer, nullable=False)
    resumo = Column(String, nullable=False)

    def __repr__(self):
        return ('<Livro: titulo: {} autor: {} ISBN: {} resumo: {}'.
                format(self.titulo, self.autor, self.ISBN, self.resumo))


    def save(self, db_session):
        try:
            db_session.add(self)
            db_session.commit()
        except SQLAlchemyError:
            db_session.rollback() # VOLTAR PARA A INFORMAÇÃO PARA O ÚLTIMO MOMENTO QUE ESTAVA SALVA
            raise

    # função para deletar
    def delete_livro(self, db_session):
        db_session.delete(self)
        db_session.commit()

    def serialize_livro(self):
        dados_livro = {
            "id_livro": self.id,
            "titulo": self.titulo,
            "autor": self.autor,
            "ISBN": self.ISBN,
            "resumo": self.resumo,
        }
        return dados_livro



class Usuarios(Base):
    __tablename__ = 'USUARIOS'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    cpf = Column(String, nullable=False)
    endereco = Column(String, nullable=False)

    def __repr__(self):
        return ('<Usuario: nome: {} cpf: {} endereco: {}'.
                format(self.nome, self.cpf, self.endereco))

    def save(self, db_session):
        try:
            db_session.add(self)
            db_session.commit()
        except SQLAlchemyError:
            db_session.rollback()  # VOLTAR PARA A INFORMAÇÃO PARA O ÚLTIMO MOMENTO QUE ESTAVA SALVA
            raise

    def delete_usuario(self, db_session):
        db_session.delete(self)
        db_session.commit()

    def serialize_usuario(self):
        dados_usuario = {
            "id_usuario": self.id,
            "nome": self.nome,
            "cpf": self.cpf,
            "endereco": self.endereco,
        }
        return dados_usuario

# class Emprestimos(Base):
#     __tablename__ = 'EMPRESTIMOS'
#
#     id = Column(Integer, primary_key=True)
#     data_de_emprestimo = Column(String, nullable=False)
#     data_de_devolucao = Column(String, nullable=False)
#     livro_emprestado_id = Column(Integer, ForeignKey('LIVROS.id'))
#     livro_emprestado = relationship(Livro)
#     usuario_emprestado_id = Column(Integer, ForeignKey('USUARIOS.id'))
#     usuario_emprestado = relationship(Usuarios)
#
#
#     def __repr__(self):
#         return ('<Emprestimo: data_de_emprestimo: {} data_de_devolucao: {}'
#                 ' livro_emprestado_id: {} usuario_emprestado_id:'.
#                 format(self.data_de_emprestimo, self.data_de_devolucao, self.livro_emprestado_id, self.usuario_emprestado_id,))
#
#     def save(self, db_session):
#         try:
#             db_session.add(self)
#             db_session.commit()
#         except SQLAlchemyError:
#             db_session.rollback()  # VOLTAR PARA A INFORMAÇÃO PARA O ÚLTIMO MOMENTO QUE ESTAVA SALVA
#             raise
#
#     def delete_emprestimo(self, db_session):
#         db_session.delete(self)
#         db_session.commit()
#
#     def serialize_emprestimo(self):
#         dados_emprestimo = {
#             "id_emprestimo": self.id,
#             "data_de_emprestimo": self.data_de_emprestimo,
#             'data_de_devolucao': self.data_de_devolucao,
#             "livro_emprestado_id": self.livro_emprestado_id,
#             "usuario_emprestado_id": self.usuario_emprestado_id,
#         }
#         return dados_emprestimo

class Emprestimos(Base):
    __tablename__ = 'EMPRESTIMOS'

    id = Column(Integer, primary_key=True)
    data_de_emprestimo = Column(String, nullable=False)
    data_de_devolucao = Column(String, nullable=False)
    livro_emprestado_id = Column(Integer, ForeignKey('LIVROS.id'))
    livro_emprestado = relationship(Livro)
    usuario_emprestado_id = Column(Integer, ForeignKey('USUARIOS.id'))
    usuario_emprestado = relationship(Usuarios)
    status = Column(String, nullable=False)


    def __repr__(self):
        return ('<Emprestimo: data_de_emprestimo: {} data_de_devolucao: {}'
                ' livro_emprestado_id: {} usuario_emprestado_id: status: {}'.
                format(self.data_de_emprestimo, self.data_de_devolucao,
                       self.livro_emprestado_id, self.usuario_emprestado_id, self.status))

    def save(self, db_session):
        try:
            db_session.add(self)
            db_session.commit()
        except SQLAlchemyError:
            db_session.rollback()  # VOLTAR PARA A INFORMAÃ‡ÃƒO PARA O ÃšLTIMO MOMENTO QUE ESTAVA SALVA
            raise

    def delete_emprestimo(self, db_session):
        db_session.delete(self)
        db_session.commit()

    def serialize_emprestimo(self):
        dados_emprestimo = {
            "id_emprestimo": self.id,
            "data_de_emprestimo": self.data_de_emprestimo,
            'data_de_devolucao': self.data_de_devolucao,
            "livro_emprestado_id": self.livro_emprestado_id,
            "usuario_emprestado_id": self.usuario_emprestado_id,
            "status": self.status,
        }
        return dados_emprestimo

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()

#
# @app.route('/novo_usuario', methods=['POST'])
# def criar_usuario():
#     try:
#         dados_usuario = request.get_json()
#         # print(dados_usuario)
#         # print(dados_usuario["cpf"])
#         # quando clicar no botao de salva
#         if not "cpf" in dados_usuario or not "nome" in dados_usuario or not "endereco" in dados_usuario:
#             return jsonify({
#                 'error': 'Campo inexistente'
#             })
#
#         if dados_usuario["cpf"] == "" or dados_usuario["nome"] == "" or dados_usuario["endereco"] == "":
#             return jsonify({
#                 "error": "Preencher todos os campos"
#             })
#
#
#         else:
#             nome = dados_usuario['nome']
#             cpf = dados_usuario['cpf']
#             endereco = dados_usuario['endereco']
#
#             form_novo_usuario = Usuarios(nome=nome,
#                                          cpf=cpf,
#                                          endereco=endereco,
#                                          )
#
#             print(form_novo_usuario)
#             cpf_existente = db_session.execute(select(Usuarios).filter_by(cpf=int(cpf))).scalar()
#             if cpf_existente:
#                 return jsonify({'Este cpf já é existente'})
#             form_novo_usuario.save()
#             # db_session.close()
#             # return jsonify({ })
#             resultado = [{
#                 "nome": nome,
#                 "cpf": cpf,
#                 "endereco": endereco,
#             },
#                 {"success": "Usuario cadastrado com sucesso!"}
#             # dentro do url sempre chamar função
#             return jsonify(resultado)
#     except Exception as e:
#         return jsonify({"error": str(e)})