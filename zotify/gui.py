"""Desktop app for Zotify downloads."""

from __future__ import annotations

from argparse import Namespace
from pathlib import Path
from queue import Empty, Queue
from threading import Thread
import tkinter as tk
from tkinter import filedialog, messagebox

from zotify.app import client
from zotify.config import CONFIG_VALUES


class ZotifyApp:
    """Small desktop wrapper around the existing Zotify client."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Zotify Desktop")
        self.root.geometry("900x620")
        self.root.minsize(820, 560)

        self.output_var = tk.StringVar(value=str(Path.home() / "Music" / "Zotify Music"))
        self.status_var = tk.StringVar(value="Pronto para baixar.")
        self.log_queue: Queue[str] = Queue()

        self._build_ui()
        self._poll_logs()

    def _build_ui(self) -> None:
        main = tk.Frame(self.root, padx=16, pady=16)
        main.pack(fill=tk.BOTH, expand=True)

        tk.Label(main, text="Zotify Desktop", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(
            main,
            text="Cole um ou mais links do Spotify (um por linha) e clique em Baixar.",
            fg="#4b5563",
        ).pack(anchor="w", pady=(0, 12))

        output_frame = tk.LabelFrame(main, text="Pasta de destino", padx=10, pady=10)
        output_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Entry(output_frame, textvariable=self.output_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(output_frame, text="Escolher...", command=self.choose_output_dir).pack(side=tk.LEFT, padx=(8, 0))

        links_frame = tk.LabelFrame(main, text="Links Spotify", padx=10, pady=10)
        links_frame.pack(fill=tk.BOTH, expand=True)

        self.links_text = tk.Text(links_frame, height=12, wrap=tk.WORD)
        self.links_text.pack(fill=tk.BOTH, expand=True)

        helper = (
            "Suporta link de música, álbum, playlist, artista, episódio e podcast. "
            "Ex.: https://open.spotify.com/track/..."
        )
        tk.Label(main, text=helper, fg="#6b7280").pack(anchor="w", pady=(8, 10))

        actions = tk.Frame(main)
        actions.pack(fill=tk.X, pady=(0, 10))

        self.download_btn = tk.Button(actions, text="Baixar links", width=18, command=self.download_links)
        self.download_btn.pack(side=tk.LEFT)
        tk.Button(actions, text="Baixar curtidas", width=18, command=self.download_liked).pack(side=tk.LEFT, padx=8)
        tk.Button(actions, text="Baixar playlists", width=18, command=self.download_playlists).pack(side=tk.LEFT)
        tk.Button(actions, text="Baixar seguidos", width=18, command=self.download_followed).pack(side=tk.LEFT, padx=8)

        status = tk.Label(main, textvariable=self.status_var, fg="#1f2937")
        status.pack(anchor="w", pady=(4, 6))

        logs_frame = tk.LabelFrame(main, text="Logs", padx=10, pady=10)
        logs_frame.pack(fill=tk.BOTH, expand=True)

        self.logs_text = tk.Text(logs_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.logs_text.pack(fill=tk.BOTH, expand=True)

    def choose_output_dir(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.output_var.get() or str(Path.home()))
        if selected:
            self.output_var.set(selected)

    def _default_args(self) -> Namespace:
        data = {
            "no_splash": True,
            "config_location": None,
            "username": None,
            "password": None,
            "urls": [],
            "liked_songs": False,
            "followed_artists": False,
            "playlist": False,
            "search": None,
            "download": None,
        }
        for config_key in CONFIG_VALUES:
            data[config_key.lower()] = None

        data["root_path"] = self.output_var.get().strip() or None
        return Namespace(**data)

    def _run_task(self, args: Namespace, status_text: str) -> None:
        if not self.output_var.get().strip():
            messagebox.showwarning("Destino", "Escolha uma pasta de destino primeiro.")
            return

        self.download_btn.configure(state=tk.DISABLED)
        self.status_var.set(status_text)
        self._log("Iniciando download...")

        def worker() -> None:
            try:
                client(args)
            except Exception as exc:  # noqa: BLE001
                self.log_queue.put(f"Erro: {exc}")
                self.root.after(0, lambda: self.status_var.set("Falha durante download."))
                self.root.after(0, lambda: messagebox.showerror("Erro", str(exc)))
            else:
                self.log_queue.put("Download concluído.")
                self.root.after(0, lambda: self.status_var.set("Concluído com sucesso."))
            finally:
                self.root.after(0, lambda: self.download_btn.configure(state=tk.NORMAL))

        Thread(target=worker, daemon=True).start()

    def _log(self, message: str) -> None:
        self.logs_text.configure(state=tk.NORMAL)
        self.logs_text.insert(tk.END, f"{message}\n")
        self.logs_text.see(tk.END)
        self.logs_text.configure(state=tk.DISABLED)

    def _poll_logs(self) -> None:
        try:
            while True:
                self._log(self.log_queue.get_nowait())
        except Empty:
            pass
        self.root.after(250, self._poll_logs)

    def download_links(self) -> None:
        urls = [line.strip() for line in self.links_text.get("1.0", tk.END).splitlines() if line.strip()]
        if not urls:
            messagebox.showwarning("Links", "Cole ao menos um link do Spotify.")
            return

        args = self._default_args()
        args.urls = urls
        self._run_task(args, "Baixando links informados...")

    def download_liked(self) -> None:
        args = self._default_args()
        args.liked_songs = True
        self._run_task(args, "Baixando músicas curtidas...")

    def download_playlists(self) -> None:
        args = self._default_args()
        args.playlist = True
        self._run_task(args, "Baixando playlists salvas...")

    def download_followed(self) -> None:
        args = self._default_args()
        args.followed_artists = True
        self._run_task(args, "Baixando artistas seguidos...")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    ZotifyApp().run()


if __name__ == "__main__":
    main()
