"""一个简单的点击计分小游戏 — 基于 tkinter。"""

import tkinter as tk

THEME = {
    "bg": "#f0f0f0",
    "score_fg": "#2196F3",
    "high_fg": "#FF9800",
    "timer_fg": "#E53935",
    "btn_bg": "#4CAF50",
    "btn_flash": "#81C784",
    "btn_fg": "white",
    "btn_active": "#388E3C",
    "challenge_bg": "#FF5722",
    "challenge_active": "#E64A19",
    "font_title": ("Arial", 14),
    "font_score": ("Arial", 24, "bold"),
    "font_btn": ("Arial", 18),
    "font_small": ("Arial", 10),
    "font_timer": ("Arial", 16, "bold"),
}

WINDOW_W = 420
WINDOW_H = 420
CHALLENGE_SECS = 30


class ClickGame:
    SCORE_PER_CLICK = 1

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Click Game")
        self.root.resizable(False, False)
        self.root.configure(bg=THEME["bg"])
        self._center_window()
        self.score = 0
        self.high_score = 0
        self._in_challenge = False
        self._remaining = 0
        self._timer_id = None
        self._build_ui()
        self.root.bind("<space>", lambda e: self._on_click())

    def _build_ui(self):
        t = THEME
        frame = tk.Frame(self.root, bg=t["bg"])
        frame.pack(expand=True, fill="both")

        tk.Label(
            frame, text="点击按钮或按空格键得分！", font=t["font_title"], bg=t["bg"]
        ).pack(pady=(30, 5))

        self.high_label = tk.Label(
            frame, text="最高分: 0", font=t["font_small"], fg=t["high_fg"], bg=t["bg"]
        )
        self.high_label.pack()

        self.score_label = tk.Label(
            frame, text="得分: 0", font=t["font_score"], fg=t["score_fg"], bg=t["bg"]
        )
        self.score_label.pack(pady=5)

        self.timer_label = tk.Label(
            frame, text="", font=t["font_timer"], fg=t["timer_fg"], bg=t["bg"]
        )
        self.timer_label.pack()

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
        self.click_btn.pack(pady=15)

        btn_row = tk.Frame(frame, bg=t["bg"])
        btn_row.pack()

        self.challenge_btn = tk.Button(
            btn_row,
            text="限时挑战",
            font=t["font_small"],
            bg=t["challenge_bg"],
            fg=t["btn_fg"],
            activebackground=t["challenge_active"],
            command=self._start_challenge,
        )
        self.challenge_btn.pack(side="left", padx=10)

        tk.Button(
            btn_row, text="重置", font=t["font_small"], command=self._reset
        ).pack(side="left", padx=10)

    def _center_window(self):
        sx = self.root.winfo_screenwidth()
        sy = self.root.winfo_screenheight()
        x = (sx - WINDOW_W) // 2
        y = (sy - WINDOW_H) // 2
        self.root.geometry(f"{WINDOW_W}x{WINDOW_H}+{x}+{y}")

    def _on_click(self):
        if not self.click_btn["state"] == "normal":
            return
        self.score += self.SCORE_PER_CLICK
        self._update_high()
        self._refresh_score()
        self._flash_btn()

    def _flash_btn(self):
        self.click_btn.config(bg=THEME["btn_flash"])
        self.root.after(120, lambda: self.click_btn.config(bg=THEME["btn_bg"]))

    def _refresh_score(self):
        self.score_label.config(text=f"得分: {self.score}")

    def _update_high(self):
        if self.score > self.high_score:
            self.high_score = self.score
            self.high_label.config(text=f"最高分: {self.high_score}")

    def _reset(self):
        if self._in_challenge:
            return
        self.score = 0
        self._refresh_score()

    def _start_challenge(self):
        if self._in_challenge:
            return
        self._in_challenge = True
        self.score = 0
        self._remaining = CHALLENGE_SECS
        self._refresh_score()
        self.timer_label.config(text=f"剩余: {self._remaining}s")
        self.click_btn.config(state="normal")
        self.challenge_btn.config(state="disabled")
        self._tick()

    def _tick(self):
        if self._remaining <= 0:
            self._end_challenge()
            return
        self._remaining -= 1
        self.timer_label.config(text=f"剩余: {self._remaining}s")
        self._timer_id = self.root.after(1000, self._tick)

    def _end_challenge(self):
        self._in_challenge = False
        self._update_high()
        self.click_btn.config(state="disabled")
        self.challenge_btn.config(state="normal")
        self.timer_label.config(text=f"时间到！得分: {self.score}")


def main():
    try:
        root = tk.Tk()
        ClickGame(root)
        root.mainloop()
    except Exception as e:
        print(f"程序出错：{e}")


if __name__ == "__main__":
    main()
