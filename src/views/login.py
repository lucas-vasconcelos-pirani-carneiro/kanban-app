import customtkinter as ctk

def populate_login_screen(frame_login: ctk.CTkFrame, show_frame, main_frame, frame_dashboard) -> None:
    #frame_login.grid_rowconfigure(3, weight=1)

    label_login = ctk.CTkLabel(
        frame_login,
        text="Login",
        font=ctk.CTkFont(size=24, weight="bold"),
    )
    label_login.grid(row=0, column=0, pady=(12, 8), padx=18, sticky="ew")

    # Label do e-mail e campo de entrada
    label_email = ctk.CTkLabel(
        frame_login,
        text="Email",
        font=ctk.CTkFont(size=12),
        text_color="#D0D0D0",
    )
    label_email.grid(row=1, column=0, padx=18, pady=(0, 2), sticky="w")

    campo_email = ctk.CTkEntry(
        frame_login,
        placeholder_text="Digite seu email",
        width=300,
        height=35,
    )
    campo_email.grid(row=2, column=0, padx=18, pady=(0, 8), sticky="ew")
    #email = campo_email.get()

    # Label da senha e campo de entrada
    label_senha = ctk.CTkLabel(
        frame_login,
        text="Senha",
        font=ctk.CTkFont(size=12),
        text_color="#D0D0D0",
    )
    label_senha.grid(row=5, column=0, padx=18, pady=(0, 2), sticky="w")

    campo_senha = ctk.CTkEntry(
        frame_login,
        placeholder_text="Digite sua senha",
        width=300,
        height=35,
        show="•",
    )
    campo_senha.grid(row=6, column=0, padx=18, pady=(0, 10), sticky="ew")
    #senha = campo_senha.get()

    # Botão de confirmação
    botao_confirma = ctk.CTkButton(
        frame_login,
        text="Confirmar",
        width=150,
        height=42,
        fg_color="#7B4DFF",
        hover_color="#6738E6",
        text_color="#FFFFFF",
        command=lambda: show_frame(frame_dashboard),
    )
    botao_confirma.grid(row=7, column=0, pady=(0, 8))

    register_back_button = ctk.CTkButton(
        frame_login,
        text="Voltar",
        width=150,
        height=42,
        fg_color="#7B4DFF",
        hover_color="#6738E6",
        command=lambda: show_frame(main_frame),
    )
    register_back_button.grid(row=8, column=0, pady=(0, 12))

