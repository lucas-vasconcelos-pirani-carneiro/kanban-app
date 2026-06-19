import customtkinter as ctk
import tkinter as tk

# Dicionário para os dados das swimlanes
swimlanes_data = {}
dragging_card = None  # Guarda o card atualmente sendo arrastado
drag_ghost = None      # Janela que segue o cursor durante o drag
pending_drag = None    # Armazena o último card clicado antes de decidir iniciar o drag

CARD_PRIORITY_OPTIONS = ["Baixa", "Média", "Alta", "Urgente"]

def _normalize_swimlane_title(swimlane_title: str) -> str:
    return swimlane_title.strip()

def _parse_swimlane_limit(raw_value: str):
    value = raw_value.strip()
    if value == "":
        return None

    try:
        parsed_value = int(value)
    except ValueError:
        return None

    if parsed_value < 0:
        return None

    return parsed_value

def _swimlane_has_capacity(swimlane_title: str) -> bool:
    data = swimlanes_data.get(swimlane_title)
    if not data:
        return False

    card_limit = data.get("card_limit")
    if card_limit is None:
        return True

    return len(data["cards"]) < card_limit


def _format_swimlane_card_count(swimlane_title: str) -> str:
    data = swimlanes_data.get(swimlane_title)
    if not data:
        return "0"

    current_count = len(data["cards"])
    card_limit = data.get("card_limit")
    if card_limit is None:
        return str(current_count)

    return f"{current_count}/{card_limit}"

def _refresh_swimlane_card_count(swimlane_title: str) -> None:
    data = swimlanes_data.get(swimlane_title)
    if not data:
        return

    count_label = data.get("count_label")
    if count_label is not None and count_label.winfo_exists():
        count_label.configure(text=_format_swimlane_card_count(swimlane_title))


def _refresh_swimlane_commands(swimlane_title: str) -> None:
    data = swimlanes_data.get(swimlane_title)
    if not data:
        return

    data["add_button"].configure(command=lambda title=swimlane_title: add_card_to_swimlane(title))
    data["config_button"].configure(command=lambda title=swimlane_title: click_config_swimlane(title))


def _refresh_card_swimlane_references(swimlane_title: str) -> None:
    data = swimlanes_data.get(swimlane_title)
    if not data:
        return

    content_frame = data["content_frame"]
    for card_frame in content_frame.winfo_children():
        if hasattr(card_frame, "swimlane_title"):
            card_frame.swimlane_title = swimlane_title

        for child in card_frame.winfo_children():
            if hasattr(child, "swimlane_title"):
                child.swimlane_title = swimlane_title


def rename_swimlane(old_title: str, new_title: str) -> bool:
    global swimlanes_data

    normalized_old_title = _normalize_swimlane_title(old_title)
    normalized_new_title = _normalize_swimlane_title(new_title)

    if normalized_old_title not in swimlanes_data:
        return False

    if not normalized_new_title:
        return False

    if normalized_new_title != normalized_old_title and normalized_new_title in swimlanes_data:
        return False

    data = swimlanes_data.pop(normalized_old_title)
    swimlanes_data[normalized_new_title] = data
    data["title"] = normalized_new_title
    data["title_label"].configure(text=normalized_new_title)

    _refresh_swimlane_commands(normalized_new_title)
    _refresh_card_swimlane_references(normalized_new_title)

    return True


def delete_swimlane(swimlane_title: str) -> bool:
    global swimlanes_data

    normalized_title = _normalize_swimlane_title(swimlane_title)
    data = swimlanes_data.pop(normalized_title, None)
    if not data:
        return False

    wrapper = data.get("frame")
    if wrapper is not None and wrapper.winfo_exists():
        wrapper.destroy()

    return True


def populate_board_screen(frame_board: ctk.CTkFrame, show_frame, main_frame, board_name: str = "Board") -> None:

    global swimlanes_data
    swimlanes_data = {}

    # Frame do cabeçalho
    frame_header = ctk.CTkFrame(frame_board, fg_color="transparent")
    frame_header.pack(side="top", fill="x", padx=20, pady=20)
    frame_header.grid_columnconfigure(1, weight=1)

    # Botão voltar
    botao_voltar = ctk.CTkButton(
        frame_header,
        text="←",
        width=50,
        height=50,
        corner_radius=25,
        font=("Arial", 24),
        command=lambda: click_voltar(show_frame, main_frame)
    )
    botao_voltar.grid(row=0, column=0, sticky="w", padx=(0, 10))

    # Label com o nome do board
    label_board_name = ctk.CTkLabel(
        frame_header,
        text=board_name,
        font=("Arial", 24, "bold")
    )
    label_board_name.grid(row=0, column=1, sticky="w")

    # Botão de perfil
    botao_perfil = ctk.CTkButton(
        frame_header,
        text="👤",
        width=50,
        height=50,
        corner_radius=25,
        font=("Arial", 24),
        command=lambda: click_perfil(botao_perfil, show_frame)
    )
    botao_perfil.grid(row=0, column=2, sticky="e", padx=(10, 0))

    # linha separadora
    linha = ctk.CTkFrame(frame_board, height=2, fg_color="#cccccc")
    linha.pack(side="top", fill="x", padx=20)

    # Frame com conteúdo para as swimlanes
    frame_conteudo = ctk.CTkFrame(frame_board, fg_color="transparent")
    frame_conteudo.pack(side="top", fill="both", expand=True, padx=20, pady=20)

    # Frame Scrollavel para as swimlanes
    frame_swimlanes_container = ctk.CTkScrollableFrame(
        frame_conteudo,
        fg_color="transparent",
        label_text="",
        orientation="horizontal",
    )
    frame_swimlanes_container.pack(fill="both", expand=True)

    # Guarda referências para acesso futuro
    frame_board.swimlanes_container = frame_swimlanes_container
    frame_board.show_frame = show_frame
    frame_board.main_frame = main_frame
    frame_board.board_name = board_name

    # Adiciona 3 swimlanes padrões
    add_swimlane(frame_board, "To Do")
    add_swimlane(frame_board, "In Progress")
    add_swimlane(frame_board, "Done")


def add_swimlane(frame_board: ctk.CTkFrame, swimlane_title: str) -> None:
    global swimlanes_data

    container = frame_board.swimlanes_container

    # Coluna vertical
    frame_swimlane_wrapper = ctk.CTkFrame(
        container,
        fg_color="transparent"
    )
    frame_swimlane_wrapper.pack(side="left", fill="both", expand=False, padx=10)

    # Inicializa dados da swimlane
    swimlanes_data[swimlane_title] = {
        "title": swimlane_title,
        "cards": [],
        "card_limit": None,
        "frame": frame_swimlane_wrapper,
        "count_label": None,
    }

    # Header da swimlane com título, configuração e botão de adição
    frame_swimlane_header = ctk.CTkFrame(
        frame_swimlane_wrapper,
        fg_color="#f0f0f0",
        corner_radius=8,
        width=280
    )
    frame_swimlane_header.pack(fill="x", padx=0, pady=(0, 10))
    frame_swimlane_header.pack_propagate(False)
    frame_swimlane_header.grid_columnconfigure(0, weight=1)

    # Label do título da swimlane
    label_swimlane_title = ctk.CTkLabel(
        frame_swimlane_header,
        text=swimlane_title,
        font=("Arial", 14, "bold"),
        text_color="#333333"
    )
    label_swimlane_title.grid(row=0, column=0, sticky="w", padx=15, pady=10)

    # Label com a contagem de cartões
    label_card_count = ctk.CTkLabel(
        frame_swimlane_header,
        text=_format_swimlane_card_count(swimlane_title),
        font=("Arial", 12, "bold"),
        text_color="#666666"
    )
    label_card_count.grid(row=0, column=1, sticky="e", padx=(0, 8), pady=10)

    swimlanes_data[swimlane_title]["count_label"] = label_card_count

    # Botão de adicionar cartão
    botao_add_card = ctk.CTkButton(
        frame_swimlane_header,
        text="+",
        width=40,
        height=40,
        font=("Arial", 18),
        fg_color="transparent",
        text_color="#666666",
        hover_color="#e0e0e0",
        command=lambda: add_card_to_swimlane(swimlane_title)
    )
    botao_add_card.grid(row=0, column=2, sticky="e", padx=(5, 5), pady=10)

    # Botão de configuração
    botao_config_swimlane = ctk.CTkButton(
        frame_swimlane_header,
        text="⚙️",
        width=40,
        height=40,
        font=("Arial", 16),
        fg_color="transparent",
        text_color="#666666",
        hover_color="#e0e0e0",
        command=lambda: click_config_swimlane(swimlane_title)
    )
    botao_config_swimlane.grid(row=0, column=3, sticky="e", padx=(5, 10), pady=10)

    # Área de conteúdo da swimlane
    frame_swimlane_content = ctk.CTkScrollableFrame(
        frame_swimlane_wrapper,
        fg_color="#ffffff",
        corner_radius=8,
        border_width=1,
        border_color="#e0e0e0",
        width=280,
        height=400,
        label_text="",
    )
    frame_swimlane_content.pack(fill="both", expand=True, padx=0, pady=(0, 0))

    # Armazena referências
    swimlanes_data[swimlane_title]["content_frame"] = frame_swimlane_content
    swimlanes_data[swimlane_title]["header_frame"] = frame_swimlane_header
    swimlanes_data[swimlane_title]["title_label"] = label_swimlane_title
    swimlanes_data[swimlane_title]["add_button"] = botao_add_card
    swimlanes_data[swimlane_title]["config_button"] = botao_config_swimlane

    label_placeholder = ctk.CTkLabel(
        frame_swimlane_content,
        text="Arraste cartões aqui",
        font=("Arial", 12),
        text_color="#999999"
    )
    label_placeholder.pack(expand=True)
    swimlanes_data[swimlane_title]["placeholder"] = label_placeholder


def add_card_to_swimlane(swimlane_title: str) -> None:
    global swimlanes_data

    if swimlane_title not in swimlanes_data:
        return

    if not _swimlane_has_capacity(swimlane_title):
        print(f"Swimlane '{swimlane_title}' Chegou ao limite de cards")
        return

    content_frame = swimlanes_data[swimlane_title]["content_frame"]
    placeholder = swimlanes_data[swimlane_title]["placeholder"]

    # Esconde placeholder
    if placeholder.winfo_exists():
        placeholder.pack_forget()

    # Cria nova carta
    card_title = f"Card {len(swimlanes_data[swimlane_title]['cards']) + 1}"
    card_data = {
        "title": card_title,
        "priority": "baixa",
        "due_date": "",
        "responsible": "",
    }
    create_card_widget(swimlane_title, card_data, content_frame)

    swimlanes_data[swimlane_title]["cards"].append(card_data)
    _refresh_swimlane_card_count(swimlane_title)


def _card_display_value(value: str) -> str:
    return value.strip() if value.strip() else "-"


def _refresh_card_widget(card_frame) -> None:
    card_data = card_frame.card_data
    card_frame.title_label.configure(text=card_data["title"])
    card_frame.priority_value_label.configure(text=card_data["priority"])
    card_frame.due_date_value_label.configure(text=_card_display_value(card_data["due_date"]))
    card_frame.responsible_value_label.configure(text=_card_display_value(card_data["responsible"]))


def _show_card_menu(event, card_frame) -> None:
    menu = tk.Menu(card_frame, tearoff=0)
    menu.add_command(label="Editar cartão", command=lambda: open_card_editor(card_frame))
    menu.add_separator()
    menu.add_command(label="Cancelar")

    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()


def create_card_widget(swimlane_title: str, card_data: dict, parent_frame: ctk.CTkFrame) -> None:
    frame_card = tk.Frame(
        parent_frame,
        bg="#f9f9f9",
        height=130,
        relief="solid",
        borderwidth=1
    )
    frame_card.pack(fill="x", padx=10, pady=8)
    frame_card.pack_propagate(False)

    frame_card.card_data = card_data
    frame_card.swimlane_title = swimlane_title

    content_frame = tk.Frame(frame_card, bg="#f9f9f9")
    content_frame.pack(fill="both", expand=True, padx=10, pady=8)

    title_label = tk.Label(
        content_frame,
        text=card_data["title"],
        font=("Arial", 12, "bold"),
        fg="#333333",
        bg="#f9f9f9",
        anchor="w",
        cursor="hand2"
    )
    title_label.pack(anchor="w", fill="x")

    priority_row = tk.Frame(content_frame, bg="#f9f9f9")
    priority_row.pack(anchor="w", fill="x", pady=(6, 0))
    priority_label = tk.Label(
        priority_row,
        text="Prioridade:",
        font=("Arial", 10, "bold"),
        fg="#666666",
        bg="#f9f9f9",
    )
    priority_label.pack(side="left")
    priority_value_label = tk.Label(
        priority_row,
        text=card_data["priority"],
        font=("Arial", 10),
        fg="#333333",
        bg="#f9f9f9",
    )
    priority_value_label.pack(side="left", padx=(4, 0))

    due_date_row = tk.Frame(content_frame, bg="#f9f9f9")
    due_date_row.pack(anchor="w", fill="x", pady=(3, 0))
    due_date_label = tk.Label(
        due_date_row,
        text="Prazo máximo:",
        font=("Arial", 10, "bold"),
        fg="#666666",
        bg="#f9f9f9",
    )
    due_date_label.pack(side="left")
    due_date_value_label = tk.Label(
        due_date_row,
        text=_card_display_value(card_data["due_date"]),
        font=("Arial", 10),
        fg="#333333",
        bg="#f9f9f9",
    )
    due_date_value_label.pack(side="left", padx=(4, 0))

    responsible_row = tk.Frame(content_frame, bg="#f9f9f9")
    responsible_row.pack(anchor="w", fill="x", pady=(3, 0))
    responsible_label = tk.Label(
        responsible_row,
        text="Responsável:",
        font=("Arial", 10, "bold"),
        fg="#666666",
        bg="#f9f9f9",
    )
    responsible_label.pack(side="left")
    responsible_value_label = tk.Label(
        responsible_row,
        text=_card_display_value(card_data["responsible"]),
        font=("Arial", 10),
        fg="#333333",
        bg="#f9f9f9",
    )
    responsible_value_label.pack(side="left", padx=(4, 0))

    frame_card.title_label = title_label
    frame_card.priority_value_label = priority_value_label
    frame_card.due_date_value_label = due_date_value_label
    frame_card.responsible_value_label = responsible_value_label

    for widget in (
        frame_card,
        content_frame,
        title_label,
        priority_row,
        priority_label,
        priority_value_label,
        due_date_row,
        due_date_label,
        due_date_value_label,
        responsible_row,
        responsible_label,
        responsible_value_label,
    ):
        widget.bind("<Button-1>", lambda e, f=frame_card: start_drag(e, f), add=True)
        widget.bind("<B1-Motion>", lambda e, f=frame_card: drag_card(e, f), add=True)
        widget.bind("<ButtonRelease-1>", lambda e, f=frame_card: end_drag(e, f), add=True)

    _refresh_card_widget(frame_card)


def open_card_editor(card_frame) -> None:
    card_data = card_frame.card_data

    modal = ctk.CTkToplevel()
    modal.title("Editar cartão")
    modal.resizable(False, False)
    modal.transient(card_frame.winfo_toplevel())
    modal.grab_set()
    modal.geometry("420x340")

    container = ctk.CTkFrame(modal, corner_radius=16)
    container.pack(fill="both", expand=True, padx=16, pady=16)
    container.grid_columnconfigure(1, weight=1)

    label_title = ctk.CTkLabel(
        container,
        text="Editar informações do cartão",
        font=("Arial", 18, "bold"),
    )
    label_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(16, 12))

    label_name = ctk.CTkLabel(container, text="Nome do cartão")
    label_name.grid(row=1, column=0, sticky="w", padx=16, pady=(6, 4))
    entry_name = ctk.CTkEntry(container)
    entry_name.grid(row=1, column=1, sticky="ew", padx=16, pady=(6, 4))
    entry_name.insert(0, card_data["title"])

    label_priority = ctk.CTkLabel(container, text="Prioridade")
    label_priority.grid(row=2, column=0, sticky="w", padx=16, pady=(6, 4))
    priority_var = tk.StringVar(value=card_data["priority"])
    priority_menu = ctk.CTkOptionMenu(
        container,
        variable=priority_var,
        values=CARD_PRIORITY_OPTIONS,
    )
    priority_menu.grid(row=2, column=1, sticky="ew", padx=16, pady=(6, 4))

    label_due_date = ctk.CTkLabel(container, text="Prazo máximo")
    label_due_date.grid(row=3, column=0, sticky="w", padx=16, pady=(6, 4))
    entry_due_date = ctk.CTkEntry(container)
    entry_due_date.grid(row=3, column=1, sticky="ew", padx=16, pady=(6, 4))
    entry_due_date.insert(0, card_data["due_date"])

    label_responsible = ctk.CTkLabel(container, text="Responsável")
    label_responsible.grid(row=4, column=0, sticky="w", padx=16, pady=(6, 4))
    entry_responsible = ctk.CTkEntry(container)
    entry_responsible.grid(row=4, column=1, sticky="ew", padx=16, pady=(6, 4))
    entry_responsible.insert(0, card_data["responsible"])

    status_label = ctk.CTkLabel(container, text="", text_color="#c0392b")
    status_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=16, pady=(8, 0))

    button_row = ctk.CTkFrame(container, fg_color="transparent")
    button_row.grid(row=6, column=0, columnspan=2, sticky="ew", padx=16, pady=(16, 16))
    button_row.grid_columnconfigure(0, weight=1)

    def close_modal() -> None:
        if modal.winfo_exists():
            modal.grab_release()
            modal.destroy()

    def save_changes() -> None:
        new_title = entry_name.get().strip()
        new_priority = priority_var.get().strip()
        new_due_date = entry_due_date.get().strip()
        new_responsible = entry_responsible.get().strip()

        if not new_title:
            status_label.configure(text="O nome do cartão não pode ficar vazio.")
            return

        if new_priority not in CARD_PRIORITY_OPTIONS:
            status_label.configure(text="Escolha uma prioridade válida.")
            return

        card_data["title"] = new_title
        card_data["priority"] = new_priority
        card_data["due_date"] = new_due_date
        card_data["responsible"] = new_responsible
        _refresh_card_widget(card_frame)
        close_modal()

    def delete_this_card() -> None:
        close_modal()
        delete_card(card_frame)

    botao_salvar = ctk.CTkButton(
        button_row,
        text="Salvar",
        width=100,
        command=save_changes,
    )
    botao_salvar.grid(row=0, column=0, sticky="w")

    botao_excluir = ctk.CTkButton(
        button_row,
        text="Excluir cartão",
        width=120,
        fg_color="#b33a3a",
        hover_color="#922f2f",
        command=delete_this_card,
    )
    botao_excluir.grid(row=0, column=1, padx=10)

    botao_cancelar = ctk.CTkButton(
        button_row,
        text="Cancelar",
        width=100,
        fg_color="#666666",
        hover_color="#555555",
        command=close_modal,
    )
    botao_cancelar.grid(row=0, column=2, sticky="e")

    modal.protocol("WM_DELETE_WINDOW", close_modal)
    modal.focus_force()


def delete_card(card_frame) -> None:
    global swimlanes_data

    swimlane_title = getattr(card_frame, "swimlane_title", None)
    card_data = getattr(card_frame, "card_data", None)

    if swimlane_title in swimlanes_data and card_data in swimlanes_data[swimlane_title]["cards"]:
        swimlanes_data[swimlane_title]["cards"].remove(card_data)
        if len(swimlanes_data[swimlane_title]["cards"]) == 0:
            placeholder = swimlanes_data[swimlane_title]["placeholder"]
            if placeholder.winfo_exists():
                placeholder.pack(expand=True)
        _refresh_swimlane_card_count(swimlane_title)

    if card_frame.winfo_exists():
        card_frame.destroy()

    print(f"Card apagado de '{swimlane_title}'")


def start_drag(event, card_frame) -> None:
    global pending_drag

    pending_drag = {
        "card": card_frame,
        "start_x": event.x_root,
        "start_y": event.y_root,
        "moved": False,
    }


def _begin_drag(event, card_frame) -> None:
    global dragging_card, drag_ghost

    if dragging_card is not None:
        return

    dragging_card = {
        "card": card_frame,
        "data": card_frame.card_data,
        "original_swimlane": card_frame.swimlane_title,
    }

    # Janela flutuante que segue o mouse durante o arrasto
    drag_ghost = tk.Toplevel()
    drag_ghost.overrideredirect(True)
    drag_ghost.attributes("-topmost", True)
    try:
        drag_ghost.attributes("-alpha", 0.85)
    except tk.TclError:
        pass

    ghost_label = tk.Label(
        drag_ghost,
        text=card_frame.card_data["title"],
        font=("Arial", 12, "bold"),
        fg="#333333",
        bg="#d0d0d0",
        relief="solid",
        borderwidth=1,
        width=20,
        height=3,
    )
    ghost_label.pack()

    drag_ghost.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

    card_frame.configure(bg="#e8e8e8")
    print(f"Começou a arrastar: {card_frame.card_data['title']}")


def drag_card(event, card_frame) -> None:
    global pending_drag

    if pending_drag is not None and pending_drag["card"] == card_frame and dragging_card is None:
        delta_x = abs(event.x_root - pending_drag["start_x"])
        delta_y = abs(event.y_root - pending_drag["start_y"])
        if delta_x >= 4 or delta_y >= 4:
            pending_drag["moved"] = True
            _begin_drag(event, card_frame)

    if dragging_card is None or dragging_card["card"] != card_frame:
        return
    if drag_ghost is not None and drag_ghost.winfo_exists():
        drag_ghost.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")


def end_drag(event, card_frame) -> None:
    global dragging_card, drag_ghost, swimlanes_data, pending_drag

    if dragging_card is None or dragging_card["card"] != card_frame:
        if pending_drag is not None and pending_drag["card"] == card_frame and not pending_drag["moved"]:
            _show_card_menu(event, card_frame)
        pending_drag = None
        return

    if drag_ghost is not None and drag_ghost.winfo_exists():
        drag_ghost.destroy()
    drag_ghost = None

    card_frame.configure(bg="#f9f9f9")

    cursor_x = event.x_root
    cursor_y = event.y_root

    # Encontra a swimlane alvo sob o cursor
    target_swimlane = None
    for swimlane_title, data in swimlanes_data.items():
        column_frame = data["frame"]
        if not column_frame.winfo_exists():
            continue

        frame_x = column_frame.winfo_rootx()
        frame_y = column_frame.winfo_rooty()
        frame_width = column_frame.winfo_width()
        frame_height = column_frame.winfo_height()

        if (frame_x <= cursor_x <= frame_x + frame_width and
                frame_y <= cursor_y <= frame_y + frame_height):
            target_swimlane = swimlane_title
            break

    original_swimlane = dragging_card["original_swimlane"]

    if target_swimlane and target_swimlane != original_swimlane:
        move_card_to_swimlane(card_frame, original_swimlane, target_swimlane)
        print(f"Deixada em: {target_swimlane}")
    else:
        print(f"Card ficou em: {original_swimlane}")

    dragging_card = None
    pending_drag = None


def move_card_to_swimlane(card_frame, from_swimlane: str, to_swimlane: str) -> None:
    global swimlanes_data

    card_data = card_frame.card_data

    if to_swimlane not in swimlanes_data:
        return

    if not _swimlane_has_capacity(to_swimlane):
        print(f"Swimlane '{to_swimlane}' chegou ao limite de cards")
        return

    # Remove da swimlane original
    if from_swimlane in swimlanes_data and card_data in swimlanes_data[from_swimlane]["cards"]:
        swimlanes_data[from_swimlane]["cards"].remove(card_data)
        if len(swimlanes_data[from_swimlane]["cards"]) == 0:
            placeholder = swimlanes_data[from_swimlane]["placeholder"]
            if placeholder.winfo_exists():
                placeholder.pack(expand=True)

    card_frame.destroy()

    target_content_frame = swimlanes_data[to_swimlane]["content_frame"]

    placeholder = swimlanes_data[to_swimlane]["placeholder"]
    if placeholder.winfo_exists():
        placeholder.pack_forget()
    swimlanes_data[to_swimlane]["cards"].append(card_data)
    _refresh_swimlane_card_count(from_swimlane)
    _refresh_swimlane_card_count(to_swimlane)

    create_card_widget(to_swimlane, card_data, target_content_frame)

    print(f"Card '{card_data['title']}' movido de '{from_swimlane}' para '{to_swimlane}'")


def click_voltar(show_frame, main_frame) -> None:
    show_frame("dashboard")


def click_config_swimlane(swimlane_title: str) -> None:
    global swimlanes_data

    if swimlane_title not in swimlanes_data:
        return

    data = swimlanes_data[swimlane_title]

    modal = ctk.CTkToplevel()
    modal.title(f"Configurar {swimlane_title}")
    modal.resizable(False, False)
    modal.transient(data["frame"].winfo_toplevel())
    modal.grab_set()

    modal.geometry("380x280")

    container = ctk.CTkFrame(modal, corner_radius=16)
    container.pack(fill="both", expand=True, padx=16, pady=16)
    container.grid_columnconfigure(1, weight=1)

    label_title = ctk.CTkLabel(
        container,
        text="Configurações da coluna",
        font=("Arial", 18, "bold"),
    )
    label_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(16, 10))

    label_name = ctk.CTkLabel(container, text="Nome da coluna")
    label_name.grid(row=1, column=0, sticky="w", padx=16, pady=(10, 4))
    entry_name = ctk.CTkEntry(container)
    entry_name.grid(row=1, column=1, sticky="ew", padx=16, pady=(10, 4))
    entry_name.insert(0, swimlane_title)

    label_limit = ctk.CTkLabel(container, text="Limite de cartões")
    label_limit.grid(row=2, column=0, sticky="w", padx=16, pady=(10, 4))
    entry_limit = ctk.CTkEntry(container)
    entry_limit.grid(row=2, column=1, sticky="ew", padx=16, pady=(10, 4))
    current_limit = data.get("card_limit")
    entry_limit.insert(0, "" if current_limit is None else str(current_limit))

    label_hint = ctk.CTkLabel(
        container,
        text="Deixe em branco para não limitar cartões.",
        font=("Arial", 12),
        text_color="#666666",
    )
    label_hint.grid(row=3, column=0, columnspan=2, sticky="w", padx=16, pady=(4, 8))

    status_label = ctk.CTkLabel(container, text="", text_color="#c0392b")
    status_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=16, pady=(0, 8))

    button_row = ctk.CTkFrame(container, fg_color="transparent")
    button_row.grid(row=5, column=0, columnspan=2, sticky="ew", padx=16, pady=(10, 16))
    button_row.grid_columnconfigure(0, weight=1)

    def close_modal() -> None:
        if modal.winfo_exists():
            modal.grab_release()
            modal.destroy()

    def save_changes() -> None:
        new_title = entry_name.get().strip()
        limit_value = _parse_swimlane_limit(entry_limit.get())

        if not new_title:
            status_label.configure(text="O nome da coluna não pode ficar vazio.")
            return

        if limit_value is None and entry_limit.get().strip() != "":
            status_label.configure(text="Use um número inteiro maior ou igual a zero no limite.")
            return

        if new_title != swimlane_title and new_title in swimlanes_data:
            status_label.configure(text="Já existe uma coluna com esse nome.")
            return

        if new_title != swimlane_title:
            if not rename_swimlane(swimlane_title, new_title):
                status_label.configure(text="Não foi possível renomear a coluna.")
                return

        target_title = new_title
        swimlanes_data[target_title]["card_limit"] = limit_value
        _refresh_swimlane_card_count(target_title)
        close_modal()

    def delete_current_swimlane() -> None:
        close_modal()
        delete_swimlane(swimlane_title)

    botao_salvar = ctk.CTkButton(
        button_row,
        text="Salvar",
        width=100,
        command=save_changes,
    )
    botao_salvar.grid(row=0, column=0, sticky="w")

    botao_excluir = ctk.CTkButton(
        button_row,
        text="Excluir coluna",
        width=120,
        fg_color="#b33a3a",
        hover_color="#922f2f",
        command=delete_current_swimlane,
    )
    botao_excluir.grid(row=0, column=1, padx=10)

    botao_cancelar = ctk.CTkButton(
        button_row,
        text="Cancelar",
        width=100,
        fg_color="#666666",
        hover_color="#555555",
        command=close_modal,
    )
    botao_cancelar.grid(row=0, column=2, sticky="e")

    modal.protocol("WM_DELETE_WINDOW", close_modal)
    modal.focus_force()


def click_perfil(profile_button, show_frame) -> None:
    menu = tk.Menu(profile_button, tearoff=0)
    menu.add_command(label="Sair", command=lambda: show_frame("main"))

    try:
        menu.tk_popup(
            profile_button.winfo_rootx(),
            profile_button.winfo_rooty() + profile_button.winfo_height(),
        )
    finally:
        menu.grab_release()