from PIL import Image
import customtkinter as ctk

# Cards de quadros da dashboard
cards = []

def populate_dashboard_screen(frame_dashboard: ctk.CTkFrame, show_frame, main_frame) -> None:
    frame_header = ctk.CTkFrame(frame_dashboard, fg_color="transparent")
    frame_header.pack(side="top", fill="x", padx=20, pady=20)
    frame_header.grid_columnconfigure(1, weight=1)
    
    label_quadros = ctk.CTkLabel(
        frame_header,
        text="Meus Quadros",
        font=("Arial", 24, "bold")
    )
    label_quadros.grid(row=0, column=0, sticky="w")
    
    # Ícone de foto de perfil (emoji é temporário)
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
    
    # Linha para separar o cabeçalho do conteúdo
    linha = ctk.CTkFrame(frame_dashboard, height=2, fg_color="#cccccc")
    linha.pack(side="top", fill="x", padx=20)
    
    # Frame para os cards de quadros
    frame_conteudo = ctk.CTkFrame(frame_dashboard, fg_color="transparent")
    frame_conteudo.pack(side="top", fill="both", expand=True, padx=20, pady=20)
    
    # Container scrollavel para os cards
    frame_cards_container = ctk.CTkScrollableFrame(
        frame_conteudo,
        fg_color="transparent",
        label_text="",
    )
    frame_cards_container.pack(fill="both", expand=True)
    
    frame_cards_container.grid_columnconfigure(0, weight=1)
    frame_cards_container.grid_columnconfigure(1, weight=1)
    frame_cards_container.grid_columnconfigure(2, weight=1)
    
    # Armazena os cards
    frame_dashboard.cards_container = frame_cards_container
    frame_dashboard.show_frame = show_frame
    frame_dashboard.main_frame = main_frame
    frame_dashboard.card_grid_column = 0
    frame_dashboard.card_grid_row = 0
    
    # Adiciona quadros (apenas para teste por enquanto)
    add_card(frame_dashboard, "Projeto 1")
    
    # Frame para o botão de criar novo quadro
    frame_botao = ctk.CTkFrame(frame_dashboard, fg_color="transparent")
    frame_botao.pack(side="bottom", fill="x", padx=20, pady=20)
    
    # Botão para criar novo quadro
    botao_criar_quadro = ctk.CTkButton(
        frame_botao,
        text="Criar novo Quadro",
        font=("Arial", 14, "bold"),
        command=lambda: criar_quadro(frame_dashboard)
    )
    botao_criar_quadro.pack(side="left")

def add_card(frame_dashboard: ctk.CTkFrame, titulo_card: str) -> None:
    container = frame_dashboard.cards_container
    
    # Cria frame do card
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
    
    # Atualiza a posição para o próximo card
    frame_dashboard.card_grid_column += 1
    if frame_dashboard.card_grid_column >= 4:
        frame_dashboard.card_grid_column = 0
        frame_dashboard.card_grid_row += 1
    
    # Frame interno para o conteúdo do card
    frame_interno = ctk.CTkFrame(frame_card, fg_color="transparent")
    frame_interno.pack(fill="both", expand=True, padx=12, pady=12)
    
    # Label do título do card
    label_titulo_card = ctk.CTkLabel(
        frame_interno,
        text=titulo_card,
        font=("Arial", 16, "bold"),
        text_color="#333333"
    )
    label_titulo_card.pack(anchor="w")
    
    # Descrição do card
    label_desc_card = ctk.CTkLabel(
        frame_interno,
        text="Clique para abrir",
        font=("Arial", 12),
        text_color="#666666"
    )
    label_desc_card.pack(anchor="w", pady=(5, 0))
    
    # Botão de configurações do quadro
    botao_config = ctk.CTkButton(
        frame_card,
        text="⚙️",
        width=40,
        height=40,
        font=("Arial", 18),
        fg_color="transparent",
        text_color="#666666",
        hover_color="#e0e0e0",
        command=lambda: click_config(titulo_card)
    )
    botao_config.place(relx=0.95, rely=0.05, anchor="ne")
    
    # Faz o card ser clicável
    def on_card_click(event=None):
        click_card(titulo_card, frame_dashboard)
    
    for widget in [frame_card, frame_interno, label_titulo_card, label_desc_card]:
        widget.bind("<Button-1>", on_card_click)

def click_card(titulo_card: str, frame_dashboard: ctk.CTkFrame) -> None:
    print(f"Card clicado: {titulo_card}")

def click_config(titulo_card: str) -> None:
    print(f"Configurações do card clicadas: {titulo_card}")

def click_perfil():
    print("Perfil clicado")

def criar_quadro(frame_dashboard: ctk.CTkFrame) -> None:
    nome_novo_quadro = f"Novo Quadro {len(cards) + 1}"
    cards.append(nome_novo_quadro)
    add_card(frame_dashboard, nome_novo_quadro)
    