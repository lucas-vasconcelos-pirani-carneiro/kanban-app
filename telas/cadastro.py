import customtkinter as ctk

def populate_login_screen(frame_cadastro: ctk.CTkFrame, show_frame, main_frame) -> None:
    frame_cadastro.grid_rowconfigure(7, weight=1)

    label_cadastro = ctk.CTkLabel(
        frame_cadastro,
        text="Cadastro",
        font=ctk.CTkFont(size=24, weight="bold"),
    )
    label_cadastro.grid(row=0, column=0, pady=(28, 20), padx=18, sticky="ew")

    # Label do e-mail e campo de entrada
    label_email = ctk.CTkLabel(
        frame_cadastro,
        text="Email",
        font=ctk.CTkFont(size=12),
        text_color="#D0D0D0",
    )
    label_email.grid(row=1, column=0, padx=18, pady=(0, 5), sticky="w")

    campo_email = ctk.CTkEntry(
        frame_cadastro,
        placeholder_text="Digite seu email",
        width=300,
        height=35,
    )
    campo_email.grid(row=2, column=0, padx=18, pady=(0, 12), sticky="ew")
    #email = campo_email.get()

    # Label do nome de usuário e campo de entrada
    label_usuario = ctk.CTkLabel(
        frame_cadastro,
        text="Nome de usuário",
        font=ctk.CTkFont(size=12),
        text_color="#D0D0D0",
    )
    label_usuario.grid(row=3, column=0, padx=18, pady=(0, 5), sticky="w")

    campo_usuario = ctk.CTkEntry(
        frame_cadastro,
        placeholder_text="Digite seu nome de usuário",
        width=300,
        height=35,
    )
    campo_usuario.grid(row=4, column=0, padx=18, pady=(0, 12), sticky="ew")
    #usuario = campo_usuario.get()

    # Label da senha e campo de entrada
    label_senha = ctk.CTkLabel(
        frame_cadastro,
        text="Senha",
        font=ctk.CTkFont(size=12),
        text_color="#D0D0D0",
    )
    label_senha.grid(row=5, column=0, padx=18, pady=(0, 5), sticky="w")

    campo_senha = ctk.CTkEntry(
        frame_cadastro,
        placeholder_text="Digite sua senha",
        width=300,
        height=35,
        show="•",
    )
    campo_senha.grid(row=6, column=0, padx=18, pady=(0, 20), sticky="ew")
    #senha = campo_senha.get()

    # Botão de confirmação
    botao_confirma = ctk.CTkButton(
        frame_cadastro,
        text="Confirmar",
        width=150,
        height=42,
        fg_color="#7B4DFF",
        hover_color="#6738E6",
        text_color="#FFFFFF",
    )
    botao_confirma.grid(row=7, column=0, pady=(0, 12))

    # Botão de voltar à tela inicial
    botao_voltar = ctk.CTkButton(
        frame_cadastro,
        text="Voltar",
        width=150,
        height=42,
        fg_color="#7B4DFF",
        hover_color="#6738E6",
        command=lambda: show_frame(main_frame),
    )
    botao_voltar.grid(row=8, column=0, pady=(0, 28))

