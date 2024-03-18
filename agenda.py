# main.py
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QTableWidget, QTableWidgetItem, QMessageBox
from sqlalchemy.orm import Session
from config import User, SessionLocal
from schema import UserCreate


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Gerenciamento de Usuários')
        self.setGeometry(100, 100, 600, 400)
        self.layout = QVBoxLayout()
        
        # Entrada de Nome e Email
        self.name_input = QLineEdit(placeholderText="Nome")
        self.email_input = QLineEdit(placeholderText="Email")
        
        # Botões
        self.add_button = QPushButton('Adicionar')
        self.edit_button = QPushButton('Editar')
        self.delete_button = QPushButton('Remover')
        
        # Tabela para exibir usuários
        self.users_table = QTableWidget(0, 3)
        self.users_table.setHorizontalHeaderLabels(['ID', 'Nome', 'Email'])
        
        # Layout para os botões
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        
         # Campo e botão de busca
        self.search_input = QLineEdit(self, placeholderText="Buscar por nome...")
        self.search_button = QPushButton('Buscar', self)
        self.search_button.clicked.connect(self.search_user)
        
        # Adicionando campo e botão de busca ao layout
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        self.layout.insertLayout(3, search_layout)  # Insere o layout de busca na posição desejada
        
        # Adicionando widgets ao layout principal
        self.layout.addWidget(QLabel('Nome:'))
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(QLabel('Email:'))
        self.layout.addWidget(self.email_input)
        self.layout.addLayout(button_layout)
        self.layout.addWidget(self.users_table)
        
        self.setLayout(self.layout)
        
        # Conectando sinais
        self.add_button.clicked.connect(self.add_user)
        self.edit_button.clicked.connect(self.edit_user)
        self.delete_button.clicked.connect(self.delete_user)
        
        self.load_users()
    
    def add_user(self):
        session = SessionLocal()
        try:
            user_data = UserCreate(name=self.name_input.text(), email=self.email_input.text())
            new_user = User(name=user_data.name, email=user_data.email)
            session.add(new_user)
            session.commit()
            self.load_users()
        except Exception as e:
            QMessageBox.critical(self, 'Erro', str(e))
        finally:
            session.close()
    
    def search_user(self):
        term = self.search_input.text().strip()
        session = SessionLocal()
        if term:
            # Busca usuários que contêm o termo de busca no nome
            users = session.query(User).filter(User.name.like(f"%{term}%")).all()
        else:
            # Se o termo de busca estiver vazio, busca todos os usuários
            users = session.query(User).all()
        
        # Atualiza a tabela com os usuários encontrados
        self.users_table.setRowCount(0)  # Limpa a tabela antes de adicionar novas linhas
        for user in users:
            row_position = self.users_table.rowCount()
            self.users_table.insertRow(row_position)
            self.users_table.setItem(row_position, 0, QTableWidgetItem(str(user.id)))
            self.users_table.setItem(row_position, 1, QTableWidgetItem(user.name))
            self.users_table.setItem(row_position, 2, QTableWidgetItem(user.email))
        
        session.close()


    def edit_user(self):
        selected_items = self.users_table.selectedItems()
        if selected_items:
                selected_row = selected_items[0].row()
                user_id = int(self.users_table.item(selected_row, 0).text())
                
                # Carrega o usuário do banco de dados
                session = SessionLocal()
                user = session.query(User).filter(User.id == user_id).first()
                if user:
                    # Atualiza os dados do usuário
                    try:
                        user_data = UserCreate(name=self.name_input.text(), email=self.email_input.text())
                        user.name = user_data.name
                        user.email = user_data.email
                        session.commit()
                        QMessageBox.information(self, 'Sucesso', 'Usuário atualizado com sucesso!')
                    except Exception as e:
                        session.rollback()
                        QMessageBox.critical(self, 'Erro', str(e))
                    finally:
                        session.close()
                        self.load_users()
                        self.name_input.clear()
                        self.email_input.clear()
        else:
                QMessageBox.warning(self, 'Seleção', 'Por favor, selecione um usuário para editar.')
    
    def delete_user(self):
        selected_items = self.users_table.selectedItems()
        if selected_items:
                selected_row = selected_items[0].row()
                user_id = int(self.users_table.item(selected_row, 0).text())
                
                reply = QMessageBox.question(self, 'Confirmar', 'Você tem certeza que deseja remover este usuário?',
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                
                if reply == QMessageBox.Yes:
                    session = SessionLocal()
                    user = session.query(User).filter(User.id == user_id).first()
                    if user:
                        try:
                            session.delete(user)
                            session.commit()
                            QMessageBox.information(self, 'Sucesso', 'Usuário removido com sucesso!')
                        except Exception as e:
                            session.rollback()
                            QMessageBox.critical(self, 'Erro', str(e))
                        finally:
                            session.close()
                            self.load_users()
        else:
                QMessageBox.warning(self, 'Seleção', 'Por favor, selecione um usuário para remover.')
    
    def load_users(self):
        self.users_table.setRowCount(0)
        session = SessionLocal()
        users = session.query(User).all()
        for user in users:
            row_position = self.users_table.rowCount()
            self.users_table.insertRow(row_position)
            self.users_table.setItem(row_position, 0, QTableWidgetItem(str(user.id)))
            self.users_table.setItem(row_position, 1, QTableWidgetItem(user.name))
            self.users_table.setItem(row_position, 2, QTableWidgetItem(user.email))
        session.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
