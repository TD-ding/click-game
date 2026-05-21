"""一个简单的点击计分小游戏 — 基于 tkinter。"""

import tkinter as tk

THEME = {
    "bg": "#f0f0f0",
    "score_fg": "#2196F3",
    "btn_bg": "#4CAF50",
    "btn_flash": "#81C784",
    "btn_fg": "white",
    "btn_active": "#388E3C",
    "font_title": ("Arial", 14),
    "font_score": ("Arial", 24, "bold"),
    "font_btn": ("Arial", 18),
    "font_small": ("Arial", 10),
}

WINDOW_W = 400
WINDOW_H = 300


class ClickGame:
    SCORE_PER_CLICK = 1

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Click Game")
        self.root.resizable(False, False)
        self.root.configure(bg=THEME["bg"])
        self._center_window()
        self.score = 0
        self._build_ui()
        self.root.bind("<space>", lambda e: self._on_click())

    def _build_ui(self):
        t = THEME
        frame = tk.Frame(self.root, bg=t["bg"])
        frame.pack(expand=True, fill="both")

        tk.Label(
            frame, text="点击按钮或按空格键得分！", font=t["font_title"], bg=t["bg"]
        ).pack(pady=(40, 10))

        self.score_label = tk.Label(
            frame, text="得分: 0", font=t["font_score"], fg=t["score_fg"], bg=t["bg"]
        )
        self.score_label.pack(pady=10)

        self.click_btn = tk.Button(
            frame,
            text="点我！",
            font=t["font_btn"],
            width=12,
            height=2,
            bg=t["btn_bg"],
            fg=t["btn_fg"],
            activebackground=t["btn_active"],
            command=self._on_click,
        )
        self.click_btn.pack(pady=20)

        tk.Button(
            frame, text="重置", font=t["font_small"], command=self._reset
        ).pack()

    def _center_window(self):
        sx = self.root.winfo_screenwidth()
        sy = self.root.winfo_screenheight()
        x = (sx - WINDOW_W) // 2
        y = (sy - WINDOW_H) // 2
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}+{x}+{y}")

    def _on_click(self):
        self.score += self.SCORE_PER_CLICK
        self._refresh_score()
        self._flash_btn()

    def _flash_btn(self):
        self.click_btn.config(bg=THEME["btn_flash"])
        self.root.after(120, lambda: self.click_btn.config(bg=THEME["btn_bg"]))

    def _refresh_score(self):
        self.score_label.config(text=f"得分: {self.score}")

    def _reset(self):
        self.score = 0
        self._refresh_score()


def main():
    try:
        root = tk.Tk()
        ClickGame(root)
        root.mainloop()
    except Exception as e:
        print(f"程序出错：{e}")


if __name__ == "__main__":
    main()
