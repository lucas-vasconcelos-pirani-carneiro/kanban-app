import customtkinter as ctk
from datetime import datetime
from src.repositories.coluna_repository import ColunaRepository
from src.repositories.cartao_repository import CartaoRepository
from src.repositories.usuario_repository import UsuarioRepository
from src.services.coluna_service import ColunaService
from src.services.cartao_service import CartaoService
from src.services.usuario_service import UsuarioService

coluna_repository = ColunaRepository()
cartao_repository = CartaoRepository()
usuario_repository = UsuarioRepository()
coluna_service = ColunaService(coluna_repository)
cartao_service = CartaoService(cartao_repository, coluna_repository)
usuario_service = UsuarioService(usuario_repository)

CORES_PRIORIDADE = {
    "baixa":   "#4CAF50",
    "media":   "#FF9800",
    "alta":    "#F44336",
    "urgente": "#9C27B0",
}

LABELS_PRIORIDADE = {
    "baixa":   "Baixa",
    "media":   "Média",
    "alta":    "Alta",
    "urgente": "Urgente",
}


def populate_kanban_screen(frame_kanban: ctk.CTkFrame, show_frame) -> None:
    frame_kanban.quadro_atual = None
    frame_kanban.frame_quadros = None
    frame_kanban.show_frame = show_frame
    frame_kanban.usuario_logado = None

    frame_header = ctk.CTkFrame(frame_kanban, fg_color="transparent")
    frame_header.pack(side="top", fill="x", padx=20, pady=(20, 10))
    frame_header.grid_columnconfigure(1, weight=1)

    frame_kanban.label_titulo = ctk.CTkLabel(
        frame_header,
        text="Quadro",
        font=("Arial", 22, "bold")
    )
    frame_kanban.label_titulo.grid(row=0, column=0, sticky="w")

    ctk.CTkButton(
        frame_header,
        text="Voltar",
        font=("Arial", 13, "bold"),
        fg_color="#888888",
        hover_color="#666666",
        width=100,
        command=lambda: _voltar(frame_kanban)
    ).grid(row=0, column=1, sticky="e")

    linha = ctk.CTkFrame(frame_kanban, height=2, fg_color="#cccccc")
    linha.pack(side="top", fill="x", padx=20)

    frame_kanban.frame_colunas = ctk.CTkScrollableFrame(
        frame_kanban,
        fg_color="transparent",
        label_text="",
        orientation="horizontal"
    )
    frame_kanban.frame_colunas.pack(side="top", fill="both", expand=True, padx=10, pady=10)

    frame_rodape = ctk.CTkFrame(frame_kanban, fg_color="transparent")
    frame_rodape.pack(side="bottom", fill="x", padx=20, pady=10)

    ctk.CTkButton(
        frame_rodape,
        text="+ Adicionar Coluna",
        font=("Arial", 13, "bold"),
        command=lambda: abrir_dialog_criar_coluna(frame_kanban)
    ).pack(side="left")


def carregar_kanban(frame_kanban: ctk.CTkFrame, quadro, frame_quadros) -> None:
    frame_kanban.quadro_atual = quadro
    frame_kanban.frame_quadros = frame_quadros
    frame_kanban.usuario_logado = frame_quadros.frame_dashboard.usuario_logado
    frame_kanban.label_titulo.configure(text=quadro.nome)
    _renderizar_colunas(frame_kanban)


def _voltar(frame_kanban: ctk.CTkFrame) -> None:
    frame_kanban.show_frame(frame_kanban.frame_quadros)


def _renderizar_colunas(frame_kanban: ctk.CTkFrame) -> None:
    for widget in frame_kanban.frame_colunas.winfo_children():
        widget.destroy()

    colunas = coluna_service.listar_colunas_do_quadro(frame_kanban.quadro_atual.id_quadro)

    if not colunas:
        ctk.CTkLabel(
            frame_kanban.frame_colunas,
            text="Nenhuma coluna ainda.\nClique em '+ Adicionar Coluna' para começar.",
            font=("Arial", 14),
            text_color="#888888"
        ).pack(pady=40, padx=20)
        return

    for coluna in colunas:
        _criar_widget_coluna(frame_kanban, coluna)


def _criar_widget_coluna(frame_kanban: ctk.CTkFrame, coluna) -> None:
    cartoes = cartao_service.cartao_repo.listar_por_coluna(coluna.id_coluna)
    total = len(cartoes)
    wip_atingido = coluna.limite_col is not None and total >= coluna.limite_col

    frame_col = ctk.CTkFrame(
        frame_kanban.frame_colunas,
        fg_color="#ECECEC",
        corner_radius=10,
        width=260
    )
    frame_col.pack(side="left", fill="y", padx=8, pady=4, anchor="n")
    frame_col.pack_propagate(False)

    # Usa grid internamente para controlar expansão
    frame_col.grid_rowconfigure(0, weight=0)  # cabeçalho fixo
    frame_col.grid_rowconfigure(1, weight=1)  # cartões expandem
    frame_col.grid_rowconfigure(2, weight=0)  # botão fixo
    frame_col.grid_columnconfigure(0, weight=1)

    # Cabeçalho — linha 0
    frame_cab = ctk.CTkFrame(frame_col, fg_color="transparent")
    frame_cab.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))

    cor_indicador = "#FF5555" if wip_atingido else "#7B4DFF"
    limite_texto = f"/{coluna.limite_col}" if coluna.limite_col else ""
    ctk.CTkLabel(
        frame_cab,
        text=f"{total}{limite_texto}",
        font=("Arial", 11, "bold"),
        fg_color=cor_indicador,
        text_color="white",
        corner_radius=10,
        width=36,
        height=20
    ).pack(side="left")

    ctk.CTkLabel(
        frame_cab,
        text=coluna.nome,
        font=("Arial", 13, "bold"),
        text_color="#333333"
    ).pack(side="left", padx=(6, 0))

    ctk.CTkButton(
        frame_cab,
        text="⚙️",
        width=28, height=28,
        font=("Arial", 14),
        fg_color="transparent",
        hover_color="#DDDDDD",
        text_color="#666666",
        command=lambda c=coluna: abrir_config_coluna(c, frame_kanban)
    ).pack(side="right")

    # Área scrollável dos cartões — linha 1 (expande)
    frame_cartoes = ctk.CTkScrollableFrame(
        frame_col,
        fg_color="transparent",
        label_text=""
    )
    frame_cartoes.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)

    for cartao in cartoes:
        _criar_widget_cartao(frame_cartoes, cartao, coluna, frame_kanban)

    # Botão adicionar cartão — linha 2 (fixo na base)
    ctk.CTkButton(
        frame_col,
        text="+ Cartão",
        font=("Arial", 12),
        height=30,
        fg_color="#7B4DFF",
        hover_color="#6738E6",
        command=lambda c=coluna: abrir_dialog_criar_cartao(c, frame_kanban)
    ).grid(row=2, column=0, sticky="ew", padx=8, pady=(4, 8))

def _criar_widget_cartao(frame_cartoes, cartao, coluna, frame_kanban) -> None:
    cor = CORES_PRIORIDADE.get(cartao.prioridade, "#999999")
    label_prio = LABELS_PRIORIDADE.get(cartao.prioridade, cartao.prioridade)

    frame_cartao = ctk.CTkFrame(
        frame_cartoes,
        fg_color="white",
        corner_radius=8,
        border_width=2,
        border_color=cor
    )
    frame_cartao.pack(fill="x", pady=4, padx=2)

    # Barra de prioridade no topo
    ctk.CTkFrame(frame_cartao, fg_color=cor, height=4, corner_radius=0).pack(fill="x")

    # Linha superior: nome + botão ⚙️
    frame_topo = ctk.CTkFrame(frame_cartao, fg_color="transparent")
    frame_topo.pack(fill="x", padx=8, pady=(6, 0))

    ctk.CTkLabel(
        frame_topo,
        text=cartao.nome,
        font=("Arial", 12, "bold"),
        text_color="#222222",
        anchor="w",
        wraplength=160
    ).pack(side="left", fill="x", expand=True)

    ctk.CTkButton(
        frame_topo,
        text="⚙️",
        width=24, height=24,
        font=("Arial", 11),
        fg_color="transparent",
        hover_color="#EEEEEE",
        text_color="#666666",
        command=lambda c=cartao: abrir_detalhes_cartao(c, frame_kanban)
    ).pack(side="right")

    # Corpo do cartão
    frame_info = ctk.CTkFrame(frame_cartao, fg_color="transparent")
    frame_info.pack(fill="x", padx=8, pady=(2, 6))

    # Descrição (se houver)
    if cartao.descricao and cartao.descricao.strip():
        ctk.CTkLabel(
            frame_info,
            text=cartao.descricao,
            font=("Arial", 10),
            text_color="#555555",
            anchor="w",
            wraplength=200,
            justify="left"
        ).pack(anchor="w", pady=(0, 4))

    ctk.CTkLabel(
        frame_info,
        text=f"● {label_prio}",
        font=("Arial", 10, "bold"),
        text_color=cor
    ).pack(anchor="w")

    ctk.CTkLabel(
        frame_info,
        text=f"📅 {_data_iso_para_br(cartao.data_limite)}",
        font=("Arial", 10),
        text_color="#666666"
    ).pack(anchor="w")

    # Responsável
    try:
        responsavel = usuario_service.obter_usuario(cartao.id_user_responsavel)
        nome_responsavel = responsavel.nome
    except Exception:
        nome_responsavel = "—"

    ctk.CTkLabel(
        frame_info,
        text=f"👤 {nome_responsavel}",
        font=("Arial", 10),
        text_color="#666666"
    ).pack(anchor="w")

# Máscara de data

def _aplicar_mascara_data(entry: ctk.CTkEntry) -> None:

    def formatar(event=None):
        # Ignora teclas de navegação
        if event and event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab"):
            return

        texto = entry.get()
        digitos = ''.join(c for c in texto if c.isdigit())
        digitos = digitos[:8]

        resultado = ""
        for i, c in enumerate(digitos):
            if i == 2 or i == 4:
                resultado += "/"
            resultado += c

        entry.delete(0, "end")
        entry.insert(0, resultado)

    def validar_ao_sair(event=None):
        texto = entry.get().strip()
        if not texto:
            return
        try:
            datetime.strptime(texto, "%d/%m/%Y")
            entry.configure(border_color="#4CAF50")
        except ValueError:
            entry.configure(border_color="#FF5555")

    entry.bind("<KeyRelease>", formatar)
    entry.bind("<FocusOut>", validar_ao_sair)


def _data_br_para_iso(data_br: str) -> str:
    """Converte DD/MM/AAAA para AAAA-MM-DD para salvar no banco."""
    dt = datetime.strptime(data_br, "%d/%m/%Y")
    return dt.strftime("%Y-%m-%d")


def _data_iso_para_br(data_iso: str) -> str:
    """Converte AAAA-MM-DD para DD/MM/AAAA para exibir."""
    if not data_iso:
        return ""
    try:
        dt = datetime.strptime(data_iso, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        return data_iso

# Dialogs 

def abrir_dialog_criar_coluna(frame_kanban: ctk.CTkFrame) -> None:
    dialog = ctk.CTkToplevel()
    dialog.title("Nova Coluna")
    dialog.geometry("380x260")
    lw, lh = dialog.winfo_screenwidth(), dialog.winfo_screenheight()
    dialog.geometry(f"380x260+{int(lw/2-190)}+{int(lh/2-130)}")

    ctk.CTkLabel(dialog, text="Nova Coluna", font=("Arial", 16, "bold")).pack(pady=(20, 12))
    ctk.CTkLabel(dialog, text="Nome da coluna", font=("Arial", 13, "bold")).pack(pady=(0, 4))
    campo_nome = ctk.CTkEntry(dialog, placeholder_text="Nome da coluna", width=300)
    campo_nome.pack(pady=(0, 10))

    ctk.CTkLabel(dialog, text="Limite de Cartões (WIP) — deixe vazio para ilimitado",
                 font=("Arial", 11), text_color="#888888").pack(pady=(0, 4))
    campo_wip = ctk.CTkEntry(dialog, placeholder_text="Ex: 3", width=300)
    campo_wip.pack(pady=(0, 10))

    label_erro = ctk.CTkLabel(dialog, text="", text_color="#FF5555", font=("Arial", 11))
    label_erro.pack()

    def confirmar():
        nome = campo_nome.get().strip()
        wip_texto = campo_wip.get().strip()
        limite = None
        if wip_texto:
            if not wip_texto.isdigit():
                label_erro.configure(text="O limite deve ser um número inteiro positivo.")
                return
            limite = int(wip_texto)
        try:
            coluna_service.criar_coluna(
                id_quadro=frame_kanban.quadro_atual.id_quadro,
                nome=nome, limite_col=limite
            )
            dialog.destroy()
            _renderizar_colunas(frame_kanban)
        except ValueError as e:
            label_erro.configure(text=str(e))

    ctk.CTkButton(dialog, text="Criar", width=180, command=confirmar).pack(pady=(8, 4))
    ctk.CTkButton(dialog, text="Cancelar", width=180, fg_color="#888888",
                  hover_color="#666666", command=dialog.destroy).pack(pady=(0, 12))
    dialog.after(100, dialog.grab_set)


def abrir_dialog_criar_cartao(coluna, frame_kanban: ctk.CTkFrame) -> None:
    dialog = ctk.CTkToplevel()
    dialog.title("Novo Cartão")
    dialog.geometry("440x560")  # altura aumentada
    lw, lh = dialog.winfo_screenwidth(), dialog.winfo_screenheight()
    dialog.geometry(f"440x560+{int(lw/2-220)}+{int(lh/2-280)}")
    dialog.resizable(False, False)

    ctk.CTkLabel(dialog, text=f"Novo Cartão - {coluna.nome}",
                 font=("Arial", 16, "bold")).pack(pady=(20, 12))

    ctk.CTkLabel(dialog, text="Nome do Cartão", font=("Arial", 13, "bold")).pack(pady=(0, 4))
    campo_nome = ctk.CTkEntry(dialog, placeholder_text="Nome do cartão", width=360)
    campo_nome.pack(pady=(0, 8))

    ctk.CTkLabel(dialog, text="Descrição (Opcional)", font=("Arial", 13, "bold")).pack(pady=(0, 4))
    campo_desc = ctk.CTkTextbox(dialog, width=360, height=70)
    campo_desc.pack(pady=(0, 8))

    ctk.CTkLabel(dialog, text="Prioridade", font=("Arial", 13, "bold")).pack(pady=(0, 4))
    campo_prioridade = ctk.CTkOptionMenu(
        dialog,
        values=["baixa", "media", "alta", "urgente"],
        width=360
    )
    campo_prioridade.set("baixa")
    campo_prioridade.pack(pady=(0, 8))

    ctk.CTkLabel(dialog, text="Prazo Máximo", font=("Arial", 13, "bold")).pack(pady=(0, 4))
    campo_prazo = ctk.CTkEntry(dialog, placeholder_text="DD/MM/AAAA", width=360)
    campo_prazo.pack(pady=(0, 4))
    _aplicar_mascara_data(campo_prazo)

    label_erro = ctk.CTkLabel(dialog, text="", text_color="#FF5555", font=("Arial", 11))
    label_erro.pack(pady=(8, 0))

    def confirmar():
        nome = campo_nome.get().strip()
        desc = campo_desc.get("1.0", "end").strip()
        prioridade = campo_prioridade.get()
        prazo_br = campo_prazo.get().strip()
        usuario = frame_kanban.usuario_logado

        if not usuario:
            label_erro.configure(text="Nenhum usuário logado.")
            return

        try:
            prazo_iso = _data_br_para_iso(prazo_br)
        except ValueError:
            label_erro.configure(text="Data inválida. Use o formato DD/MM/AAAA.")
            return

        try:
            cartao_service.criar_cartao(
                id_coluna=coluna.id_coluna,
                id_user_responsavel=usuario.id_user,
                nome=nome,
                data_limite=prazo_iso,
                prioridade=prioridade,
                descricao=desc
            )
            dialog.destroy()
            _renderizar_colunas(frame_kanban)
        except ValueError as e:
            label_erro.configure(text=str(e))

    ctk.CTkButton(dialog, text="Criar Cartão", width=200, command=confirmar).pack(pady=(12, 4))
    ctk.CTkButton(dialog, text="Cancelar", width=200, fg_color="#888888",
                  hover_color="#666666", command=dialog.destroy).pack(pady=(0, 15))
    dialog.after(100, dialog.grab_set)

    def confirmar():
        nome = campo_nome.get().strip()
        desc = campo_desc.get("1.0", "end").strip()
        prioridade = campo_prioridade.get()
        prazo_br = campo_prazo.get().strip()
        usuario = frame_kanban.usuario_logado

        if not usuario:
            label_erro.configure(text="Nenhum usuário logado.")
            return

        try:
            prazo_iso = _data_br_para_iso(prazo_br)
        except ValueError:
            label_erro.configure(text="Data inválida. Use o formato DD/MM/AAAA.")
            return

        try:
            cartao_service.criar_cartao(
                id_coluna=coluna.id_coluna,
                id_user_responsavel=usuario.id_user,
                nome=nome,
                data_limite=prazo_iso,
                prioridade=prioridade,
                descricao=desc
            )
            dialog.destroy()
            _renderizar_colunas(frame_kanban)
        except ValueError as e:
            label_erro.configure(text=str(e))


def abrir_detalhes_cartao(cartao, frame_kanban: ctk.CTkFrame) -> None:
    dialog = ctk.CTkToplevel()
    dialog.title("Detalhes do Cartão")
    dialog.geometry("440x520")
    lw, lh = dialog.winfo_screenwidth(), dialog.winfo_screenheight()
    dialog.geometry(f"440x520+{int(lw/2-220)}+{int(lh/2-260)}")

    ctk.CTkLabel(dialog, text="Detalhes do Cartão", font=("Arial", 16, "bold")).pack(pady=(20, 12))

    ctk.CTkLabel(dialog, text="Nome do Cartão", font=("Arial", 13, "bold")).pack(pady=(0, 4))
    campo_nome = ctk.CTkEntry(dialog, placeholder_text="Nome", width=360)
    campo_nome.insert(0, cartao.nome)
    campo_nome.pack(pady=(0, 8))

    ctk.CTkLabel(dialog, text="Descrição", font=("Arial", 13, "bold")).pack(pady=(0, 4))
    campo_desc = ctk.CTkTextbox(dialog, width=360, height=70)
    campo_desc.insert("1.0", cartao.descricao or "")
    campo_desc.pack(pady=(0, 8))

    ctk.CTkLabel(dialog, text="Prioridade", font=("Arial", 13, "bold")).pack(pady=(0, 4))
    campo_prioridade = ctk.CTkOptionMenu(
        dialog,
        values=["baixa", "media", "alta", "urgente"],
        width=360
    )
    campo_prioridade.set(cartao.prioridade or "baixa")
    campo_prioridade.pack(pady=(0, 8))

    ctk.CTkLabel(dialog, text="Prazo Máximo", font=("Arial", 13, "bold")).pack(pady=(0, 4))
    campo_prazo = ctk.CTkEntry(dialog, placeholder_text="AAAA-MM-DD", width=360)
    # preenche o campo já no formato BR
    campo_prazo.insert(0, _data_iso_para_br(cartao.data_limite or ""))
    campo_prazo.pack(pady=(0, 4))
    _aplicar_mascara_data(campo_prazo)

    label_feedback = ctk.CTkLabel(dialog, text="", font=("Arial", 11))
    label_feedback.pack(pady=(4, 0))

    def salvar():
        novo_nome = campo_nome.get().strip()
        nova_desc = campo_desc.get("1.0", "end").strip()
        nova_prio = campo_prioridade.get()
        prazo_br = campo_prazo.get().strip()

        try:
            prazo_iso = _data_br_para_iso(prazo_br)
        except ValueError:
            label_feedback.configure(text="Data inválida. Use o formato DD/MM/AAAA.", text_color="#FF5555")
            return

        cartao.nome = novo_nome
        cartao.descricao = nova_desc
        cartao.prioridade = nova_prio
        cartao.data_limite = prazo_iso

        try:
            cartao_service.cartao_repo.atualizar(cartao)
            label_feedback.configure(text="Cartão atualizado!", text_color="#4CAF50")
            dialog.after(1500, lambda: [dialog.destroy(), _renderizar_colunas(frame_kanban)])
        except Exception as e:
            label_feedback.configure(text=str(e), text_color="#FF5555")

    def excluir():
        cartao_service.excluir_cartao(cartao.id_cartao)
        dialog.destroy()
        _renderizar_colunas(frame_kanban)

    ctk.CTkButton(dialog, text="Salvar Alterações", width=200, command=salvar).pack(pady=(4, 4))
    ctk.CTkButton(dialog, text="Excluir Cartão", width=200,
                  fg_color="#FF5555", hover_color="#CC3333", command=excluir).pack(pady=(0, 4))
    ctk.CTkButton(dialog, text="Fechar", width=200, fg_color="#888888",
                  hover_color="#666666", command=dialog.destroy).pack(pady=(0, 15))
    dialog.after(100, dialog.grab_set)


def abrir_config_coluna(coluna, frame_kanban: ctk.CTkFrame) -> None:
    dialog = ctk.CTkToplevel()
    dialog.title("Configurações da Coluna")
    dialog.geometry("380x300")
    lw, lh = dialog.winfo_screenwidth(), dialog.winfo_screenheight()
    dialog.geometry(f"380x300+{int(lw/2-190)}+{int(lh/2-150)}")

    ctk.CTkLabel(dialog, text="Configurações da Coluna", font=("Arial", 16, "bold")).pack(pady=(20, 12))
    ctk.CTkLabel(dialog, text="Nome da coluna", font=("Arial", 13, "bold")).pack(pady=(0, 4))
    campo_nome = ctk.CTkEntry(dialog, placeholder_text="Nome", width=300)
    campo_nome.insert(0, coluna.nome)
    campo_nome.pack(pady=(0, 8))

    ctk.CTkLabel(dialog, text="Limite de Cartões (WIP) — deixe vazio para ilimitado",
                 font=("Arial", 11), text_color="#888888").pack(pady=(0, 4))
    campo_wip = ctk.CTkEntry(dialog, placeholder_text="Ex: 3", width=300)
    if coluna.limite_col:
        campo_wip.insert(0, str(coluna.limite_col))
    campo_wip.pack(pady=(0, 8))

    label_feedback = ctk.CTkLabel(dialog, text="", font=("Arial", 11))
    label_feedback.pack()

    def salvar():
        novo_nome = campo_nome.get().strip()
        wip_texto = campo_wip.get().strip()
        novo_limite = None
        if wip_texto:
            if not wip_texto.isdigit():
                label_feedback.configure(text="O limite deve ser um número inteiro.", text_color="#FF5555")
                return
            novo_limite = int(wip_texto)
        try:
            coluna_service.atualizar_coluna(coluna.id_coluna, novo_nome, novo_limite)
            label_feedback.configure(text="Coluna atualizada!", text_color="#4CAF50")
            dialog.after(1500, lambda: [dialog.destroy(), _renderizar_colunas(frame_kanban)])
        except ValueError as e:
            label_feedback.configure(text=str(e), text_color="#FF5555")

    def excluir():
        try:
            coluna_service.excluir_coluna(coluna.id_coluna)
            dialog.destroy()
            _renderizar_colunas(frame_kanban)
        except ValueError as e:
            label_feedback.configure(text=str(e), text_color="#FF5555")

    ctk.CTkButton(dialog, text="Salvar Alterações", width=200, command=salvar).pack(pady=(4, 4))
    ctk.CTkButton(dialog, text="Excluir Coluna", width=200,
                  fg_color="#FF5555", hover_color="#CC3333", command=excluir).pack(pady=(0, 4))
    ctk.CTkButton(dialog, text="Cancelar", width=200, fg_color="#888888",
                  hover_color="#666666", command=dialog.destroy).pack(pady=(0, 15))
    dialog.after(100, dialog.grab_set)
