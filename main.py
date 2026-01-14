import json
from datetime import datetime


class Gerenciador:
    def __init__(self):
        self.lista_tarefas = []

    def acionar(self, tarefa):
        tarefa.id = len(self.lista_tarefas) + 1
        self.lista_tarefas.append(tarefa)
        self.salvar_dados()

    def salvar_dados(self):
        with open('nexus_data.json', 'w') as arquivo:
            dados_para_salvar = [t.__dict__ for t in self.lista_tarefas]
            json.dump(dados_para_salvar, arquivo, indent=4)
            print("Dados salvos com sucesso!")

    def carregar_dados(self):
        try:
            with open('nexus_data.json', 'r') as arquivo:
                conteudo = arquivo.read()
                if not conteudo:
                    self.lista_tarefas = []
                    return
                arquivo.seek(0)
                dados_carregados = json.loads(conteudo)
                self.lista_tarefas = [Tarefa(**tarefa) for tarefa in dados_carregados]
            print("Dados carregados com sucesso!")

        except FileNotFoundError:
            print("Nenhum arquivo de dados encontrado. Iniciando novo...")
            self.lista_tarefas = []
        except json.JSONDecodeError:
            print("Erro: O arquivo de dados está corrompido ou vazio. Iniciando lista limpa.")
            self.lista_tarefas = []

    def remover_tarefa(self, id_alv):
        try:
            id_alv = int(id_alv)
            tamanho_antes = len(self.lista_tarefas)
            self.lista_tarefas = [t for t in self.lista_tarefas if t.id != id_alv]
            if len(self.lista_tarefas) == tamanho_antes:
                print(f"[!] Erro: O ID {id_alv} não foi encontrado.")
            else:
                for i, tarefa in enumerate(self.lista_tarefas, start=1):
                    tarefa.id = i
            self.salvar_dados()
            print(f"Tarefa {id_alv} removida com sucesso!")
        except ValueError:
            print("[!] Erro: Por favor, digite um número válido para o ID.")

    def atualizar_status(self, id_alv, novo_status):
        try:
            id_alv = int(id_alv)
            encontrado = False
            for tarefa in self.lista_tarefas:
                if tarefa.id == id_alv:
                    tarefa.status = novo_status
                    if novo_status == "Completed":
                        tarefa.data_conclusao = datetime.now().strftime("%d/%m/%Y %H:%M")
                    self.salvar_dados()
                    print("Status da tarefa atualizado com sucesso!")
                    encontrado = True
                    break
            if not encontrado:
                print("Tarefa não encontrada.")
        except ValueError:
            print("[!] Erro: Digite um número de ID válido.")


class Tarefa:
    def __init__(self, nome, descricao, data_entrega, status='Pending',
                 id=None, data_inicio=None, data_conclusao=None, tempo_dedicado=0):
        self.id = id
        self.nome = nome
        self.descricao = descricao
        self.data_entrega = data_entrega
        self.status = status
        self.data_inicio = data_inicio if data_inicio else datetime.now().strftime("%d/%m/%Y %H:%M")
        self.data_conclusao = data_conclusao
        self.tempo_dedicado = tempo_dedicado


def menu():
    meu_gerenciador = Gerenciador()
    meu_gerenciador.carregar_dados()

    while True:
        print("1. Adicionar Tarefa")
        print("2. Listar Tarefas")
        print("3. Remover Tarefa")
        print("4. Atualizar Status")
        print("5. Sair")

        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            nome = input("Nome da tarefa: ")
            descricao = input("Descrição da tarefa: ")
            data_entrega = input("Data de entrega (DD/MM/AAAA): ")
            nova_tarefa = Tarefa(nome, descricao, data_entrega)
            meu_gerenciador.acionar(nova_tarefa)
            print("Tarefa adicionada com sucesso!")

        elif opcao == '2':
            if not meu_gerenciador.lista_tarefas:
                print("\n[!] Nenhuma tarefa adicionada até o momento.")
            else:
                print("\n--- SUAS TAREFAS ---")
                for tarefas in meu_gerenciador.lista_tarefas:
                    print(f" ID: {tarefas.id} | Nome: {tarefas.nome} | Descrição: {tarefas.descricao} | "
                          f"Data de Entrega: {tarefas.data_entrega} | Status: {tarefas.status}")

        elif opcao == '3':
            id_alv = input("Digite o ID da tarefa que deseja remover: ")
            meu_gerenciador.remover_tarefa(id_alv)

        elif opcao == '4':
            id_alv = (input("Digite o ID da tarefa: "))
            print("Escolha o novo status: 1. Pending | 2. In Progress | 3. Completed")
            st = input("Opção: ")

            status_map = {"1": "Pending", "2": "In Progress", "3": "Completed"}
            novo_st = status_map.get(st, "Pending")

            meu_gerenciador.atualizar_status(id_alv, novo_st)

        elif opcao == '5':
            print("Saindo...")
            break

        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu()
