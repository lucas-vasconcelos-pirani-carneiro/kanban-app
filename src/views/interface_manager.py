import customtkinter as ctk
from src.views.main import populate_main_screen
from src.views.cadastro import populate_register_screen
from src.views.login import populate_login_screen
from src.views.dashboard import populate_dashboard_screen, carregar_projetos
from src.views.quadros import populate_quadros_screen
from src.views.kanban import populate_kanban_screen

def create_app() -> ctk.CTk:
    app = ctk.CTk()
    app.title("Kanban App")
    app.geometry("1100x700")

    largura_tela = app.winfo_screenwidth()
    altura_tela = app.winfo_screenheight()
    pos_x = int((largura_tela / 2) - (1100 / 2))
    pos_y = int((altura_tela / 2) - (700 / 2))
    app.geometry(f"1100x700+{pos_x}+{pos_y}")

    app.grid_columnconfigure(0, weight=1)
    app.grid_rowconfigure(0, weight=1)

    main_frame     = ctk.CTkFrame(app, corner_radius=18)
    frame_cadastro = ctk.CTkFrame(app, corner_radius=18)
    frame_login    = ctk.CTkFrame(app, corner_radius=18)
    frame_dashboard = ctk.CTkFrame(app, corner_radius=18)
    frame_quadros  = ctk.CTkFrame(app, corner_radius=18)
    frame_kanban   = ctk.CTkFrame(app, corner_radius=18)

    for frame in (main_frame, frame_cadastro, frame_login,
                  frame_dashboard, frame_quadros, frame_kanban):
        frame.grid(row=0, column=0, padx=24, pady=24, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)

    # Conecta frame_quadros ao frame_kanban para navegação
    frame_quadros.frame_kanban = frame_kanban
    frame_quadros.frame_dashboard = frame_dashboard

    def show_frame(frame: ctk.CTkFrame) -> None:
        frame.tkraise()
        if frame is frame_dashboard:
            carregar_projetos(frame_dashboard)

    populate_main_screen(main_frame, show_frame, frame_login, frame_cadastro)
    populate_dashboard_screen(frame_dashboard, show_frame, main_frame)
    populate_register_screen(frame_cadastro, show_frame, main_frame)
    populate_login_screen(frame_login, show_frame, main_frame, frame_dashboard)
    populate_quadros_screen(frame_quadros, show_frame, frame_dashboard)
    populate_kanban_screen(frame_kanban, show_frame)

    show_frame(main_frame)

    return app

if __name__ == "__main__":
    app = create_app()
    app.mainloop()
