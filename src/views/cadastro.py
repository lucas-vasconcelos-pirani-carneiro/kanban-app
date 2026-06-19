import customtkinter as ctk
from src.repositories.usuario_repository import UsuarioRepository
from src.services.usuario_service import UsuarioService

repository = UsuarioRepository()
service = UsuarioService(repository)

def populate_register_screen(frame_cadastro: ctk.CTkFrame, show_frame, main_frame) -> None:
    frame_cadastro.grid_columnconfigure(0, weight=1)

    label_cadastro = ctk.CTkLabel(
        frame_cadastro,
        text="Cadastro",
        font=ctk.CTkFont(size=24, weight="bold"),
    )
    label_cadastro.grid(row=0, column=0, pady=(28, 20), padx=18, sticky="ew")

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
    campo_senha.grid(row=6, column=0, padx=18, pady=(0, 12), sticky="ew")

    label_erro = ctk.CTkLabel(
        frame_cadastro,
        text="",
        font=ctk.CTkFont(size=11),
        text_color="#FF5555",
    )
    label_erro.grid(row=7, column=0, padx=18, pady=(0, 6))

    label_sucesso = ctk.CTkLabel(
        frame_cadastro,
        text="",
        font=ctk.CTkFont(size=11),
        text_color="#55FF55",
    )
    label_sucesso.grid(row=8, column=0, padx=18, pady=(0, 6))

    def realizar_cadastro():
        email = campo_email.get().strip()
        nome = campo_usuario.get().strip()
        senha = campo_senha.get()
        label_erro.configure(text="")
        label_sucesso.configure(text="")

        try:
            service.criar_usuario(nome=nome, email=email, senha_texto_puro=senha)
            campo_email.delete(0, "end")
            campo_usuario.delete(0, "end")
            campo_senha.delete(0, "end")
            label_sucesso.configure(text="Cadastro realizado com sucesso!")
            frame_cadastro.after(2000, lambda: show_frame(main_frame))
        except ValueError as e:
            label_erro.configure(text=str(e))

    botao_confirma = ctk.CTkButton(
        frame_cadastro,
        text="Confirmar",
        width=150,
        height=42,
        fg_color="#7B4DFF",
        hover_color="#6738E6",
        text_color="#FFFFFF",
        command=realizar_cadastro,
    )
    botao_confirma.grid(row=9, column=0, pady=(0, 12))

    botao_voltar = ctk.CTkButton(
        frame_cadastro,
        text="Voltar",
        width=150,
        height=42,
        fg_color="#7B4DFF",
        hover_color="#6738E6",
        command=lambda: show_frame(main_frame),
    )
    botao_voltar.grid(row=10, column=0, pady=(0, 28))
