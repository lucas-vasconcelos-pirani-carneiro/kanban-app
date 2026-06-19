import customtkinter as ctk
from datetime import datetime
from src.repositories.coluna_repository import ColunaRepository
from src.repositories.cartao_repository import CartaoRepository
from src.repositories.usuario_repository import UsuarioRepository
from src.repositories.raia_repository import RaiaRepository
from src.services.coluna_service import ColunaService
from src.services.cartao_service import CartaoService
from src.services.usuario_service import UsuarioService
from src.services.raia_service import RaiaService

coluna_repository = ColunaRepository()
cartao_repository = CartaoRepository()
usuario_repository = UsuarioRepository()
raia_repository = RaiaRepository()
coluna_service = ColunaService(coluna_repository)
cartao_service = CartaoService(cartao_repository, coluna_repository)
usuario_service = UsuarioService(usuario_repository)
raia_service = RaiaService(raia_repository)

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

COR_RAIA_HEADER = "#7B4DFF"
COR_RAIA_HEADER_SEMRAIA = "#AAAAAA"


# ── SETUP INICIAL ──────────────────────────────────────────────────────────────

def populate_kanban_screen(frame_kanban: ctk.CTkFrame, show_frame) -> None:
    frame_kanban.quadro_atual = None
    frame_kanban.frame_quadros = None
    frame_kanban.show_frame = show_frame
    frame_kanban.usuario_logado = None
    frame_kanban.ordem_colunas = None

    frame_header = ctk.CTkFrame(frame_kanban, fg_color="transparent")
    frame_header.pack(side="top", fill="x", padx=20, pady=(20, 10))
    frame_header.grid_columnconfigure(1, weight=1)

    frame_kanban.label_titulo = ctk.CTkLabel(
        frame_header, text="Quadro", font=("Arial", 22, "bold")
    )
    frame_kanban.label_titulo.grid(row=0, column=0, sticky="w")

    ctk.CTkButton(
        frame_header,
        text="" \
        "Voltar",
        font=("Arial", 13, "bold"),
        fg_color="#888888",
        hover_color="#666666",
        width=100,
        command=lambda: _voltar(frame_kanban)
    ).grid(row=0, column=1, sticky="e")

    linha = ctk.CTkFrame(frame_kanban, height=2, fg_color="#cccccc")
    linha.pack(side="top", fill="x", padx=20)

    # Frame scrollável principal — scroll horizontal E vertical
    frame_kanban.frame_scroll = ctk.CTkScrollableFrame(
        frame_kanban,
        fg_color="transparent",
        label_text="",
        orientation="horizontal"
    )
    frame_kanban.frame_scroll.pack(side="top", fill="both", expand=True, padx=10, pady=10)

    frame_rodape = ctk.CTkFrame(frame_kanban, fg_color="transparent")
    frame_rodape.pack(side="bottom", fill="x", padx=20, pady=10)

    ctk.CTkButton(
        frame_rodape,
        text="+ Adicionar Coluna",
        font=("Arial", 13, "bold"),
        command=lambda: abrir_dialog_criar_coluna(frame_kanban)
    ).pack(side="left")

    ctk.CTkButton(
        frame_rodape,
        text="+ Adicionar Raia",
        font=("Arial", 13, "bold"),
        fg_color="#5C8A3C",
        hover_color="#4A7030",
        command=lambda: abrir_dialog_criar_raia(frame_kanban)
    ).pack(side="left", padx=(10, 0))


def carregar_kanban(frame_kanban: ctk.CTkFrame, quadro, frame_quadros) -> None:
    frame_kanban.quadro_atual = quadro
    frame_kanban.frame_quadros = frame_quadros
    frame_kanban.usuario_logado = frame_quadros.frame_dashboard.usuario_logado
    frame_kanban.label_titulo.configure(text=quadro.nome)
    frame_kanban.ordem_colunas = None
    _renderizar_tudo(frame_kanban)


def _voltar(frame_kanban: ctk.CTkFrame) -> None:
    frame_kanban.show_frame(frame_kanban.frame_quadros)


# ── RENDERIZAÇÃO PRINCIPAL ─────────────────────────────────────────────────────

def _renderizar_tudo(frame_kanban: ctk.CTkFrame) -> None:
    """Reconstrói toda a grade do kanban: cabeçalho de colunas + raias."""
    for widget in frame_kanban.frame_scroll.winfo_children():
        widget.destroy()

    colunas = _get_colunas_ordenadas(frame_kanban)
    raias = raia_service.listar_raias_do_quadro(frame_kanban.quadro_atual.id_quadro)

    if not colunas:
        ctk.CTkLabel(
            frame_kanban.frame_scroll,
            text="Nenhuma coluna ainda.\nClique em '+ Adicionar Coluna' para começar.",
            font=("Arial", 14),
            text_color="#888888"
        ).pack(pady=40, padx=20)
        return

    # Frame principal da grade
    frame_grade = ctk.CTkFrame(frame_kanban.frame_scroll, fg_color="transparent")
    frame_grade.pack(side="left", anchor="nw", fill="both", expand=True)

    LARGURA_RAIA = 120
    LARGURA_COL = 260

    # Configura colunas do grid
    frame_grade.grid_columnconfigure(0, minsize=LARGURA_RAIA)
    for i in range(len(colunas)):
        frame_grade.grid_columnconfigure(i + 1, minsize=LARGURA_COL)

    # ── Linha 0: cabeçalho das colunas ────────────────────────────────────────
    # Célula vazia no canto superior esquerdo
    ctk.CTkFrame(frame_grade, fg_color="transparent", width=LARGURA_RAIA, height=60).grid(
        row=0, column=0, padx=4, pady=4
    )

    for col_idx, coluna in enumerate(colunas):
        _criar_cabecalho_coluna(frame_grade, coluna, col_idx + 1, frame_kanban, colunas)

    # ── Linhas seguintes: uma por raia ────────────────────────────────────────
    # Faixa "Sem Raia" sempre aparece primeiro
    _criar_linha_raia(frame_grade, None, colunas, 1, frame_kanban)

    for raia_idx, raia in enumerate(raias):
        _criar_linha_raia(frame_grade, raia, colunas, raia_idx + 2, frame_kanban)


def _criar_cabecalho_coluna(frame_grade, coluna, col_idx, frame_kanban, colunas) -> None:
    """Cria a célula de cabeçalho de uma coluna com contador WIP e botões."""
    total = cartao_repository.contar_por_coluna(coluna.id_coluna)
    wip_atingido = coluna.limite_col is not None and total >= coluna.limite_col
    cor_indicador = "#FF5555" if wip_atingido else "#7B4DFF"
    limite_texto = f"/{coluna.limite_col}" if coluna.limite_col else ""

    frame_cab = ctk.CTkFrame(
        frame_grade,
        fg_color="#DEDEDE",
        corner_radius=8,
        height=60
    )
    frame_cab.grid(row=0, column=col_idx, sticky="nsew", padx=4, pady=4)
    frame_cab.grid_propagate(False)

    # Linha superior: contador + nome
    frame_topo = ctk.CTkFrame(frame_cab, fg_color="transparent")
    frame_topo.pack(fill="x", padx=6, pady=(6, 2))

    ctk.CTkLabel(
        frame_topo,
        text=f"{total}{limite_texto}",
        font=("Arial", 11, "bold"),
        fg_color=cor_indicador,
        text_color="white",
        corner_radius=8,
        width=36, height=20
    ).pack(side="left")

    # Banner de WIP atingido
    if wip_atingido:
        ctk.CTkLabel(
            frame_topo,
            text="WIP!",
            font=("Arial", 9, "bold"),
            fg_color="#FF5555",
            text_color="white",
            corner_radius=4,
            width=28, height=16
        ).pack(side="left", padx=(4, 0))

    ctk.CTkLabel(
        frame_topo,
        text=coluna.nome,
        font=("Arial", 12, "bold"),
        text_color="#333333"
    ).pack(side="left", padx=(6, 0))

    # Linha inferior: botões de ação
    frame_btns = ctk.CTkFrame(frame_cab, fg_color="transparent")
    frame_btns.pack(fill="x", padx=6, pady=(0, 4))

    for texto, direcao in [("◀", -1), ("▶", 1)]:
        ctk.CTkButton(
            frame_btns,
            text=texto,
            width=28, height=22,
            font=("Arial", 13, "bold"),
            fg_color="#CCCCCC",
            hover_color="#AAAAAA",
            text_color="#444444",
            corner_radius=4,
            command=lambda c=coluna, d=direcao: _mover_coluna(c, frame_kanban, d)
        ).pack(side="left", padx=(0, 2))

    ctk.CTkButton(
        frame_btns,
        text="⚙️",
        width=28, height=22,
        font=("Arial", 11),
        fg_color="#CCCCCC",
        hover_color="#AAAAAA",
        text_color="#444444",
        corner_radius=4,
        command=lambda c=coluna: abrir_config_coluna(c, frame_kanban)
    ).pack(side="left", padx=(0, 2))


def _criar_linha_raia(frame_grade, raia, colunas, row_idx, frame_kanban) -> None:
    """Cria uma linha horizontal completa para uma raia."""
    nome_raia = raia.nome if raia else "Sem Raia"
    id_raia = raia.id_raia if raia else None
    cor_header = COR_RAIA_HEADER if raia else COR_RAIA_HEADER_SEMRAIA

    # Célula do nome da raia (coluna 0)
    frame_nome_raia = ctk.CTkFrame(
        frame_grade,
        fg_color=cor_header,
        corner_radius=8,
    )
    frame_nome_raia.grid(row=row_idx, column=0, sticky="nsew", padx=4, pady=4)

    frame_conteudo_raia = ctk.CTkFrame(frame_nome_raia, fg_color="transparent")
    frame_conteudo_raia.pack(fill="both", expand=True, padx=6, pady=6)

    ctk.CTkLabel(
        frame_conteudo_raia,
        text=nome_raia,
        font=("Arial", 12, "bold"),
        text_color="white",
        wraplength=100,
        justify="center"
    ).pack(anchor="center", expand=True)

    if raia:
        ctk.CTkButton(
            frame_conteudo_raia,
            text="⚙️",
            width=24, height=24,
            font=("Arial", 11),
            fg_color="transparent",
            hover_color="#5a3db5",
            text_color="white",
            command=lambda r=raia: abrir_config_raia(r, frame_kanban)
        ).pack(anchor="s", pady=(4, 0))

    # Células dos cartões por coluna
    for col_idx, coluna in enumerate(colunas):
        _criar_celula_cartoes(
            frame_grade, coluna, id_raia, row_idx, col_idx + 1, frame_kanban
        )


def _criar_celula_cartoes(frame_grade, coluna, id_raia, row_idx, col_idx, frame_kanban) -> None:
    """Cria a célula que contém os cartões de uma (coluna x raia) específica."""
    frame_celula = ctk.CTkFrame(
        frame_grade,
        fg_color="#F0F0F0",
        corner_radius=8
    )
    frame_celula.grid(row=row_idx, column=col_idx, sticky="nsew", padx=4, pady=4)

    cartoes = cartao_repository.listar_por_coluna_e_raia(coluna.id_coluna, id_raia)

    frame_lista = ctk.CTkScrollableFrame(
        frame_celula,
        fg_color="transparent",
        label_text="",
        height=200
    )
    frame_lista.pack(fill="both", expand=True, padx=4, pady=(4, 2))

    for cartao in cartoes:
        _criar_widget_cartao(frame_lista, cartao, coluna, id_raia, frame_kanban)

    ctk.CTkButton(
        frame_celula,
        text="+ Cartão",
        height=26,
        font=("Arial", 11),
        fg_color="#7B4DFF",
        hover_color="#6738E6",
        corner_radius=6,
        command=lambda col=coluna, r=id_raia: abrir_dialog_criar_cartao(col, r, frame_kanban)
    ).pack(fill="x", padx=4, pady=(2, 4))


def _criar_widget_cartao(frame_lista, cartao, coluna, id_raia, frame_kanban) -> None:
    cor = CORES_PRIORIDADE.get(cartao.prioridade, "#999999")
    label_prio = LABELS_PRIORIDADE.get(cartao.prioridade, cartao.prioridade)

    frame_cartao = ctk.CTkFrame(
        frame_lista,
        fg_color="white",
        corner_radius=8,
        border_width=2,
        border_color=cor
    )
    frame_cartao.pack(fill="x", pady=4, padx=2)

    ctk.CTkFrame(frame_cartao, fg_color=cor, height=4, corner_radius=0).pack(fill="x")

    frame_topo = ctk.CTkFrame(frame_cartao, fg_color="transparent")
    frame_topo.pack(fill="x", padx=8, pady=(6, 0))

    ctk.CTkLabel(
        frame_topo,
        text=cartao.nome,
        font=("Arial", 11, "bold"),
        text_color="#222222",
        anchor="w",
        wraplength=150
    ).pack(side="left", fill="x", expand=True)

    ctk.CTkButton(
        frame_topo,
        text="⚙️",
        width=22, height=22,
        font=("Arial", 10),
        fg_color="transparent",
        hover_color="#EEEEEE",
        text_color="#666666",
        command=lambda c=cartao: abrir_detalhes_cartao(c, frame_kanban)
    ).pack(side="right")

    frame_info = ctk.CTkFrame(frame_cartao, fg_color="transparent")
    frame_info.pack(fill="x", padx=8, pady=(2, 4))

    if cartao.descricao and cartao.descricao.strip():
        ctk.CTkLabel(
            frame_info,
            text=cartao.descricao,
            font=("Arial", 9),
            text_color="#555555",
            anchor="w",
            wraplength=180,
            justify="left"
        ).pack(anchor="w", pady=(0, 3))

    ctk.CTkLabel(
        frame_info,
        text=f"● {label_prio}",
        font=("Arial", 9, "bold"),
        text_color=cor
    ).pack(anchor="w")

    ctk.CTkLabel(
        frame_info,
        text=f"📅 {_data_iso_para_br(cartao.data_limite)}",
        font=("Arial", 9),
        text_color="#666666"
    ).pack(anchor="w")

    try:
        responsavel = usuario_service.obter_usuario(cartao.id_user_responsavel)
        nome_responsavel = responsavel.nome
    except Exception:
        nome_responsavel = "—"

    ctk.CTkLabel(
        frame_info,
        text=f"👤 {nome_responsavel}",
        font=("Arial", 9),
        text_color="#666666"
    ).pack(anchor="w")

    # Botões de mover entre colunas
    frame_rodape = ctk.CTkFrame(frame_cartao, fg_color="transparent")
    frame_rodape.pack(fill="x", padx=8, pady=(2, 6))

    ctk.CTkButton(
        frame_rodape,
        text="◀",
        width=32, height=24,
        font=("Arial", 13, "bold"),
        fg_color="#DDDDDD",
        hover_color="#BBBBBB",
        text_color="#444444",
        corner_radius=6,
        command=lambda c=cartao, col=coluna: _mover_cartao(c, col, frame_kanban, direcao=-1)
    ).pack(side="left")

    ctk.CTkButton(
        frame_rodape,
        text="▶",
        width=32, height=24,
        font=("Arial", 13, "bold"),
        fg_color="#DDDDDD",
        hover_color="#BBBBBB",
        text_color="#444444",
        corner_radius=6,
        command=lambda c=cartao, col=coluna: _mover_cartao(c, col, frame_kanban, direcao=1)
    ).pack(side="right")


# ── LÓGICA DE MOVIMENTAÇÃO ─────────────────────────────────────────────────────

def _get_colunas_ordenadas(frame_kanban):
    colunas = coluna_service.listar_colunas_do_quadro(frame_kanban.quadro_atual.id_quadro)
    if hasattr(frame_kanban, 'ordem_colunas') and frame_kanban.ordem_colunas:
        mapa = {c.id_coluna: c for c in colunas}
        ids_conhecidos = [i for i in frame_kanban.ordem_colunas if i in mapa]
        ids_novos = [c.id_coluna for c in colunas if c.id_coluna not in frame_kanban.ordem_colunas]
        frame_kanban.ordem_colunas = ids_conhecidos + ids_novos
        return [mapa[i] for i in frame_kanban.ordem_colunas]
    return colunas


def _mover_coluna(coluna, frame_kanban: ctk.CTkFrame, direcao: int) -> None:
    if not hasattr(frame_kanban, 'ordem_colunas') or frame_kanban.ordem_colunas is None:
        colunas = coluna_service.listar_colunas_do_quadro(frame_kanban.quadro_atual.id_quadro)
        frame_kanban.ordem_colunas = [c.id_coluna for c in colunas]

    ids = frame_kanban.ordem_colunas
    if coluna.id_coluna not in ids:
        return

    idx_atual = ids.index(coluna.id_coluna)
    idx_novo = idx_atual + direcao

    if idx_novo < 0 or idx_novo >= len(ids):
        return

    ids[idx_atual], ids[idx_novo] = ids[idx_novo], ids[idx_atual]
    _renderizar_tudo(frame_kanban)


def _mover_cartao(cartao, coluna_atual, frame_kanban: ctk.CTkFrame, direcao: int) -> None:
    colunas = _get_colunas_ordenadas(frame_kanban)
    ids = [c.id_coluna for c in colunas]

    if coluna_atual.id_coluna not in ids:
        return

    idx_atual = ids.index(coluna_atual.id_coluna)
    idx_novo = idx_atual + direcao

    if idx_novo < 0 or idx_novo >= len(ids):
        return

    coluna_destino = colunas[idx_novo]

    try:
        cartao_service.mover_cartao(
            id_cartao=cartao.id_cartao,
            novo_id_coluna=coluna_destino.id_coluna
        )
        _renderizar_tudo(frame_kanban)
    except ValueError as e:
        _mostrar_aviso_wip(frame_kanban, str(e))


def _mostrar_aviso_wip(frame_kanban: ctk.CTkFrame, mensagem: str) -> None:
    aviso = ctk.CTkLabel(
        frame_kanban,
        text=f"⚠️ {mensagem}",
        font=("Arial", 12, "bold"),
        fg_color="#FF9800",
        text_color="white",
        corner_radius=8,
        padx=12,
        pady=6
    )
    aviso.place(relx=0.5, rely=0.08, anchor="center")
    frame_kanban.after(3000, aviso.destroy)


# ── MÁSCARA DE DATA ────────────────────────────────────────────────────────────

def _aplicar_mascara_data(entry: ctk.CTkEntry) -> None:
    def formatar(event=None):
        if event and event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab"):
            return
        texto = entry.get()
        digitos = ''.join(c for c in texto if c.isdigit())[:8]
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
    return datetime.strptime(data_br, "%d/%m/%Y").strftime("%Y-%m-%d")


def _data_iso_para_br(data_iso: str) -> str:
    if not data_iso:
        return ""
    try:
        return datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return data_iso


# ── DIALOGS ────────────────────────────────────────────────────────────────────

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
            _renderizar_tudo(frame_kanban)
        except ValueError as e:
            label_erro.configure(text=str(e))

    ctk.CTkButton(dialog, text="Criar", width=180, command=confirmar).pack(pady=(8, 4))
    ctk.CTkButton(dialog, text="Cancelar", width=180, fg_color="#888888",
                  hover_color="#666666", command=dialog.destroy).pack(pady=(0, 12))
    dialog.after(100, dialog.grab_set)


def abrir_dialog_criar_raia(frame_kanban: ctk.CTkFrame) -> None:
    dialog = ctk.CTkToplevel()
    dialog.title("Nova Raia")
    dialog.geometry("380x220")
    lw, lh = dialog.winfo_screenwidth(), dialog.winfo_screenheight()
    dialog.geometry(f"380x220+{int(lw/2-190)}+{int(lh/2-110)}")

    ctk.CTkLabel(dialog, text="Nova Raia", font=("Arial", 16, "bold")).pack(pady=(20, 12))
    ctk.CTkLabel(dialog, text="Nome da raia", font=("Arial", 13, "bold")).pack(pady=(0, 4))
    campo_nome = ctk.CTkEntry(dialog, placeholder_text="Ex: Urgente, Bug, Melhoria...", width=300)
    campo_nome.pack(pady=(0, 10))

    label_erro = ctk.CTkLabel(dialog, text="", text_color="#FF5555", font=("Arial", 11))
    label_erro.pack()

    def confirmar():
        nome = campo_nome.get().strip()
        try:
            raia_service.criar_raia(
                id_quadro=frame_kanban.quadro_atual.id_quadro,
                nome=nome
            )
            dialog.destroy()
            _renderizar_tudo(frame_kanban)
        except ValueError as e:
            label_erro.configure(text=str(e))

    ctk.CTkButton(dialog, text="Criar", width=180, command=confirmar).pack(pady=(8, 4))
    ctk.CTkButton(dialog, text="Cancelar", width=180, fg_color="#888888",
                  hover_color="#666666", command=dialog.destroy).pack(pady=(0, 12))
    dialog.after(100, dialog.grab_set)


def abrir_config_raia(raia, frame_kanban: ctk.CTkFrame) -> None:
    dialog = ctk.CTkToplevel()
    dialog.title("Configurações da Raia")
    dialog.geometry("380x250")
    lw, lh = dialog.winfo_screenwidth(), dialog.winfo_screenheight()
    dialog.geometry(f"380x250+{int(lw/2-190)}+{int(lh/2-125)}")

    ctk.CTkLabel(dialog, text="Configurações da Raia",
                 font=("Arial", 16, "bold")).pack(pady=(20, 12))
    ctk.CTkLabel(dialog, text="Nome da raia", font=("Arial", 13, "bold")).pack(pady=(0, 4))
    campo_nome = ctk.CTkEntry(dialog, placeholder_text="Nome", width=300)
    campo_nome.insert(0, raia.nome)
    campo_nome.pack(pady=(0, 8))

    label_feedback = ctk.CTkLabel(dialog, text="", font=("Arial", 11))
    label_feedback.pack()

    def salvar():
        novo_nome = campo_nome.get().strip()
        try:
            raia_service.atualizar_nome_raia(raia.id_raia, novo_nome)
            label_feedback.configure(text="Raia atualizada!", text_color="#4CAF50")
            dialog.after(1500, lambda: [dialog.destroy(), _renderizar_tudo(frame_kanban)])
        except ValueError as e:
            label_feedback.configure(text=str(e), text_color="#FF5555")

    def excluir():
        raia_service.excluir_raia(raia.id_raia)
        dialog.destroy()
        _renderizar_tudo(frame_kanban)

    ctk.CTkButton(dialog, text="Salvar Alterações", width=200, command=salvar).pack(pady=(4, 4))
    ctk.CTkButton(dialog, text="Excluir Raia", width=200,
                  fg_color="#FF5555", hover_color="#CC3333",
                  command=excluir).pack(pady=(0, 4))
    ctk.CTkButton(dialog, text="Cancelar", width=200, fg_color="#888888",
                  hover_color="#666666", command=dialog.destroy).pack(pady=(0, 15))
    dialog.after(100, dialog.grab_set)


def abrir_dialog_criar_cartao(coluna, id_raia, frame_kanban: ctk.CTkFrame) -> None:
    dialog = ctk.CTkToplevel()
    dialog.title("Novo Cartão")
    dialog.geometry("440x560")
    lw, lh = dialog.winfo_screenwidth(), dialog.winfo_screenheight()
    dialog.geometry(f"440x560+{int(lw/2-220)}+{int(lh/2-280)}")
    dialog.resizable(False, False)

    ctk.CTkLabel(dialog, text=f"Novo Cartão — {coluna.nome}",
                 font=("Arial", 16, "bold")).pack(pady=(20, 12))

    ctk.CTkLabel(dialog, text="Nome do Cartão", font=("Arial", 13, "bold")).pack(pady=(0, 4))
    campo_nome = ctk.CTkEntry(dialog, placeholder_text="Nome do cartão", width=360)
    campo_nome.pack(pady=(0, 8))

    ctk.CTkLabel(dialog, text="Descrição (opcional)", font=("Arial", 13, "bold")).pack(pady=(0, 4))
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
                descricao=desc,
                id_raia=id_raia
            )
            dialog.destroy()
            _renderizar_tudo(frame_kanban)
        except ValueError as e:
            label_erro.configure(text=str(e))

    ctk.CTkButton(dialog, text="Criar Cartão", width=200, command=confirmar).pack(pady=(12, 4))
    ctk.CTkButton(dialog, text="Cancelar", width=200, fg_color="#888888",
                  hover_color="#666666", command=dialog.destroy).pack(pady=(0, 15))
    dialog.after(100, dialog.grab_set)


def abrir_detalhes_cartao(cartao, frame_kanban: ctk.CTkFrame) -> None:
    dialog = ctk.CTkToplevel()
    dialog.title("Detalhes do Cartão")
    dialog.geometry("440x580")
    lw, lh = dialog.winfo_screenwidth(), dialog.winfo_screenheight()
    dialog.geometry(f"440x580+{int(lw/2-220)}+{int(lh/2-290)}")
    dialog.resizable(False, False)

    ctk.CTkLabel(dialog, text="Detalhes do Cartão",
                 font=("Arial", 16, "bold")).pack(pady=(20, 12))

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
    campo_prazo = ctk.CTkEntry(dialog, placeholder_text="DD/MM/AAAA", width=360)
    campo_prazo.insert(0, _data_iso_para_br(cartao.data_limite or ""))
    campo_prazo.pack(pady=(0, 4))
    _aplicar_mascara_data(campo_prazo)

    # Seleção de raia
    raias = raia_service.listar_raias_do_quadro(
        coluna_repository.buscar_por_id(cartao.id_coluna).id_quadro
    )
    opcoes_raia = ["Sem Raia"] + [r.nome for r in raias]
    mapa_raia = {r.nome: r.id_raia for r in raias}

    ctk.CTkLabel(dialog, text="Raia", font=("Arial", 13, "bold")).pack(pady=(8, 4))
    campo_raia = ctk.CTkOptionMenu(dialog, values=opcoes_raia, width=360)

    raia_atual = next((r.nome for r in raias if r.id_raia == cartao.id_raia), "Sem Raia")
    campo_raia.set(raia_atual)
    campo_raia.pack(pady=(0, 8))

    label_feedback = ctk.CTkLabel(dialog, text="", font=("Arial", 11))
    label_feedback.pack(pady=(4, 0))

    def salvar():
        novo_nome = campo_nome.get().strip()
        nova_desc = campo_desc.get("1.0", "end").strip()
        nova_prio = campo_prioridade.get()
        prazo_br = campo_prazo.get().strip()
        raia_selecionada = campo_raia.get()

        try:
            prazo_iso = _data_br_para_iso(prazo_br)
        except ValueError:
            label_feedback.configure(
                text="Data inválida. Use o formato DD/MM/AAAA.", text_color="#FF5555")
            return

        cartao.nome = novo_nome
        cartao.descricao = nova_desc
        cartao.prioridade = nova_prio
        cartao.data_limite = prazo_iso
        cartao.id_raia = mapa_raia.get(raia_selecionada, None)

        try:
            cartao_service.cartao_repo.atualizar(cartao)
            label_feedback.configure(text="Cartão atualizado!", text_color="#4CAF50")
            dialog.after(1500, lambda: [dialog.destroy(), _renderizar_tudo(frame_kanban)])
        except Exception as e:
            label_feedback.configure(text=str(e), text_color="#FF5555")

    def excluir():
        cartao_service.excluir_cartao(cartao.id_cartao)
        dialog.destroy()
        _renderizar_tudo(frame_kanban)

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

    ctk.CTkLabel(dialog, text="Configurações da Coluna",
                 font=("Arial", 16, "bold")).pack(pady=(20, 12))
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
                label_feedback.configure(
                    text="O limite deve ser um número inteiro.", text_color="#FF5555")
                return
            novo_limite = int(wip_texto)
        try:
            coluna_service.atualizar_coluna(coluna.id_coluna, novo_nome, novo_limite)
            label_feedback.configure(text="Coluna atualizada!", text_color="#4CAF50")
            dialog.after(1500, lambda: [dialog.destroy(), _renderizar_tudo(frame_kanban)])
        except ValueError as e:
            label_feedback.configure(text=str(e), text_color="#FF5555")

    def excluir():
        try:
            coluna_service.excluir_coluna(coluna.id_coluna)
            dialog.destroy()
            _renderizar_tudo(frame_kanban)
        except ValueError as e:
            label_feedback.configure(text=str(e), text_color="#FF5555")

    ctk.CTkButton(dialog, text="Salvar Alterações", width=200, command=salvar).pack(pady=(4, 4))
    ctk.CTkButton(dialog, text="Excluir Coluna", width=200,
                  fg_color="#FF5555", hover_color="#CC3333", command=excluir).pack(pady=(0, 4))
    ctk.CTkButton(dialog, text="Cancelar", width=200, fg_color="#888888",
                  hover_color="#666666", command=dialog.destroy).pack(pady=(0, 15))
    dialog.after(100, dialog.grab_set)
