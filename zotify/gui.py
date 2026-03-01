"""Simple desktop interface for running Zotify downloads without CLI arguments."""

from __future__ import annotations

from argparse import Namespace
from threading import Thread
import tkinter as tk
from tkinter import messagebox

from zotify.app import client
from zotify.config import CONFIG_VALUES


class ZotifyGUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Zotify App")
        self.root.geometry("720x360")
        self.root.resizable(False, False)

        self._build_ui()

    def _build_ui(self) -> None:
        container = tk.Frame(self.root, padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        title = tk.Label(container, text="Zotify", font=("Arial", 20, "bold"))
        title.pack(anchor="w")

        subtitle = tk.Label(
            container,
            text="Cole links do Spotify abaixo e clique em Baixar. Também há atalhos para curtidas e playlists.",
            fg="#333333",
            justify=tk.LEFT,
        )
        subtitle.pack(anchor="w", pady=(0, 12))

        self.urls_text = tk.Text(container, height=10, width=88)
        self.urls_text.pack(fill=tk.X)

        hint = tk.Label(
            container,
            text="Aceita múltiplos links (um por linha): música, álbum, playlist, artista, episódio ou podcast.",
            fg="#666666",
            justify=tk.LEFT,
        )
        hint.pack(anchor="w", pady=(6, 12))

        buttons = tk.Frame(container)
        buttons.pack(anchor="w")

        tk.Button(buttons, text="Baixar links", command=self.download_links, width=18).grid(row=0, column=0, padx=(0, 8))
        tk.Button(buttons, text="Músicas curtidas", command=self.download_liked, width=18).grid(row=0, column=1, padx=(0, 8))
        tk.Button(buttons, text="Playlists salvas", command=self.download_playlist, width=18).grid(row=0, column=2, padx=(0, 8))
        tk.Button(buttons, text="Artistas seguidos", command=self.download_followed, width=18).grid(row=0, column=3)

        self.status_var = tk.StringVar(value="Pronto.")
        status = tk.Label(container, textvariable=self.status_var, fg="#444444")
        status.pack(anchor="w", pady=(16, 0))

    def _base_args(self) -> Namespace:
        args = {
            "no_splash": False,
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
            args[config_key.lower()] = None

        return Namespace(**args)

    def _run_client(self, args: Namespace, started_message: str) -> None:
        self.status_var.set(started_message)

        def run() -> None:
            try:
                client(args)
                self.root.after(0, lambda: self.status_var.set("Concluído."))
            except Exception as exc:  # noqa: BLE001
                self.root.after(0, lambda: self.status_var.set("Falhou. Veja detalhes no terminal."))
                self.root.after(0, lambda: messagebox.showerror("Erro", str(exc)))

        Thread(target=run, daemon=True).start()

    def download_links(self) -> None:
        urls = [line.strip() for line in self.urls_text.get("1.0", tk.END).splitlines() if line.strip()]
        if not urls:
            messagebox.showwarning("Atenção", "Cole pelo menos um link do Spotify para baixar.")
            return

        args = self._base_args()
        args.urls = urls
        self._run_client(args, "Baixando links...")

    def download_liked(self) -> None:
        args = self._base_args()
        args.liked_songs = True
        self._run_client(args, "Baixando músicas curtidas...")

    def download_playlist(self) -> None:
        args = self._base_args()
        args.playlist = True
        self._run_client(args, "Baixando playlist salva...")

    def download_followed(self) -> None:
        args = self._base_args()
        args.followed_artists = True
        self._run_client(args, "Baixando artistas seguidos...")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    ZotifyGUI().run()


if __name__ == "__main__":
    main()
