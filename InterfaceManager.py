import customtkinter as ctk
from telas.main import populate_main_screen
from telas.login import populate_register_screen
from telas.cadastro import populate_login_screen

def show_frame(frame: ctk.CTkFrame) -> None:
    frame.tkraise()

def create_app() -> ctk.CTk:
    app = ctk.CTk()
    app.title("Kanban App")
    app.geometry("800x600")
    #app.resizable(False, False)

    # Seção para fazer o aplicativo aparecer no meio da tela
    largura_tela = app.winfo_screenwidth()
    altura_tela = app.winfo_screenheight()

    pos_x = int((largura_tela / 2) - (800 / 2))
    pos_y = int((altura_tela / 2) - (600 / 2))

    # Define a geometria da janela com o tamanho e a posição calculada
    app.geometry(f"{800}x{600}+{pos_x}+{pos_y}")

    app.grid_columnconfigure(0, weight=1)
    app.grid_rowconfigure(0, weight=1)

    # Cria os frames vazios
    main_frame = ctk.CTkFrame(app, corner_radius=18)
    frame_cadastro = ctk.CTkFrame(app, corner_radius=18)
    frame_login = ctk.CTkFrame(app, corner_radius=18)

    # Configura os frames
    for frame in (main_frame, frame_cadastro, frame_login):
        frame.grid(row=0, column=0, padx=24, pady=24, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

    # Preenche os frames com componentes da interface
    populate_main_screen(main_frame, show_frame, frame_cadastro, frame_login)
    populate_register_screen(frame_cadastro, show_frame, main_frame)
    populate_login_screen(frame_login, show_frame, main_frame)

    show_frame(main_frame)

    return app


if __name__ == "__main__":
    app = create_app()
    app.mainloop()