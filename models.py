# importar bibliotecas
from sqlite3 import Date

from flask import Flask
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, declarative_base
from datetime import datetime


engine = create_engine('sqlite:///nome.sqlite3')
db_session = scoped_session(sessionmaker(bind=engine))


Base = declarative_base()
Base.query = db_session.query_property()

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


    def save(self):
        db_session.add(self)
        db_session.commit()

    # função para deletar
    def delete_livro(self):
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

    def save(self):
        db_session.add(self)
        db_session.commit()

    def delete_usuario(self):
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


class Emprestimos(Base):
    __tablename__ = 'EMPRESTIMOS'

    id = Column(Integer, primary_key=True)
    data_de_emprestimo = Column(String, nullable=False)
    data_de_devolucao = Column(String, nullable=False)
    livro_emprestado_id = Column(Integer, ForeignKey('LIVROS.id'))
    livro_emprestado = relationship(Livro)
    usuario_emprestado_id = Column(Integer, ForeignKey('USUARIOS.id'))
    usuario_emprestado = relationship(Usuarios)


    def __repr__(self):
        return ('<Emprestimo: data_de_emprestimo: {} data_de_devolucao: {}'
                ' livro_emprestado_id: {} usuario_emprestado_id:'.
                format(self.data_de_emprestimo, self.data_de_devolucao, self.livro_emprestado_id, self.usuario_emprestado_id,))

    def save(self):
        db_session.add(self)
        db_session.commit()

    def delete_emprestimo(self):
        db_session.delete(self)
        db_session.commit()

    def serialize_emprestimo(self):
        dados_emprestimo = {
            "id_emprestimo": self.id,
            "data_de_emprestimo": self.data_de_emprestimo,
            'data_de_devolucao': self.data_de_devolucao,
            "livro_emprestado_id": self.livro_emprestado_id,
            "usuario_emprestado_id": self.usuario_emprestado_id,
        }
        return dados_emprestimo



def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()


