import json
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class TarefaNaoEncontrada(Exception):
    """Exceção levantada quando um ID de tarefa não existe."""
    pass


class Gerenciador:
    def __init__(self):
        self.lista_tarefas = []

    def acionar(self, tarefa):
        tarefa.id = len(self.lista_tarefas) + 1
        self.lista_tarefas.append(tarefa)
        self.salvar_dados()

    def salvar_dados(self):
        with open('nexus_data.json', 'w', encoding='utf-8') as arquivo:
            dados_para_salvar = []
            for t in self.lista_tarefas:
                temp_dict = t.dict()
                temp_dict['inicio_timer'] = None
                dados_para_salvar.append(temp_dict)

            json.dump(dados_para_salvar, arquivo, indent=4, ensure_ascii=False)

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
                raise TarefaNaoEncontrada()
            for i, tarefa in enumerate(self.lista_tarefas, start=1):
                tarefa.id = i
            self.salvar_dados()
            return True
        except ValueError:
            raise ValueError("ID inválido")

    def atualizar_status(self, id_alv, novo_status):
        id_alv = int(id_alv)
        for tarefa in self.lista_tarefas:
            if tarefa.id == id_alv:
                tarefa.status = novo_status
                if novo_status == "Completed":
                    tarefa.data_conclusao = datetime.now().strftime("%d/%m/%Y %H:%M")
                    hoje = datetime.now().strftime("%d/%m/%Y")
                    if hoje not in tarefa.conclusoes:
                        tarefa.conclusoes.append(hoje)

                self.salvar_dados()
                return tarefa
        raise TarefaNaoEncontrada()

    def gerenciar_timer(self, id_alv, acao):
        try:
            id_alv = int(id_alv)
            for t in self.lista_tarefas:
                if t.id == id_alv:
                    if acao == "play":
                        t.inicio_timer = datetime.now()
                    elif acao == "stop":
                        if t.inicio_timer is not None:
                            tempo_passado = datetime.now() - t.inicio_timer
                            minutos = tempo_passado.total_seconds() / 60
                            t.tempo_dedicado += round(minutos, 2)
                            t.inicio_timer = None
                            self.salvar_dados()
                    return t
            raise TarefaNaoEncontrada()
        except ValueError:
            raise ValueError("ID inválido")

    def adicionar_tempo_manual(self, id_alv, minutos):
        try:
            id_alv = int(id_alv)
            for t in self.lista_tarefas:
                if t.id == id_alv:
                    t.tempo_dedicado += float(minutos)
                    self.salvar_dados()
                    return t
            raise TarefaNaoEncontrada()
        except ValueError:
            raise ValueError("Valores inválidos")

    def exibir_dashboard(self):
        if not self.lista_tarefas:
            print("\n[!] Adicione tarefas primeiro para gerar o dashboard.")
            return

        total_minutos = sum(t.tempo_dedicado for t in self.lista_tarefas)
        concluidas = sum(1 for t in self.lista_tarefas if t.status == "Completed")
        tarefa_foco = max(self.lista_tarefas, key=lambda t: t.tempo_dedicado)

        print("\n" + "═"*35)
        print("📊 NEXUS DASHBOARD 📊")
        print("═"*35)
        print(f"⏱️  Tempo Total Investido: {total_minutos:.2f} min")
        print(f"✅ Tarefas Concluídas:    {concluidas}/{len(self.lista_tarefas)}")

        if total_minutos > 0:
            print(f"🔥 Maior Foco:           {tarefa_foco.nome} ({tarefa_foco.tempo_dedicado:.2f} min)")
        progresso = (concluidas / len(self.lista_tarefas)) * 100
        print(f"📈 Progresso Geral:       {progresso:.1f}%")
        print("═"*35)


class Tarefa(BaseModel):
    id: Optional[int] = None
    nome: str
    descricao: str
    data_entrega: str
    status: str = "Pending"
    tempo_dedicado: float = 0.0
    inicio_timer: Optional[datetime] = None
    data_inicio: Optional[str] = None
    data_conclusao: Optional[str] = None

    recorrente: bool = False
    dias_semana: List[int] = []
    conclusoes: List[str] = []
    hora_inicio: str = "00:00"
    hora_fim: str = "00:00"

    class Config:
        from_attributes = True


def menu():
    meu_gerenciador = Gerenciador()
    meu_gerenciador.carregar_dados()

    while True:
        print("1. Adicionar Tarefa")
        print("2. Listar Tarefas")
        print("3. Remover Tarefa")
        print("4. Atualizar Status")
        print("5. Gestão de Tempo (Timer/Manual)")
        print("6. Dashboard de Produtividade")
        print("7. Sair")

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
                    print(f" ID: {tarefas.id} | Nome: {tarefas.nome} | Descrição: {tarefas.descricao} | Data de Entrega: {tarefas.data_entrega} |"
                          f"Tempo: {tarefas.tempo_dedicado:.2f} min | Status: {tarefas.status}")

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
            id_alv = input("ID da tarefa: ")
            print("1. Iniciar Timer (Play) | 2. Parar Timer (Stop) | 3. Adicionar Manual")
            sub_op = input("Escolha: ")

            if sub_op == '1':
                meu_gerenciador.gerenciar_timer(id_alv, "play")
            elif sub_op == '2':
                meu_gerenciador.gerenciar_timer(id_alv, "stop")
            elif sub_op == '3':
                minutos = input("Quantos minutos adicionar? ")
                meu_gerenciador.adicionar_tempo_manual(id_alv, minutos)

        elif opcao == '6':
            meu_gerenciador.exibir_dashboard()

        elif opcao == '7':
            print("Saindo...")
            break

        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    menu()
