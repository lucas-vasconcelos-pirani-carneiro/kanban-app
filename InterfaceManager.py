import customtkinter as ctk
from telas.main import populate_main_screen
from telas.cadastro import populate_register_screen
from telas.login import populate_login_screen
from telas.dashboard import populate_dashboard_screen
from telas.quadros import populate_board_screen

# Dicionário global para armazenar referências aos frames
frames_dict = {}

def show_frame(frame_name_or_obj = None, frame: ctk.CTkFrame = None, **kwargs) -> None:
    if isinstance(frame_name_or_obj, str) and frame_name_or_obj in frames_dict:
        target_frame = frames_dict[frame_name_or_obj]
        target_frame.tkraise()
        
        # Se estiver mostrando o frame de board, atualize os dados do quadro
        if frame_name_or_obj == "board" and "board_name" in kwargs:
            for widget in target_frame.winfo_children():
                widget.destroy()
            populate_board_screen(
                target_frame,
                show_frame,
                frames_dict.get("main"),
                kwargs["board_name"]
            )
    # Checa se é um frame diretamente passado como argumento
    elif isinstance(frame_name_or_obj, ctk.CTkFrame):
        frame_name_or_obj.tkraise()
    elif frame is not None and isinstance(frame, ctk.CTkFrame):
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
    frame_dashboard = ctk.CTkFrame(app, corner_radius=18)
    frame_board = ctk.CTkFrame(app, corner_radius=18)

    # Configura os frames
    for frame in (main_frame, frame_cadastro, frame_login, frame_dashboard, frame_board):
        frame.grid(row=0, column=0, padx=24, pady=24, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

    # Armazena os frames em um dicionário global
    frames_dict["main"] = main_frame
    frames_dict["cadastro"] = frame_cadastro
    frames_dict["login"] = frame_login
    frames_dict["dashboard"] = frame_dashboard
    frames_dict["board"] = frame_board

    # Preenche os frames com componentes da interface
    populate_main_screen(main_frame, show_frame, frame_login, frame_cadastro)
    populate_dashboard_screen(frame_dashboard, show_frame, main_frame)
    populate_register_screen(frame_cadastro, show_frame, main_frame)
    populate_login_screen(frame_login, show_frame, main_frame, frame_dashboard)
    populate_board_screen(frame_board, show_frame, main_frame, "Board")

    show_frame("main")

    return app

if __name__ == "__main__":
    app = create_app()
    app.mainloop()