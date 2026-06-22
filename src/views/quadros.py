import customtkinter as ctk
from src.repositories.quadro_repository import QuadroRepository
from src.repositories.coluna_repository import ColunaRepository
from src.services.quadro_service import QuadroService
from src.services.coluna_service import ColunaService

quadro_repository = QuadroRepository()
coluna_repository = ColunaRepository()
quadro_service = QuadroService(quadro_repository)
coluna_service = ColunaService(coluna_repository)


def populate_quadros_screen(frame_quadros: ctk.CTkFrame, show_frame, frame_dashboard) -> None:
    frame_quadros.projeto_atual = None
    frame_quadros.show_frame = show_frame
    frame_quadros.frame_dashboard = frame_dashboard

    frame_header = ctk.CTkFrame(frame_quadros, fg_color="transparent")
    frame_header.pack(side="top", fill="x", padx=20, pady=20)
    frame_header.grid_columnconfigure(1, weight=1)

    frame_quadros.label_titulo = ctk.CTkLabel(
        frame_header,
        text="Meus Quadros",
        font=("Arial", 24, "bold")
    )
    frame_quadros.label_titulo.grid(row=0, column=0, sticky="w")

    botao_perfil = ctk.CTkButton(
        frame_header,
        text="👤",
        width=50,
        height=50,
        corner_radius=25,
        font=("Arial", 24),
        fg_color="transparent",
        hover_color="#e0e0e0",
        text_color="#333333",
        command=lambda: None
    )
    botao_perfil.grid(row=0, column=1, sticky="e")

    linha = ctk.CTkFrame(frame_quadros, height=2, fg_color="#cccccc")
    linha.pack(side="top", fill="x", padx=20)

    frame_conteudo = ctk.CTkFrame(frame_quadros, fg_color="transparent")
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

    frame_quadros.cards_container = frame_cards_container
    frame_quadros.card_grid_column = 0
    frame_quadros.card_grid_row = 0

    frame_botoes = ctk.CTkFrame(frame_quadros, fg_color="transparent")
    frame_botoes.pack(side="bottom", fill="x", padx=20, pady=20)

    ctk.CTkButton(
        frame_botoes,
        text="Voltar",
        font=("Arial", 14, "bold"),
        fg_color="#888888",
        hover_color="#666666",
        command=lambda: show_frame(frame_dashboard)
    ).pack(side="left")

    ctk.CTkButton(
        frame_botoes,
        text="+ Criar Novo Quadro",
        font=("Arial", 14, "bold"),
        command=lambda: abrir_dialog_criar_quadro(frame_quadros)
    ).pack(side="left", padx=(10, 0))


def carregar_quadros(frame_quadros: ctk.CTkFrame, projeto) -> None:
    frame_quadros.projeto_atual = projeto
    frame_quadros.label_titulo.configure(text=f"Quadros - {projeto.nome}")

    for widget in frame_quadros.cards_container.winfo_children():
        widget.destroy()

    frame_quadros.card_grid_column = 0
    frame_quadros.card_grid_row = 0

    quadros = quadro_service.listar_quadros_do_projeto(projeto.id_proj)

    if not quadros:
        ctk.CTkLabel(
            frame_quadros.cards_container,
            text="Nenhum quadro encontrado.\nClique em '+ Criar Novo Quadro' para começar.",
            font=("Arial", 14),
            text_color="#888888"
        ).grid(row=0, column=0, columnspan=3, pady=40)
        return

    for quadro in quadros:
        _add_card_quadro(frame_quadros, quadro)


def _add_card_quadro(frame_quadros: ctk.CTkFrame, quadro) -> None:
    container = frame_quadros.cards_container

    frame_card = ctk.CTkFrame(
        container,
        fg_color="#f0f0f0",
        corner_radius=10,
        border_width=2,
        border_color="#e0e0e0",
        width=360,
        height=200
    )
    frame_card.grid(
        row=frame_quadros.card_grid_row,
        column=frame_quadros.card_grid_column,
        padx=10, pady=10,
        sticky="nsew"
    )

    frame_quadros.card_grid_column += 1
    if frame_quadros.card_grid_column >= 3:
        frame_quadros.card_grid_column = 0
        frame_quadros.card_grid_row += 1

    frame_interno = ctk.CTkFrame(frame_card, fg_color="transparent")
    frame_interno.pack(fill="both", expand=True, padx=12, pady=12)

    label_nome = ctk.CTkLabel(
        frame_interno,
        text=quadro.nome,
        font=("Arial", 16, "bold"),
        text_color="#333333"
    )
    label_nome.pack(anchor="w")

    label_sub = ctk.CTkLabel(
        frame_interno,
        text="Clique para abrir",
        font=("Arial", 12),
        text_color="#666666"
    )
    label_sub.pack(anchor="w", pady=(5, 0))

    botao_config = ctk.CTkButton(
        frame_card,
        text="⚙️",
        width=40,
        height=40,
        font=("Arial", 18),
        fg_color="transparent",
        text_color="#666666",
        hover_color="#e0e0e0",
        command=lambda q=quadro: abrir_config_quadro(q, frame_quadros)
    )
    botao_config.place(relx=0.95, rely=0.05, anchor="ne")

    def on_click(event=None, q=quadro):
        abrir_kanban(q, frame_quadros)

    for widget in [frame_card, frame_interno, label_nome, label_sub]:
        widget.bind("<Button-1>", on_click)


def abrir_kanban(quadro, frame_quadros: ctk.CTkFrame) -> None:
    from src.views.kanban import carregar_kanban
    frame_kanban = frame_quadros.frame_kanban
    carregar_kanban(frame_kanban, quadro, frame_quadros)
    frame_quadros.show_frame(frame_kanban)


def abrir_dialog_criar_quadro(frame_quadros: ctk.CTkFrame) -> None:
    dialog = ctk.CTkToplevel()
    dialog.title("Criar Novo Quadro")
    dialog.geometry("420x320")

    largura = dialog.winfo_screenwidth()
    altura = dialog.winfo_screenheight()
    dialog.geometry(f"420x320+{int(largura/2 - 210)}+{int(altura/2 - 160)}")

    ctk.CTkLabel(dialog, text="Criar Novo Quadro", font=("Arial", 16, "bold")).pack(pady=(20, 15))

    ctk.CTkLabel(dialog, text="Nome do Quadro", font=("Arial", 13, "bold")).pack(pady=(0, 5))
    campo_nome = ctk.CTkEntry(dialog, placeholder_text="Ex: Sprint 1", width=320)
    campo_nome.pack(pady=(0, 10))

    ctk.CTkLabel(dialog, text="Colunas iniciais (separadas por vírgula)", font=("Arial", 13, "bold")).pack(pady=(0, 5))
    campo_colunas = ctk.CTkEntry(dialog, placeholder_text="Ex: Backlog, WIP, Concluido", width=320)
    campo_colunas.insert(0, "Backlog, WIP, Concluido")
    campo_colunas.pack(pady=(0, 10))

    label_erro = ctk.CTkLabel(dialog, text="", text_color="#FF5555", font=("Arial", 11))
    label_erro.pack()

    def confirmar():
        nome = campo_nome.get().strip()
        colunas_texto = campo_colunas.get().strip()
        label_erro.configure(text="")

        try:
            novo_quadro = quadro_service.criar_quadro(
                id_proj=frame_quadros.projeto_atual.id_proj,
                nome=nome
            )

            # Cria as colunas iniciais automaticamente
            if colunas_texto:
                nomes_colunas = [c.strip() for c in colunas_texto.split(",") if c.strip()]
                for nome_coluna in nomes_colunas:
                    coluna_service.criar_coluna(
                        id_quadro=novo_quadro.id_quadro,
                        nome=nome_coluna
                    )

            dialog.destroy()
            carregar_quadros(frame_quadros, frame_quadros.projeto_atual)
        except ValueError as e:
            label_erro.configure(text=str(e))

    ctk.CTkButton(dialog, text="Criar Quadro", width=200, command=confirmar).pack(pady=(10, 5))
    ctk.CTkButton(
        dialog, text="Cancelar", width=200,
        fg_color="#888888", hover_color="#666666",
        command=dialog.destroy
    ).pack(pady=(0, 15))

    dialog.after(100, dialog.grab_set)


def abrir_config_quadro(quadro, frame_quadros: ctk.CTkFrame) -> None:
    dialog = ctk.CTkToplevel()
    dialog.title("Configurações do Quadro")
    dialog.geometry("400x280")

    largura = dialog.winfo_screenwidth()
    altura = dialog.winfo_screenheight()
    dialog.geometry(f"400x280+{int(largura/2 - 200)}+{int(altura/2 - 140)}")

    ctk.CTkLabel(dialog, text="Configurações do Quadro", font=("Arial", 16, "bold")).pack(pady=(20, 15))
    ctk.CTkLabel(dialog, text="Nome do Quadro", font=("Arial", 13, "bold")).pack(pady=(0, 5))

    campo_nome = ctk.CTkEntry(dialog, placeholder_text="Nome do quadro", width=300)
    campo_nome.insert(0, quadro.nome)
    campo_nome.pack(pady=(0, 10))

    label_feedback = ctk.CTkLabel(dialog, text="", font=("Arial", 11))
    label_feedback.pack()

    def salvar():
        novo_nome = campo_nome.get().strip()
        try:
            quadro_service.atualizar_nome_quadro(quadro.id_quadro, novo_nome)
            label_feedback.configure(text="Quadro atualizado!", text_color="#55FF55")
            dialog.after(1500, lambda: [dialog.destroy(), carregar_quadros(frame_quadros, frame_quadros.projeto_atual)])
        except ValueError as e:
            label_feedback.configure(text=str(e), text_color="#FF5555")

    def excluir():
        confirm = ctk.CTkToplevel()
        confirm.title("Confirmar Exclusão")
        confirm.geometry("340x160")
        confirm.geometry(f"340x160+{int(largura/2 - 170)}+{int(altura/2 - 80)}")

        ctk.CTkLabel(
            confirm,
            text=f'Excluir "{quadro.nome}"?\nTodas as colunas e cartões serão removidos.',
            font=("Arial", 13), wraplength=300
        ).pack(pady=(25, 15))

        frame_btn = ctk.CTkFrame(confirm, fg_color="transparent")
        frame_btn.pack()

        def executar():
            quadro_service.excluir_quadro(quadro.id_quadro)
            confirm.destroy()
            dialog.destroy()
            carregar_quadros(frame_quadros, frame_quadros.projeto_atual)

        ctk.CTkButton(frame_btn, text="Excluir", fg_color="#FF5555", hover_color="#CC3333",
                      width=120, command=executar).pack(side="left", padx=10)
        ctk.CTkButton(frame_btn, text="Cancelar", fg_color="#888888", hover_color="#666666",
                      width=120, command=confirm.destroy).pack(side="left", padx=10)
        confirm.after(100, confirm.grab_set)

    ctk.CTkButton(dialog, text="Salvar Alterações", width=200, command=salvar).pack(pady=(5, 5))
    ctk.CTkButton(dialog, text="Excluir Quadro", width=200,
                  fg_color="#FF5555", hover_color="#CC3333", command=excluir).pack(pady=(0, 5))
    ctk.CTkButton(dialog, text="Cancelar", width=200,
                  fg_color="#888888", hover_color="#666666", command=dialog.destroy).pack(pady=(0, 15))

    dialog.after(100, dialog.grab_set)
