import customtkinter as ctk
from src.repositories.usuario_repository import UsuarioRepository
from src.repositories.projeto_repository import ProjetoRepository
from src.repositories.membro_projeto_repository import MembroProjetoRepository
from src.services.usuario_service import UsuarioService
from src.services.projeto_service import ProjetoService
from src.services.membro_projeto_service import MembroProjetoService

usuario_repository = UsuarioRepository()
projeto_repository = ProjetoRepository()
membro_projeto_repository = MembroProjetoRepository()
usuario_service = UsuarioService(usuario_repository)
projeto_service = ProjetoService(projeto_repository)
membro_projeto_service = MembroProjetoService(membro_projeto_repository)

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
    dialog.geometry("520x650")

    # Centraliza o dialog na tela
    largura_tela = dialog.winfo_screenwidth()
    altura_tela = dialog.winfo_screenheight()
    pos_x = int((largura_tela / 2) - (520 / 2))
    pos_y = int((altura_tela / 2) - (650 / 2))
    dialog.geometry(f"520x650+{pos_x}+{pos_y}")

    frame_conteudo = ctk.CTkScrollableFrame(dialog, fg_color="transparent", width=480, height=560)
    frame_conteudo.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(frame_conteudo, text="Nome do Projeto", font=("Arial", 14, "bold")).pack(pady=(10, 5))
    campo_nome = ctk.CTkEntry(frame_conteudo, placeholder_text="Digite o nome do projeto", width=380)
    campo_nome.pack(pady=(0, 10))

    ctk.CTkLabel(frame_conteudo, text="Descrição (opcional)", font=("Arial", 14, "bold")).pack(pady=(0, 5))
    campo_desc = ctk.CTkEntry(frame_conteudo, placeholder_text="Digite uma descrição", width=380)
    campo_desc.pack(pady=(0, 10))

    usuario_logado = obter_usuario_logado(frame_dashboard)
    participantes_emails = []
    if usuario_logado:
        participantes_emails.append(usuario_logado.email)

    ctk.CTkLabel(frame_conteudo, text="Adicionar participantes", font=("Arial", 14, "bold")).pack(pady=(10, 5))

    frame_adicionar = ctk.CTkFrame(frame_conteudo, fg_color="transparent")
    frame_adicionar.pack(fill="x", pady=(0, 10))

    campo_participante = ctk.CTkEntry(
        frame_adicionar,
        placeholder_text="Digite o e-mail do participante",
    )
    campo_participante.pack(side="left", fill="x", expand=True, padx=(0, 10))

    label_erro = ctk.CTkLabel(frame_conteudo, text="", text_color="#FF5555", font=("Arial", 11))
    label_erro.pack(pady=(0, 8))

    frame_lista_participantes = ctk.CTkScrollableFrame(frame_conteudo, height=180)
    frame_lista_participantes.pack(fill="x", expand=False, pady=(0, 10))

    def atualizar_lista_participantes():
        construir_lista_participantes(
            frame_lista_participantes,
            participantes_emails,
            permitir_remover=False,
            remover_participante=None,
            email_usuario_logado=usuario_logado.email if usuario_logado else ""
        )

    def adicionar_participante():
        email_digitado = campo_participante.get().strip()

        if not email_digitado:
            label_erro.configure(text="Digite um e-mail para adicionar.")
            return

        if email_ja_listado(email_digitado, participantes_emails):
            label_erro.configure(text="Este e-mail já está na lista de participantes.")
            return

        usuario = usuario_repository.buscar_por_email(email_digitado)
        if not usuario:
            label_erro.configure(text=f"Nenhum usuário encontrado com o e-mail {email_digitado}.")
            return

        participantes_emails.append(usuario.email)
        campo_participante.delete(0, "end")
        label_erro.configure(text="")
        atualizar_lista_participantes()

    ctk.CTkButton(frame_adicionar, text="Adicionar", width=110, command=adicionar_participante).pack(side="right")

    atualizar_lista_participantes()

    def confirmar():
        nome = campo_nome.get().strip()
        descricao = campo_desc.get().strip()
        usuario = obter_usuario_logado(frame_dashboard)

        if not usuario:
            label_erro.configure(text="Nenhum usuário logado.")
            return

        try:
            projeto = projeto_service.criar_projeto(
                nome=nome,
                id_user_criador=usuario.id_user,
                descricao=descricao
            )

            for email_participante in participantes_emails:
                if email_participante.strip().casefold() == usuario.email.strip().casefold():
                    continue

                usuario_participante = usuario_repository.buscar_por_email(email_participante)
                if not usuario_participante:
                    continue

                membro_projeto_service.adicionar_membro(
                    id_user_solicitante=usuario.id_user,
                    id_user_novo=usuario_participante.id_user,
                    id_proj=projeto.id_proj,
                    gerente=False
                )

            dialog.destroy()
            carregar_projetos(frame_dashboard)
        except ValueError as e:
            label_erro.configure(text=str(e))

    ctk.CTkButton(frame_conteudo, text="Criar", command=confirmar).pack(pady=(10, 0))
    ctk.CTkButton(
        frame_conteudo,
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
    dialog.geometry("560x700")

    largura_tela = dialog.winfo_screenwidth()
    altura_tela = dialog.winfo_screenheight()
    pos_x = int((largura_tela / 2) - (560 / 2))
    pos_y = int((altura_tela / 2) - (700 / 2))
    dialog.geometry(f"560x700+{pos_x}+{pos_y}")

    frame_conteudo = ctk.CTkScrollableFrame(dialog, fg_color="transparent", width=520, height=640)
    frame_conteudo.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(
        frame_conteudo,
        text="Configurações do Projeto",
        font=("Arial", 16, "bold")
    ).pack(pady=(10, 15))

    ctk.CTkLabel(frame_conteudo, text="Nome do Projeto", font=("Arial", 13, "bold")).pack(pady=(0, 5))
    campo_nome = ctk.CTkEntry(frame_conteudo, placeholder_text="Nome do projeto", width=400)
    campo_nome.insert(0, titulo_card)
    campo_nome.pack(pady=(0, 10))

    ctk.CTkLabel(frame_conteudo, text="Descrição", font=("Arial", 13, "bold")).pack(pady=(0, 5))

    # Busca a descrição atual do projeto
    try:
        projeto_atual = projeto_service.obter_projeto(id_proj)
        descricao_atual = projeto_atual.descricao or ""
    except ValueError:
        descricao_atual = ""

    campo_desc = ctk.CTkEntry(frame_conteudo, placeholder_text="Descrição do projeto", width=400)
    campo_desc.insert(0, descricao_atual)
    campo_desc.pack(pady=(0, 10))

    usuario_logado = obter_usuario_logado(frame_dashboard)
    email_usuario_logado = usuario_logado.email if usuario_logado else ""

    ctk.CTkLabel(frame_conteudo, text="Adicionar participantes", font=("Arial", 13, "bold")).pack(pady=(10, 5))

    frame_adicionar = ctk.CTkFrame(frame_conteudo, fg_color="transparent")
    frame_adicionar.pack(fill="x", pady=(0, 10))

    campo_participante = ctk.CTkEntry(
        frame_adicionar,
        placeholder_text="Digite o e-mail do participante"
    )
    campo_participante.pack(side="left", fill="x", expand=True, padx=(0, 10))

    label_feedback = ctk.CTkLabel(frame_conteudo, text="", font=("Arial", 11))
    label_feedback.pack(pady=(0, 8))

    frame_lista_participantes = ctk.CTkScrollableFrame(frame_conteudo, height=220)
    frame_lista_participantes.pack(fill="x", expand=False, pady=(0, 10))

    def remover_participante(email_participante: str):
        if not usuario_logado:
            label_feedback.configure(text="Nenhum usuário logado.", text_color="#FF5555")
            return

        usuario_participante = usuario_repository.buscar_por_email(email_participante)
        if not usuario_participante:
            label_feedback.configure(
                text=f"Nenhum usuário encontrado com o e-mail {email_participante}.",
                text_color="#FF5555"
            )
            return

        try:
            membro_projeto_service.remover_membro(
                id_user_solicitante=usuario_logado.id_user,
                id_user_alvo=usuario_participante.id_user,
                id_proj=id_proj,
            )
            label_feedback.configure(text="Participante removido com sucesso!", text_color="#55FF55")
            atualizar_participantes()
        except (ValueError, PermissionError) as e:
            label_feedback.configure(text=str(e), text_color="#FF5555")

    def atualizar_participantes():
        participantes_emails = obter_participantes_emails(id_proj)
        construir_lista_participantes(
            frame_lista_participantes,
            participantes_emails,
            permitir_remover=True,
            remover_participante=remover_participante,
            email_usuario_logado=email_usuario_logado,
        )

    def adicionar_participante():
        if not usuario_logado:
            label_feedback.configure(text="Nenhum usuário logado.", text_color="#FF5555")
            return

        email_digitado = campo_participante.get().strip()
        if not email_digitado:
            label_feedback.configure(text="Digite um e-mail para adicionar.", text_color="#FF5555")
            return

        usuario_participante = usuario_repository.buscar_por_email(email_digitado)
        if not usuario_participante:
            label_feedback.configure(
                text=f"Nenhum usuário encontrado com o e-mail {email_digitado}.",
                text_color="#FF5555"
            )
            return

        try:
            membro_projeto_service.adicionar_membro(
                id_user_solicitante=usuario_logado.id_user,
                id_user_novo=usuario_participante.id_user,
                id_proj=id_proj,
                gerente=False
            )
            campo_participante.delete(0, "end")
            label_feedback.configure(text="Participante adicionado com sucesso!", text_color="#55FF55")
            atualizar_participantes()
        except (ValueError, PermissionError) as e:
            label_feedback.configure(text=str(e), text_color="#FF5555")

    ctk.CTkButton(frame_adicionar, text="Adicionar", width=110, command=adicionar_participante).pack(side="right")

    atualizar_participantes()

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

    frame_acoes = ctk.CTkFrame(frame_conteudo, fg_color="transparent")
    frame_acoes.pack(pady=(10, 15))

    ctk.CTkButton(
        frame_acoes,
        text="Salvar Alterações",
        width=150,
        command=salvar_edicao
    ).pack(side="left", padx=5)

    ctk.CTkButton(
        frame_acoes,
        text="Excluir Projeto",
        width=150,
        fg_color="#FF5555",
        hover_color="#CC3333",
        command=confirmar_exclusao
    ).pack(side="left", padx=5)

    ctk.CTkButton(
        frame_acoes,
        text="Cancelar",
        width=150,
        fg_color="#888888",
        hover_color="#666666",
        command=dialog.destroy
    ).pack(side="left", padx=5)

    dialog.after(100, dialog.grab_set)

def fazer_logout(frame_dashboard, show_frame, main_frame):
    frame_dashboard.usuario_logado = None
    show_frame(main_frame)

def obter_email_usuario(id_user: int) -> str:
    usuario = usuario_repository.buscar_por_id(id_user)
    if not usuario:
        raise ValueError("Usuário não encontrado.")
    return usuario.email


def obter_participantes_emails(id_proj: int) -> list[str]:
    participantes = []

    for membro in membro_projeto_service.listar_membros_do_projeto(id_proj):
        try:
            participantes.append(obter_email_usuario(membro.id_user))
        except ValueError:
            continue

    return participantes


def email_ja_listado(email: str, participantes: list[str]) -> bool:
    email_normalizado = email.strip().casefold()
    return any(participante.strip().casefold() == email_normalizado for participante in participantes)


def construir_lista_participantes(
    frame_lista: ctk.CTkScrollableFrame,
    participantes: list[str],
    permitir_remover: bool,
    remover_participante,
    email_usuario_logado: str = "",
) -> None:
    for widget in frame_lista.winfo_children():
        widget.destroy()

    if not participantes:
        ctk.CTkLabel(
            frame_lista,
            text="Nenhum participante adicionado.",
            font=("Arial", 12),
            text_color="#888888"
        ).pack(pady=10)
        return

    for email in participantes:
        frame_item = ctk.CTkFrame(frame_lista, fg_color="transparent")
        frame_item.pack(fill="x", padx=4, pady=4)

        texto_email = email
        if email_usuario_logado and email.strip().casefold() == email_usuario_logado.strip().casefold():
            texto_email = f"{email} (você)"

        ctk.CTkLabel(
            frame_item,
            text=texto_email,
            font=("Arial", 12),
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        if permitir_remover and remover_participante and not (
            email_usuario_logado and email.strip().casefold() == email_usuario_logado.strip().casefold()
        ):
            ctk.CTkButton(
                frame_item,
                text="Remover",
                width=90,
                fg_color="#FF5555",
                hover_color="#CC3333",
                command=lambda email_participante=email: remover_participante(email_participante)
            ).pack(side="right", padx=(10, 0))


def obter_usuario_logado(frame_dashboard: ctk.CTkFrame):
    return frame_dashboard.usuario_logado

def click_card(titulo_card: str, id_proj: int, frame_dashboard: ctk.CTkFrame) -> None:
    print(f"Projeto clicado: {titulo_card} (id: {id_proj})")

def click_config(titulo_card: str, id_proj: int, frame_dashboard: ctk.CTkFrame) -> None:
    abrir_config_projeto(titulo_card, id_proj, frame_dashboard)