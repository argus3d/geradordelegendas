import os
import sys
import threading
import torch
import stable_whisper
import tkinter as tk
from tkinter import filedialog, messagebox

# -------------------------------------------------
# FFmpeg (mesma pasta do exe/script)
# -------------------------------------------------
# Tenta localizar o ffmpeg em múltiplos caminhos possíveis
def _find_ffmpeg():
    candidates = [
        # Pasta do script (desenvolvimento)
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg", "ffmpeg.exe"),
        # Pasta do executável (PyInstaller)
        os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "ffmpeg", "ffmpeg.exe"),
        # Diretório de trabalho atual
        os.path.join(os.getcwd(), "ffmpeg", "ffmpeg.exe"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    # Debug: mostra onde foi procurado
    checked = "\n".join(candidates)
    messagebox.showerror("Erro", f"ffmpeg.exe não encontrado.\n\nProcurado em:\n{checked}")
    sys.exit()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FFMPEG_PATH = _find_ffmpeg()
os.environ["PATH"] = os.path.dirname(FFMPEG_PATH) + os.pathsep + os.environ.get("PATH", "")

# -------------------------------------------------
# PALETA
# -------------------------------------------------
BG       = "#0f0f13"
SURFACE  = "#1a1a22"
BORDER   = "#2a2a38"
ACCENT   = "#6c63ff"
ACCENT2  = "#9d97ff"
TEXT     = "#e8e8f0"
SUBTEXT  = "#888899"
SUCCESS  = "#4ade80"
ERROR    = "#f87171"
WARNING  = "#fbbf24"

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_SUB    = ("Segoe UI", 11)
FONT_LABEL  = ("Segoe UI", 9, "bold")
FONT_VALUE  = ("Segoe UI", 9)
FONT_LOG    = ("Consolas", 9)
FONT_BTN    = ("Segoe UI", 10, "bold")
FONT_SMALL  = ("Segoe UI", 8)

# -------------------------------------------------
def gpu_available():
    return torch.cuda.is_available()

# -------------------------------------------------
def process_video(video_path, model, log):
    try:
        video_path = os.path.abspath(video_path)
        srt_path = os.path.splitext(video_path)[0] + ".srt"
        log(f"▸  {os.path.basename(video_path)}", "info")

        if not os.path.isfile(video_path):
            log(f"   ✗  Arquivo não encontrado: {video_path}", "error")
            return

        result = model.transcribe(video_path, language="pt", verbose=False)
        result.remove_words_by_str(["Music", "Música"])
        result.to_srt_vtt(srt_path, word_level=False)
        log(f"   ✓  {os.path.basename(srt_path)}", "success")
    except Exception as e:
        log(f"   ✗  Erro em {os.path.basename(video_path)}: {e}", "error")

# -------------------------------------------------
# COMPONENTES
# -------------------------------------------------
def make_button(parent, text, command, primary=False, width=None):
    cfg = dict(
        text=text,
        command=command,
        font=FONT_BTN,
        relief="flat",
        cursor="hand2",
        bd=0,
        padx=20,
        pady=10,
    )
    if width:
        cfg["width"] = width
    if primary:
        btn = tk.Button(parent, bg=ACCENT, fg="white", activebackground=ACCENT2,
                        activeforeground="white", **cfg)
    else:
        btn = tk.Button(parent, bg=SURFACE, fg=SUBTEXT, activebackground=BORDER,
                        activeforeground=TEXT, **cfg)
    return btn

def make_label(parent, text, font=FONT_LABEL, fg=SUBTEXT):
    return tk.Label(parent, text=text, font=font, bg=BG, fg=fg)

def separator(parent):
    f = tk.Frame(parent, bg=BORDER, height=1)
    f.pack(fill="x", padx=24, pady=4)
    return f

# -------------------------------------------------
# RADIOBUTTON GROUP CUSTOM
# -------------------------------------------------
class RadioGroup(tk.Frame):
    def __init__(self, parent, options, default=None, **kw):
        super().__init__(parent, bg=BG, **kw)
        self.var = tk.StringVar(value=default or options[0])
        self.buttons = []
        for opt in options:
            btn = tk.Button(
                self,
                text=opt,
                font=FONT_VALUE,
                relief="flat",
                cursor="hand2",
                bd=0,
                padx=12,
                pady=6,
                command=lambda o=opt: self._select(o),
            )
            btn.pack(side="left", padx=2)
            self.buttons.append((opt, btn))
        self._refresh()

    def _select(self, value):
        self.var.set(value)
        self._refresh()

    def _refresh(self):
        for opt, btn in self.buttons:
            if opt == self.var.get():
                btn.configure(bg=ACCENT, fg="white", activebackground=ACCENT2,
                               activeforeground="white")
            else:
                btn.configure(bg=BORDER, fg=SUBTEXT, activebackground=SURFACE,
                               activeforeground=TEXT)

    def get(self):
        return self.var.get()

# -------------------------------------------------
# APP
# -------------------------------------------------
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Legendas — IESDE")
        self.root.geometry("760x580")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.target = None
        self.running = False

        self.frame_select  = tk.Frame(root, bg=BG)
        self.frame_process = tk.Frame(root, bg=BG)

        self._build_select()
        self._build_process()
        self._show_select()

    # =========================================================
    # TELA 1 — SELEÇÃO
    # =========================================================
    def _build_select(self):
        f = self.frame_select

        # — espaço superior
        tk.Frame(f, bg=BG, height=60).pack()

        # — ícone / logotipo textual
        logo = tk.Label(f, text="◈", font=("Segoe UI", 38), bg=BG, fg=ACCENT)
        logo.pack()

        tk.Label(f, text="Gerador de Legendas", font=FONT_TITLE, bg=BG, fg=TEXT).pack(pady=(8, 4))
        tk.Label(f, text="IESDE · powered by Whisper", font=FONT_SMALL, bg=BG, fg=SUBTEXT).pack()

        tk.Frame(f, bg=BG, height=40).pack()

        # — cards de seleção
        cards = tk.Frame(f, bg=BG)
        cards.pack()

        self._card_btn(cards, "🎬", "Um arquivo", "Selecione um único .mp4", self._select_file).pack(
            side="left", padx=12)
        self._card_btn(cards, "📁", "Uma pasta", "Todos os .mp4 da pasta", self._select_folder).pack(
            side="left", padx=12)

        tk.Frame(f, bg=BG, height=30).pack()
        tk.Label(f, text="Suporte a GPU CUDA • Modelos tiny → large",
                 font=FONT_SMALL, bg=BG, fg=BORDER).pack()

    def _card_btn(self, parent, icon, title, desc, cmd):
        card = tk.Frame(parent, bg=SURFACE, cursor="hand2", relief="flat",
                        bd=0, width=220, height=150)
        card.pack_propagate(False)

        def on_enter(_):  card.configure(bg=BORDER)
        def on_leave(_):  card.configure(bg=SURFACE)
        def click(_):     cmd()

        for w in (card,):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", click)

        inner = tk.Frame(card, bg=SURFACE)
        inner.place(relx=0.5, rely=0.5, anchor="center")
        inner.bind("<Enter>", on_enter)
        inner.bind("<Leave>", on_leave)
        inner.bind("<Button-1>", click)

        lbl_icon = tk.Label(inner, text=icon, font=("Segoe UI", 26), bg=SURFACE, fg=ACCENT)
        lbl_icon.pack()
        lbl_icon.bind("<Enter>", on_enter); lbl_icon.bind("<Leave>", on_leave)
        lbl_icon.bind("<Button-1>", click)

        lbl_title = tk.Label(inner, text=title, font=("Segoe UI", 10, "bold"), bg=SURFACE, fg=TEXT)
        lbl_title.pack(pady=(4, 0))
        lbl_title.bind("<Enter>", on_enter); lbl_title.bind("<Leave>", on_leave)
        lbl_title.bind("<Button-1>", click)

        lbl_desc = tk.Label(inner, text=desc, font=FONT_SMALL, bg=SURFACE, fg=SUBTEXT)
        lbl_desc.pack()
        lbl_desc.bind("<Enter>", on_enter); lbl_desc.bind("<Leave>", on_leave)
        lbl_desc.bind("<Button-1>", click)

        return card

    # =========================================================
    # TELA 2 — PROCESSAMENTO
    # =========================================================
    def _build_process(self):
        f = self.frame_process

        # ── topbar
        topbar = tk.Frame(f, bg=SURFACE, height=52)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        make_button(topbar, "← Voltar", self._show_select).pack(side="left", padx=12, pady=8)

        tk.Label(topbar, text="Legendas — IESDE", font=("Segoe UI", 11, "bold"),
                 bg=SURFACE, fg=TEXT).pack(side="left", padx=4)

        self.btn_run = make_button(topbar, "▶  Gerar Legendas", self._run, primary=True)
        self.btn_run.pack(side="right", padx=12, pady=8)

        # ── painel de configuração
        cfg_row = tk.Frame(f, bg=BG)
        cfg_row.pack(fill="x", padx=20, pady=(14, 6))

        # — bloco dispositivo
        col1 = tk.Frame(cfg_row, bg=BG)
        col1.pack(side="left", padx=(0, 30))
        tk.Label(col1, text="DISPOSITIVO", font=FONT_LABEL, bg=BG, fg=SUBTEXT).pack(anchor="w")
        tk.Frame(col1, bg=BG, height=4).pack()
        default_device = "GPU (CUDA)" if gpu_available() else "CPU"
        self.device_group = RadioGroup(col1, ["CPU", "GPU (CUDA)"], default=default_device)
        self.device_group.pack(anchor="w")

        # — bloco modelo
        col2 = tk.Frame(cfg_row, bg=BG)
        col2.pack(side="left")
        tk.Label(col2, text="MODELO WHISPER", font=FONT_LABEL, bg=BG, fg=SUBTEXT).pack(anchor="w")
        tk.Frame(col2, bg=BG, height=4).pack()
        self.model_group = RadioGroup(col2, ["tiny", "base", "small", "medium", "large"],
                                      default="large")
        self.model_group.pack(anchor="w")

        # — alvo selecionado
        self.lbl_target = tk.Label(f, text="", font=FONT_SMALL, bg=BG, fg=SUBTEXT,
                                    anchor="w", wraplength=700)
        self.lbl_target.pack(fill="x", padx=22, pady=(2, 6))

        separator(f)

        # ── log
        log_container = tk.Frame(f, bg=BG)
        log_container.pack(fill="both", expand=True, padx=20, pady=(6, 0))

        self.log_box = tk.Text(
            log_container,
            bg=SURFACE,
            fg=TEXT,
            font=FONT_LOG,
            relief="flat",
            bd=0,
            padx=14,
            pady=12,
            insertbackground=ACCENT,
            selectbackground=ACCENT,
        )
        self.log_box.pack(fill="both", expand=True)
        self.log_box.config(state="disabled")

        # tags de cor
        self.log_box.tag_config("info",    foreground=TEXT)
        self.log_box.tag_config("success", foreground=SUCCESS)
        self.log_box.tag_config("error",   foreground=ERROR)
        self.log_box.tag_config("warn",    foreground=WARNING)
        self.log_box.tag_config("dim",     foreground=SUBTEXT)
        self.log_box.tag_config("accent",  foreground=ACCENT2)

        # ── status bar
        self.statusbar = tk.Frame(f, bg=BORDER, height=28)
        self.statusbar.pack(fill="x")
        self.statusbar.pack_propagate(False)
        self.lbl_status = tk.Label(self.statusbar, text="Pronto", font=FONT_SMALL,
                                    bg=BORDER, fg=SUBTEXT)
        self.lbl_status.pack(side="left", padx=12)

    # =========================================================
    # HELPERS
    # =========================================================
    def log(self, text, tag="info"):
        self.log_box.config(state="normal")
        self.log_box.insert("end", text + "\n", tag)
        self.log_box.see("end")
        self.log_box.config(state="disabled")
        self.root.update()

    def set_status(self, text, color=SUBTEXT):
        self.lbl_status.configure(text=text, fg=color)
        self.root.update()

    # =========================================================
    # NAVEGAÇÃO
    # =========================================================
    def _select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Vídeos MP4", "*.mp4")])
        if path:
            self.target = path
            self._show_process()

    def _select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.target = path
            self._show_process()

    def _show_select(self):
        self.frame_process.pack_forget()
        self.frame_select.pack(fill="both", expand=True)

    def _show_process(self):
        self.frame_select.pack_forget()
        self.frame_process.pack(fill="both", expand=True)
        short = self.target if len(self.target) < 80 else "…" + self.target[-77:]
        self.lbl_target.configure(text=f"Alvo: {short}")
        # limpar log ao trocar alvo
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")
        self.set_status("Pronto")

    # =========================================================
    # EXECUÇÃO
    # =========================================================
    def _run(self):
        if self.running:
            return
        if not self.target:
            messagebox.showerror("Erro", "Nenhum arquivo ou pasta selecionado.")
            return

        device_sel = self.device_group.get()
        if device_sel == "GPU (CUDA)":
            if not gpu_available():
                messagebox.showerror("Erro", "GPU CUDA não disponível.")
                return
            device = "cuda"
        else:
            device = "cpu"

        model_name = self.model_group.get()
        self.running = True
        self.btn_run.configure(state="disabled", text="Processando…")

        def worker():
            try:
                self.log(f"Modelo  : {model_name}", "dim")
                self.log(f"Device  : {device.upper()}", "dim")
                self.log(f"Alvo    : {os.path.basename(self.target)}\n", "dim")
                self.set_status("Carregando modelo…", WARNING)

                model = stable_whisper.load_model(model_name, device=device)

                if os.path.isfile(self.target):
                    videos = [os.path.abspath(self.target)]
                else:
                    folder = os.path.abspath(self.target)
                    videos = [
                        os.path.join(folder, f)
                        for f in os.listdir(folder)
                        if f.lower().endswith(".mp4")
                        and os.path.isfile(os.path.join(folder, f))
                    ]
                    self.log(f"Pasta   : {folder}", "dim")

                total = len(videos)
                self.log(f"{total} vídeo(s) encontrado(s)\n", "accent")
                self.set_status(f"Processando 0/{total}…", WARNING)

                for i, path in enumerate(videos, 1):
                    self.set_status(f"Processando {i}/{total}…", WARNING)
                    process_video(path, model, self.log)

                self.log("\n✓ Concluído com sucesso.", "success")
                self.set_status(f"Concluído — {total} vídeo(s)", SUCCESS)
            except Exception as e:
                self.log(f"\n✗ Falha geral: {e}", "error")
                self.set_status("Erro", ERROR)
            finally:
                self.running = False
                self.btn_run.configure(state="normal", text="▶  Gerar Legendas")

        threading.Thread(target=worker, daemon=True).start()


# -------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
