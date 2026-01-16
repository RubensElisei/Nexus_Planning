from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from main import Gerenciador, Tarefa, TarefaNaoEncontrada
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

meu_gerenciador = Gerenciador()
meu_gerenciador.carregar_dados()


class TarefaRequest(BaseModel):
    nome: str
    descricao: str
    data_entrega: str
    hora_inicio: str = "00:00"
    hora_fim: str = "00:00"
    recorrente: bool = False
    dias_semana: List[int] = []


@app.get("/tarefas")
def list_tasks():
    return meu_gerenciador.lista_tarefas


@app.post("/tarefas")
def create_task(dados: TarefaRequest):
    nova = Tarefa(**dados.dict())
    meu_gerenciador.acionar(nova)
    return nova


@app.delete("/tarefas/{id_alvo}")
def delete_task(id_alvo: int):
    try:
        meu_gerenciador.remover_tarefa(id_alvo)
        return {"status": "removida"}
    except TarefaNaoEncontrada:
        raise HTTPException(status_code=404, detail="Tarefa não existe")


@app.patch("/tarefas/{id_alvo}/status")
def update_task_status(id_alvo: int, novo_status: str):
    try:
        tarefa_atualizada = meu_gerenciador.atualizar_status(id_alvo, novo_status)
        return tarefa_atualizada
    except TarefaNaoEncontrada:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")


@app.post("/tarefas/{id_alvo}/timer")
def control_timer(id_alvo: int, acao: str):

    try:
        meu_gerenciador.gerenciar_timer(id_alv=id_alvo, acao=acao)
        return {"status": f"Timer {acao} executado", "id": id_alvo}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/tarefas/{id_alvo}")
def edit_task(id_alvo: int, dados: TarefaRequest):
    try:
        for t in meu_gerenciador.lista_tarefas:
            if t.id == id_alvo:
                t.nome = dados.nome
                t.descricao = dados.descricao
                t.data_entrega = dados.data_entrega
                meu_gerenciador.salvar_dados()
                return t
        raise TarefaNaoEncontrada()
    except TarefaNaoEncontrada:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")


@app.post("/tarefas/{id_alvo}/tempo_manual")
def add_manual_time(id_alvo: int, minutos: float):
    try:
        tarefa = meu_gerenciador.adicionar_tempo_manual(id_alvo, minutos)
        return tarefa
    except TarefaNaoEncontrada:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")


@app.get("/calendario")
def get_calendar_events():
    eventos = []
    hoje = datetime.now()

    for t in meu_gerenciador.lista_tarefas:
        if not t.recorrente:
            try:
                data_iso = datetime.strptime(t.data_entrega, "%d/%m/%Y").strftime("%Y-%m-%d")

                eventos.append({
                    "id": str(t.id),
                    "title": t.nome,
                    "start": f"{data_iso}T{t.hora_inicio}:00",
                    "end": f"{data_iso}T{t.hora_fim}:00",
                    "color": "#3b82f6" if t.status != "Completed" else "#10b981",
                    "extendedProps": {"descricao": t.descricao}
                })
            except Exception:
                pass

        else:
            for i in range(180):
                dia_futuro = hoje + timedelta(days=i)
                if dia_futuro.weekday() in t.dias_semana:
                    data_str = dia_futuro.strftime("%d/%m/%Y")
                    data_iso = dia_futuro.strftime("%Y-%m-%d")
                    esta_concluido = data_str in t.conclusoes

                    eventos.append({
                        "id": f"{t.id}-{data_str}",
                        "title": f"{t.nome}",
                        "start": f"{data_iso}T{t.hora_inicio}:00",
                        "end": f"{data_iso}T{t.hora_fim}:00",
                        "color": "#10b981" if esta_concluido else "#6366f1"
                    })
    return eventos
