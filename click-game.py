"""一个简单的点击计分小游戏 — 基于 tkinter。"""

import tkinter as tk
from tkinter import messagebox


class ClickGame:
    SCORE_PER_CLICK = 1

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Click Game")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.score = 0
        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self.root, bg="#f0f0f0")
        frame.pack(expand=True, fill="both")

        tk.Label(
            frame, text="点击下方按钮得分！", font=("Arial", 14), bg="#f0f0f0"
        ).pack(pady=(40, 10))

        self.score_label = tk.Label(
            frame, text="得分: 0", font=("Arial", 24, "bold"), fg="#2196F3", bg="#f0f0f0"
        )
        self.score_label.pack(pady=10)

        self.click_btn = tk.Button(
            frame,
            text="点我！",
            font=("Arial", 18),
            width=12,
            height=2,
            bg="#4CAF50",
            fg="white",
            activebackground="#388E3C",
            command=self._on_click,
        )
        self.click_btn.pack(pady=20)

        tk.Button(
            frame, text="重置", font=("Arial", 10), command=self._reset
        ).pack()

    def _on_click(self):
        try:
            self.score += self.SCORE_PER_CLICK
            self._refresh_score()
        except tk.TclError:
            messagebox.showerror("错误", "窗口已关闭，无法更新分数。")

    def _refresh_score(self):
        self.score_label.config(text=f"得分: {self.score}")

    def _reset(self):
        self.score = 0
        self._refresh_score()


def main():
    root = tk.Tk()
    ClickGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
