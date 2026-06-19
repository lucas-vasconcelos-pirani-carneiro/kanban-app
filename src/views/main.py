import customtkinter as ctk

def populate_main_screen(main_frame: ctk.CTkFrame, show_frame, login_frame, register_frame) -> None:
    main_frame.grid_rowconfigure(3, weight=1)

    label_titulo = ctk.CTkLabel(
        main_frame,
        text="KanbanApp",
        font=ctk.CTkFont(size=24, weight="bold"),
        anchor="center",
    )
    label_titulo.grid(row=0, column=0, pady=(28, 10), sticky="ew")

    label_bem_vindo = ctk.CTkLabel(
        main_frame,
        text="Bem-vindo! Escolha uma opção para continuar.",
        font=ctk.CTkFont(size=14),
        text_color="#D0D0D0",
        anchor="center",
    )
    label_bem_vindo.grid(row=1, column=0, pady=(0, 28), padx=18, sticky="ew")

    frame_botoes = ctk.CTkFrame(main_frame, fg_color="transparent")
    frame_botoes.grid(row=2, column=0, pady=(0, 24))

    botao_cadastro = ctk.CTkButton(
        frame_botoes,
        text="Cadastrar",
        width=180,
        height=50,
        fg_color="#7B4DFF",
        hover_color="#6738E6",
        text_color="#FFFFFF",
        command=lambda: show_frame(register_frame),
    )
    botao_cadastro.grid(row=0, column=0, padx=(0, 12))

    botao_login = ctk.CTkButton(
        frame_botoes,
        text="Entrar",
        width=180,
        height=50,
        fg_color="#7B4DFF",
        hover_color="#6738E6",
        text_color="#FFFFFF",
        command=lambda: show_frame(login_frame),
    )
    botao_login.grid(row=0, column=1, padx=(12, 0))

