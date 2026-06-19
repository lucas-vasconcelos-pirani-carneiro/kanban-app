import customtkinter as ctk
from src.repositories.usuario_repository import UsuarioRepository
from src.repositories.projeto_repository import ProjetoRepository
from src.services.usuario_service import UsuarioService
from src.services.projeto_service import ProjetoService

usuario_repository = UsuarioRepository()
projeto_repository = ProjetoRepository()
usuario_service = UsuarioService(usuario_repository)
projeto_service = ProjetoService(projeto_repository)

def populate_dashboard_screen(frame_dashboard: ctk.CTkFrame, show_frame, main_frame) -> None:
    frame_header = ctk.CTkFrame(frame_dashboard, fg_color="transparent")
    frame_header.pack(side="top", fill="x", padx=20, pady=20)
    frame_header.grid_columnconfigure(1, weight=1)

    label_quadros = ctk.CTkLabel(
        frame_header,
        text="Meus Projetos",
        font=("Arial", 24, "bold")
    )
    label_quadros.grid(row=0, column=0, sticky="w")

    botao_perfil = ctk.CTkButton(
        frame_header,
        text="👤",
        width=50,
        height=50,
        corner_radius=25,
        font=("Arial", 24),
        command=lambda: click_perfil()
    )
    botao_perfil.grid(row=0, column=1, sticky="e")

    linha = ctk.CTkFrame(frame_dashboard, height=2, fg_color="#cccccc")
    linha.pack(side="top", fill="x", padx=20)

    frame_conteudo = ctk.CTkFrame(frame_dashboard, fg_color="transparent")
    frame_conteudo.pack(side="top", fill="both", expand=True, padx=20, pady=20)

    frame_cards_container = ctk.CTkScrollableFrame(
        frame_conteudo,
        fg_color="transparent",
        label_text="",
    )
    frame_cards_container.pack(fill="both", expand=True)

    frame_cards_container.grid_columnconfigure(0, weight=1)
    frame_cards_container.grid_columnconfigure(1, weight=1)
    frame_cards_container.grid_columnconfigure(2, weight=1)

    frame_dashboard.cards_container = frame_cards_container
    frame_dashboard.show_frame = show_frame
    frame_dashboard.main_frame = main_frame
    frame_dashboard.card_grid_column = 0
    frame_dashboard.card_grid_row = 0
    frame_dashboard.usuario_logado = None

    frame_botao = ctk.CTkFrame(frame_dashboard, fg_color="transparent")
    frame_botao.pack(side="bottom", fill="x", padx=20, pady=20)

    botao_sair = ctk.CTkButton(
        frame_botao,
        text="Sair",
        font=("Arial", 14, "bold"),
        fg_color="#FF5555",
        hover_color="#CC3333",
        command=lambda: fazer_logout(frame_dashboard, show_frame, main_frame)
    )
    botao_sair.pack(side="right")

    botao_criar_quadro = ctk.CTkButton(
        frame_botao,
        text="+ Novo Projeto",
        font=("Arial", 14, "bold"),
        command=lambda: abrir_dialog_criar_projeto(frame_dashboard)
    )
    botao_criar_quadro.pack(side="left")

def carregar_projetos(frame_dashboard: ctk.CTkFrame) -> None:
    # Limpa os cards existentes
    for widget in frame_dashboard.cards_container.winfo_children():
        widget.destroy()

    frame_dashboard.card_grid_column = 0
    frame_dashboard.card_grid_row = 0

    projetos = projeto_service.listar_projetos()

    if not projetos:
        label_vazio = ctk.CTkLabel(
            frame_dashboard.cards_container,
            text="Nenhum projeto encontrado.\nClique em '+ Novo Projeto' para começar.",
            font=("Arial", 14),
            text_color="#888888"
        )
        label_vazio.grid(row=0, column=0, columnspan=3, pady=40)
        return

    for projeto in projetos:
        add_card(frame_dashboard, projeto.nome, projeto.descricao or "Sem descrição", projeto.id_proj)

def add_card(frame_dashboard: ctk.CTkFrame, titulo_card: str, descricao: str = "", id_proj: int = None) -> None:
    container = frame_dashboard.cards_container

    frame_card = ctk.CTkFrame(
        container,
        fg_color="#f0f0f0",
        corner_radius=10,
        border_width=2,
        border_color="#e0e0e0",
        width=360,
        height=280
    )
    frame_card.grid(
        row=frame_dashboard.card_grid_row,
        column=frame_dashboard.card_grid_column,
        padx=10, pady=10,
        sticky="nsew"
    )

    frame_dashboard.card_grid_column += 1
    if frame_dashboard.card_grid_column >= 3:
        frame_dashboard.card_grid_column = 0
        frame_dashboard.card_grid_row += 1

    frame_interno = ctk.CTkFrame(frame_card, fg_color="transparent")
    frame_interno.pack(fill="both", expand=True, padx=12, pady=12)

    label_titulo_card = ctk.CTkLabel(
        frame_interno,
        text=titulo_card,
        font=("Arial", 16, "bold"),
        text_color="#333333"
    )
    label_titulo_card.pack(anchor="w")

    label_desc_card = ctk.CTkLabel(
        frame_interno,
        text=descricao,
        font=("Arial", 12),
        text_color="#666666",
        wraplength=280
    )
    label_desc_card.pack(anchor="w", pady=(5, 0))

    botao_config = ctk.CTkButton(
        frame_card,
        text="⚙️",
        width=40,
        height=40,
        font=("Arial", 18),
        fg_color="transparent",
        text_color="#666666",
        hover_color="#e0e0e0",
        command=lambda: click_config(titulo_card, id_proj, frame_dashboard)
    )
    botao_config.place(relx=0.95, rely=0.05, anchor="ne")

    def on_card_click(event=None):
        click_card(titulo_card, id_proj, frame_dashboard)

    for widget in [frame_card, frame_interno, label_titulo_card, label_desc_card]:
        widget.bind("<Button-1>", on_card_click)

def abrir_dialog_criar_projeto(frame_dashboard: ctk.CTkFrame) -> None:
    dialog = ctk.CTkToplevel()
    dialog.title("Novo Projeto")
    dialog.geometry("400x300")

    # Centraliza o dialog na tela
    largura_tela = dialog.winfo_screenwidth()
    altura_tela = dialog.winfo_screenheight()
    pos_x = int((largura_tela / 2) - (400 / 2))
    pos_y = int((altura_tela / 2) - (300 / 2))
    dialog.geometry(f"400x300+{pos_x}+{pos_y}")

    ctk.CTkLabel(dialog, text="Nome do Projeto", font=("Arial", 14, "bold")).pack(pady=(20, 5))
    campo_nome = ctk.CTkEntry(dialog, placeholder_text="Digite o nome do projeto", width=300)
    campo_nome.pack(pady=(0, 10))

    ctk.CTkLabel(dialog, text="Descrição (opcional)", font=("Arial", 14, "bold")).pack(pady=(0, 5))
    campo_desc = ctk.CTkEntry(dialog, placeholder_text="Digite uma descrição", width=300)
    campo_desc.pack(pady=(0, 10))

    label_erro = ctk.CTkLabel(dialog, text="", text_color="#FF5555", font=("Arial", 11))
    label_erro.pack()

    def confirmar():
        nome = campo_nome.get().strip()
        descricao = campo_desc.get().strip()
        usuario = frame_dashboard.usuario_logado

        if not usuario:
            label_erro.configure(text="Nenhum usuário logado.")
            return

        try:
            projeto_service.criar_projeto(
                nome=nome,
                id_user_criador=usuario.id_user,
                descricao=descricao
            )
            dialog.destroy()
            carregar_projetos(frame_dashboard)
        except ValueError as e:
            label_erro.configure(text=str(e))

    ctk.CTkButton(dialog, text="Criar", command=confirmar).pack(pady=(10, 0))
    ctk.CTkButton(
        dialog,
        text="Cancelar",
        fg_color="#888888",
        hover_color="#666666",
        command=dialog.destroy
    ).pack(pady=(5, 0))

    # Aguarda a janela estar visível antes de aplicar o grab
    dialog.after(100, dialog.grab_set)

def abrir_config_projeto(titulo_card: str, id_proj: int, frame_dashboard: ctk.CTkFrame) -> None:
    dialog = ctk.CTkToplevel()
    dialog.title("Configurações do Projeto")
    dialog.geometry("400x380")

    largura_tela = dialog.winfo_screenwidth()
    altura_tela = dialog.winfo_screenheight()
    pos_x = int((largura_tela / 2) - (400 / 2))
    pos_y = int((altura_tela / 2) - (380 / 2))
    dialog.geometry(f"400x380+{pos_x}+{pos_y}")

    ctk.CTkLabel(
        dialog,
        text="Configurações do Projeto",
        font=("Arial", 16, "bold")
    ).pack(pady=(20, 15))

    ctk.CTkLabel(dialog, text="Nome do Projeto", font=("Arial", 13, "bold")).pack(pady=(0, 5))
    campo_nome = ctk.CTkEntry(dialog, placeholder_text="Nome do projeto", width=300)
    campo_nome.insert(0, titulo_card)
    campo_nome.pack(pady=(0, 10))

    ctk.CTkLabel(dialog, text="Descrição", font=("Arial", 13, "bold")).pack(pady=(0, 5))

    # Busca a descrição atual do projeto
    try:
        projeto_atual = projeto_service.obter_projeto(id_proj)
        descricao_atual = projeto_atual.descricao or ""
    except ValueError:
        descricao_atual = ""

    campo_desc = ctk.CTkEntry(dialog, placeholder_text="Descrição do projeto", width=300)
    campo_desc.insert(0, descricao_atual)
    campo_desc.pack(pady=(0, 10))

    label_feedback = ctk.CTkLabel(dialog, text="", font=("Arial", 11))
    label_feedback.pack(pady=(0, 5))

    def salvar_edicao():
        novo_nome = campo_nome.get().strip()
        nova_desc = campo_desc.get().strip()
        label_feedback.configure(text="", text_color="#FF5555")

        try:
            projeto_service.atualizar_projeto(id_proj, novo_nome, nova_desc)
            label_feedback.configure(text="Projeto atualizado com sucesso!", text_color="#55FF55")
            dialog.after(1500, lambda: [dialog.destroy(), carregar_projetos(frame_dashboard)])
        except ValueError as e:
            label_feedback.configure(text=str(e), text_color="#FF5555")

    def confirmar_exclusao():
        confirm_dialog = ctk.CTkToplevel()
        confirm_dialog.title("Confirmar Exclusão")
        confirm_dialog.geometry("360x180")

        largura_tela = confirm_dialog.winfo_screenwidth()
        altura_tela = confirm_dialog.winfo_screenheight()
        pos_x = int((largura_tela / 2) - (360 / 2))
        pos_y = int((altura_tela / 2) - (180 / 2))
        confirm_dialog.geometry(f"360x180+{pos_x}+{pos_y}")

        ctk.CTkLabel(
            confirm_dialog,
            text=f"Tem certeza que deseja excluir\n\"{titulo_card}\"?",
            font=("Arial", 13),
            wraplength=300
        ).pack(pady=(25, 15))

        frame_botoes = ctk.CTkFrame(confirm_dialog, fg_color="transparent")
        frame_botoes.pack()

        def executar_exclusao():
            try:
                projeto_service.excluir_projeto(id_proj)
                confirm_dialog.destroy()
                dialog.destroy()
                carregar_projetos(frame_dashboard)
            except ValueError as e:
                confirm_dialog.destroy()
                label_feedback.configure(text=str(e), text_color="#FF5555")

        ctk.CTkButton(
            frame_botoes,
            text="Excluir",
            fg_color="#FF5555",
            hover_color="#CC3333",
            width=120,
            command=executar_exclusao
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            frame_botoes,
            text="Cancelar",
            fg_color="#888888",
            hover_color="#666666",
            width=120,
            command=confirm_dialog.destroy
        ).pack(side="left", padx=10)

        confirm_dialog.after(100, confirm_dialog.grab_set)

    ctk.CTkButton(
        dialog,
        text="Salvar Alterações",
        width=200,
        command=salvar_edicao
    ).pack(pady=(5, 5))

    ctk.CTkButton(
        dialog,
        text="Excluir Projeto",
        width=200,
        fg_color="#FF5555",
        hover_color="#CC3333",
        command=confirmar_exclusao
    ).pack(pady=(5, 5))

    ctk.CTkButton(
        dialog,
        text="Cancelar",
        width=200,
        fg_color="#888888",
        hover_color="#666666",
        command=dialog.destroy
    ).pack(pady=(5, 15))

    dialog.after(100, dialog.grab_set)

def fazer_logout(frame_dashboard, show_frame, main_frame):
    frame_dashboard.usuario_logado = None
    show_frame(main_frame)

def click_card(titulo_card: str, id_proj: int, frame_dashboard: ctk.CTkFrame) -> None:
    print(f"Projeto clicado: {titulo_card} (id: {id_proj})")

def click_config(titulo_card: str, id_proj: int, frame_dashboard: ctk.CTkFrame) -> None:
    abrir_config_projeto(titulo_card, id_proj, frame_dashboard)

def click_perfil():
    print("Perfil clicado")
