import tkinter as tk
from tkinter import messagebox
import math
import re


class ScientificCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Immersive Scientific Calculator")
        self.root.geometry("1100x760")
        self.root.minsize(700, 500)
        self.root.configure(bg="#08090d")

        self.expression = ""
        self.cursor_pos = 0
        self.answer = 0
        self.memory = 0
        self.angle_mode = "DEG"
        self.history = []
        self.history_visible = True
        self.sci_visible = True

        self.build_background()
        self.build_interface()
        self.bind_keyboard()

    # ============================================================
    # BACKGROUND
    # ============================================================

    def build_background(self):
        self.canvas = tk.Canvas(
            self.root,
            bg="#08090d",
            highlightthickness=0
        )
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Ambient circles
        self.canvas.create_oval(
            -200, -180, 300, 320,
            fill="#101a32",
            outline=""
        )

        self.canvas.create_oval(
            800, 400, 1250, 850,
            fill="#17102c",
            outline=""
        )

        self.canvas.create_oval(
            400, 250, 850, 700,
            fill="#0b1720",
            outline=""
        )

    # ============================================================
    # MAIN INTERFACE
    # ============================================================

    def build_interface(self):

        self.main = tk.Frame(
            self.root,
            bg="#0c0e14",
            highlightbackground="#252936",
            highlightthickness=1
        )

        self.main.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            relwidth=0.94,
            relheight=0.92
        )

        # Sliders: horizontal (left <-> right) + vertical (sci <-> history)
        # Smooth: opaqueresize=live drag, visible handle + resize cursor,
        # debounced _on_resize (see below) so sash moves at 60fps
        self.main_paned = tk.PanedWindow(
            self.main,
            orient="horizontal",
            sashwidth=8,
            sashrelief="flat",
            bg="#0c0e14",
            bd=0,
            opaqueresize=True,
            showhandle=True,
            handlesize=24,
            handlepad=4,
            sashcursor="sb_h_double_arrow",
            sashpad=2
        )
        self.main_paned.pack(fill="both", expand=True, padx=25, pady=25)

        # --------------------------------------------------------
        # LEFT SIDE
        # --------------------------------------------------------

        self.left = tk.Frame(
            self.main_paned,
            bg="#0c0e14"
        )

        self.main_paned.add(self.left, minsize=320, stretch="always")

        # Header
        header = tk.Frame(
            self.left,
            bg="#0c0e14"
        )
        header.pack(fill="x")

        tk.Label(
            header,
            text="SCIENTIFIC",
            font=("Helvetica", 11, "bold"),
            fg="#7e879c",
            bg="#0c0e14"
        ).pack(anchor="w")

        tk.Label(
            header,
            text="CALCULATOR",
            font=("Helvetica", 25, "bold"),
            fg="#f4f6fb",
            bg="#0c0e14"
        ).pack(anchor="w")

        # --------------------------------------------------------
        # DISPLAY
        # --------------------------------------------------------

        self.display_frame = tk.Frame(
            self.left,
            bg="#10131b",
            highlightbackground="#252b3a",
            highlightthickness=1
        )

        self.display_frame.pack(
            fill="x",
            pady=(20, 15)
        )

        top_row = tk.Frame(self.display_frame, bg="#10131b")
        top_row.pack(fill="x", padx=18, pady=(12, 0))

        self.memory_label = tk.Label(
            top_row,
            text="",
            font=("Helvetica", 10, "bold"),
            fg="#fbbf24",
            bg="#10131b"
        )
        self.memory_label.pack(side="left")

        self.mode_label = tk.Label(
            top_row,
            text="DEG",
            font=("Helvetica", 10, "bold"),
            fg="#65d9ff",
            bg="#10131b"
        )
        self.mode_label.pack(side="right")

        self.display = tk.Entry(
            self.display_frame,
            font=("Helvetica", 28, "bold"),
            fg="#ffffff",
            bg="#10131b",
            justify="right",
            relief="flat",
            bd=0,
            highlightthickness=0,
            insertbackground="#ffffff",
            insertwidth=2,
            disabledbackground="#10131b",
            disabledforeground="#ffffff",
            readonlybackground="#10131b",
            state="readonly",
        )

        self.display.pack(
            fill="x",
            padx=18,
            pady=(4, 4),
            ipady=6
        )
        # Cursor / arrow editing: Entry holds pretty text, we mirror self.expression
        # readonly blocks direct typing (all input via handlers) but allows cursor moves
        self.display.bind("<ButtonRelease-1>", lambda e: self._sync_cursor_from_widget())
        self.display.bind("<KeyRelease-Left>", lambda e: self._sync_cursor_from_widget())
        self.display.bind("<KeyRelease-Right>", lambda e: self._sync_cursor_from_widget())
        self.display.bind("<KeyRelease-Home>", lambda e: self._sync_cursor_from_widget())
        self.display.bind("<KeyRelease-End>", lambda e: self._sync_cursor_from_widget())

        self.answer_label = tk.Label(
            self.display_frame,
            text="",
            font=("Helvetica", 14),
            fg="#8b93a7",
            bg="#10131b",
            anchor="e",
            justify="right",
            wraplength=620
        )

        self.answer_label.pack(
            fill="x",
            padx=18,
            pady=(0, 12)
        )

        # --------------------------------------------------------
        # MODE BUTTONS
        # --------------------------------------------------------

        mode_frame = tk.Frame(
            self.left,
            bg="#0c0e14"
        )
        mode_frame.pack(fill="x", pady=(0, 10))

        self.deg_btn = self.create_button(
            mode_frame,
            "DEG",
            self.set_degree,
            width=6,
            color="#65d9ff"
        )
        self.deg_btn.pack(side="left", padx=3)

        self.rad_btn = self.create_button(
            mode_frame,
            "RAD",
            self.set_radian,
            width=6
        )
        self.rad_btn.pack(side="left", padx=3)

        self.create_button(
            mode_frame,
            "←",
            self.backspace,
            width=6
        ).pack(side="right", padx=3)

        self.create_button(
            mode_frame,
            "C",
            self.clear,
            width=6,
            color="#ff6b7a"
        ).pack(side="right", padx=3)

        self._sync_mode_buttons()

        # --------------------------------------------------------
        # BASIC BUTTONS
        # --------------------------------------------------------

        keypad = tk.Frame(
            self.left,
            bg="#0c0e14"
        )
        keypad.pack(
            fill="both",
            expand=True
        )

        buttons = [
            ["(", ")", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "−"],
            ["1", "2", "3", "+"],
            ["0", ".", "ANS", "="]
        ]

        for r, row in enumerate(buttons):
            keypad.rowconfigure(r, weight=1)

            for c, text in enumerate(row):
                keypad.columnconfigure(c, weight=1)

                if text == "=":
                    color = "#4cc9f0"
                elif text in ["÷", "×", "−", "+", "%"]:
                    color = "#a78bfa"
                else:
                    color = "#ffffff"

                button = self.create_button(
                    keypad,
                    text,
                    lambda value=text: self.button_press(value),
                    color=color,
                    font_size=16
                )

                button.grid(
                    row=r,
                    column=c,
                    sticky="nsew",
                    padx=4,
                    pady=4
                )

        # --------------------------------------------------------
        # RIGHT SCIENTIFIC PANEL (PanedWindow: manual slider + dual hide)
        # --------------------------------------------------------

        self.right = tk.Frame(
            self.main_paned,
            bg="#10131a",
            highlightbackground="#252936",
            highlightthickness=1
        )

        self.main_paned.add(self.right, minsize=240, stretch="always")
        self.sci_visible = True

        right_header = tk.Frame(self.right, bg="#10131a")
        right_header.pack(fill="x", padx=20, pady=(18, 5))

        tk.Label(
            right_header,
            text="SCIENTIFIC",
            font=("Helvetica", 11, "bold"),
            fg="#7e879c",
            bg="#10131a"
        ).pack(side="left")

        self.sci_toggle = self.create_button(
            right_header,
            "Sci",
            self.toggle_sci,
            color="#8b93a7",
            font_size=9
        )
        self.sci_toggle.pack(side="right", padx=(4, 0))

        self.hist_toggle = self.create_button(
            right_header,
            "Hist",
            self.toggle_history,
            color="#8b93a7",
            font_size=9
        )
        self.hist_toggle.pack(side="right")

        self.right_paned = tk.PanedWindow(
            self.right,
            orient="vertical",
            sashwidth=8,
            sashrelief="flat",
            bg="#10131a",
            bd=0,
            opaqueresize=True,
            showhandle=True,
            handlesize=24,
            handlepad=4,
            sashcursor="sb_v_double_arrow",
            sashpad=2
        )
        self.right_paned.pack(fill="both", expand=True, padx=15, pady=10)

        self.scientific = tk.Frame(
            self.right_paned,
            bg="#10131a"
        )
        self.right_paned.add(self.scientific, minsize=160, stretch="always")

        scientific = self.scientific

        scientific_buttons = [
            ["sin", "cos", "tan"],
            ["sec", "csc", "cot"],
            ["sin⁻¹", "cos⁻¹", "tan⁻¹"],
            ["sinh", "cosh", "tanh"],
            ["log", "ln", "log2"],
            ["eˣ", "2ˣ", "10ˣ"],
            ["x²", "x³", "xʸ"],
            ["√", "cbrt", "1/x"],
            ["π", "e", "n!"],
            ["abs", "mod", "EE"],
            ["MC", "MR", "M+"],
            ["M−", "RAND", "+/-"]
        ]

        for r, row in enumerate(scientific_buttons):
            scientific.rowconfigure(r, weight=1)

            for c, text in enumerate(row):
                scientific.columnconfigure(c, weight=1)

                btn = self.create_button(
                    scientific,
                    text,
                    lambda value=text: self.scientific_press(value),
                    color="#ffffff",
                    font_size=11
                )

                btn.grid(
                    row=r,
                    column=c,
                    sticky="nsew",
                    padx=4,
                    pady=1
                )

        # --------------------------------------------------------
        # HISTORY (PanedWindow pane: manual slider + hide)
        # --------------------------------------------------------

        self.history_frame = tk.Frame(
            self.right_paned,
            bg="#0b0d12",
            highlightbackground="#252936",
            highlightthickness=1
        )

        self.right_paned.add(self.history_frame, minsize=90, stretch="always")

        hist_top = tk.Frame(self.history_frame, bg="#0b0d12")
        hist_top.pack(fill="x", padx=12, pady=8)

        tk.Label(
            hist_top,
            text="HISTORY",
            font=("Helvetica", 9, "bold"),
            fg="#697386",
            bg="#0b0d12"
        ).pack(side="left")

        clear_hist = self.create_button(
            hist_top,
            "Clear",
            self.clear_history,
            color="#ff6b7a",
            font_size=9
        )
        clear_hist.pack(side="right")

        list_frame = tk.Frame(self.history_frame, bg="#0b0d12")
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.history_list = tk.Listbox(
            list_frame,
            bg="#0b0d12",
            fg="#e5e9f2",
            selectbackground="#2a334d",
            selectforeground="#ffffff",
            borderwidth=0,
            highlightthickness=0,
            font=("Menlo", 10)
        )
        self.history_list.pack(side="left", fill="both", expand=True)

        hist_scroll = tk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.history_list.yview
        )
        hist_scroll.pack(side="right", fill="y")
        self.history_list.configure(yscrollcommand=hist_scroll.set)

        self.history_list.bind(
            "<Double-Button-1>",
            self.load_history
        )

        # Dynamic wraplength + font scaling on resize (debounced for smooth sash)
        self._resize_job = None
        self._last_rw = 0
        self._last_rh = 0
        self._saved_main_sash = None
        self._saved_right_sash = None
        self.root.bind("<Configure>", self._on_resize)
        self._move_cursor_to_end()
        self.update_display()

    def _on_resize(self, event=None):
        # Ignore child Configure bursts from sash dragging; only root window
        try:
            if event is not None and getattr(event, "widget", None) not in (None, self.root):
                return
        except Exception:
            pass
        try:
            rw = self.root.winfo_width()
            rh = self.root.winfo_height()
            if abs(rw - self._last_rw) < 4 and abs(rh - self._last_rh) < 4:
                return
            self._last_rw, self._last_rh = rw, rh
            if self._resize_job is not None:
                try:
                    self.root.after_cancel(self._resize_job)
                except Exception:
                    pass
            self._resize_job = self.root.after(80, self._apply_resize)
        except Exception:
            pass

    def _apply_resize(self):
        self._resize_job = None
        # Only react to root resizes (Entry uses x-scroll, only answer wraps)
        try:
            w = self.display_frame.winfo_width()
            if w > 100:
                wrap = max(280, w - 40)
                self.answer_label.configure(wraplength=wrap)
            # Shrink display font on short windows so history stays visible
            h = self.root.winfo_height()
            if h < 620:
                self.display.configure(font=("Helvetica", 22, "bold"))
            else:
                self.display.configure(font=("Helvetica", 28, "bold"))
        except Exception:
            pass

    # ---------- cursor helpers for editable Entry display ----------
    def _pretty(self, expr):
        return (
            expr.replace("*", "×")
            .replace("/", "÷")
            .replace("-", "−")
        )

    def _sync_cursor_from_widget(self):
        try:
            idx = self.display.index(tk.INSERT)
            # pretty and internal are same length (1-1 char maps)
            self.cursor_pos = max(0, min(len(self.expression), int(idx)))
        except Exception:
            pass

    def _insert_at_cursor(self, text):
        self.cursor_pos = max(0, min(len(self.expression), self.cursor_pos))
        self.expression = (
            self.expression[:self.cursor_pos] + text + self.expression[self.cursor_pos:]
        )
        self.cursor_pos += len(text)

    def _move_cursor_to_end(self):
        self.cursor_pos = len(self.expression)

    def _remember_sash(self):
        try:
            self._saved_right_sash = self.right_paned.sash_coord(0)
        except Exception:
            pass
        try:
            self._saved_main_sash = self.main_paned.sash_coord(0)
        except Exception:
            pass

    def _restore_sash(self):
        try:
            if self._saved_right_sash:
                self.right_paned.sash_place(0, *self._saved_right_sash)
        except Exception:
            pass

    def toggle_history(self):
        if self.history_visible:
            self._remember_sash()
            try:
                self.right_paned.forget(self.history_frame)
            except Exception:
                pass
            self.hist_toggle.configure(text="Hist+")
            self.history_visible = False
        else:
            try:
                self.right_paned.add(self.history_frame, minsize=90, stretch="always")
            except Exception:
                pass
            self.hist_toggle.configure(text="Hist")
            self.history_visible = True
            self.root.after_idle(self._restore_sash)

    def toggle_sci(self):
        if self.sci_visible:
            self._remember_sash()
            try:
                self.right_paned.forget(self.scientific)
            except Exception:
                pass
            self.sci_toggle.configure(text="Sci+")
            self.sci_visible = False
        else:
            try:
                # re-add scientific before history to keep order
                try:
                    self.right_paned.forget(self.history_frame)
                except Exception:
                    pass
                self.right_paned.add(self.scientific, minsize=160, stretch="always")
                if self.history_visible:
                    self.right_paned.add(self.history_frame, minsize=90, stretch="always")
            except Exception:
                pass
            self.sci_toggle.configure(text="Sci")
            self.sci_visible = True
            self.root.after_idle(self._restore_sash)

    # ============================================================
    # BUTTON CREATION (cross-platform: Label-based, respects colors
    # on macOS where tk.Button ignores bg/fg)
    # ============================================================

    def create_button(
        self,
        parent,
        text,
        command,
        width=None,
        color="#ffffff",
        font_size=None,
        bg="#1e2433"
    ):
        if font_size is None:
            if text in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                        ".", "+", "−", "×", "÷", "%", "=", "(", ")"]:
                font_size = 16
            elif len(text) <= 3:
                font_size = 12
            else:
                font_size = 11

        bg_normal = bg
        bg_hover = "#2a334d"
        bg_press = "#141824"

        button = tk.Label(
            parent,
            text=text,
            font=("Helvetica", font_size, "bold"),
            fg=color,
            bg=bg_normal,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=8,
            pady=8,
            anchor="center",
            highlightbackground="#394052",
            highlightthickness=1
        )
        button._bg_normal = bg_normal
        button._fg_normal = color
        button._command = command

        if width:
            button.configure(width=width)

        def on_enter(e):
            button.configure(bg=bg_hover)

        def on_leave(e):
            button.configure(bg=getattr(button, "_bg_normal", bg_normal))

        def on_press(e):
            button.configure(bg=bg_press)

        def on_release(e):
            button.configure(bg=bg_hover)
            try:
                button._command()
            except Exception:
                pass

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        button.bind("<ButtonPress-1>", on_press)
        button.bind("<ButtonRelease-1>", on_release)

        return button

    def _sync_mode_buttons(self):
        # Highlight active angle mode
        if self.angle_mode == "DEG":
            self.deg_btn.configure(fg="#65d9ff")
            self.deg_btn._fg_normal = "#65d9ff"
            self.rad_btn.configure(fg="#8b93a7")
            self.rad_btn._fg_normal = "#8b93a7"
        else:
            self.rad_btn.configure(fg="#65d9ff")
            self.rad_btn._fg_normal = "#65d9ff"
            self.deg_btn.configure(fg="#8b93a7")
            self.deg_btn._fg_normal = "#8b93a7"

    def _update_memory_indicator(self):
        if self.memory != 0:
            self.memory_label.configure(text="M")
        else:
            self.memory_label.configure(text="")

    # ============================================================
    # BASIC INPUT
    # ============================================================

    def _clear_answer_preview(self):
        self.answer_label.configure(text="")

    def _format_answer_str(self):
        try:
            return self.format_result(self.answer)
        except Exception:
            return str(self.answer)

    def _char_before_cursor(self):
        if 0 < self.cursor_pos <= len(self.expression):
            return self.expression[self.cursor_pos - 1]
        return ""

    def _maybe_insert_mult(self):
        # Insert explicit × before a new operand/function when needed,
        # based on char before cursor: 2 + sin( -> 2*sin(
        ch = self._char_before_cursor()
        if not ch:
            return
        if ch.isdigit() or ch in ")!":
            self._insert_at_cursor("*")
        elif self.expression[:self.cursor_pos].endswith("pi"):
            self._insert_at_cursor("*")

    def button_press(self, value):

        if value == "=":
            self.calculate()
            return

        mapping = {
            "÷": "/",
            "×": "*",
            "−": "-",
        }

        value = mapping.get(value, value)

        if value == "ANS":
            # Show symbolic ANS so user sees multiply: 2 + ANS -> 2*ANS
            ch = self._char_before_cursor()
            if ch and (ch.isdigit() or ch in ")!"):
                self._insert_at_cursor("*")
            self._insert_at_cursor("ANS")
        else:
            # Guard: don't start with dangling binary ops except minus/paren
            if self.cursor_pos == 0 and value in ["*", "/", "%", ")", "!", "^"]:
                return
            # Guard: operator after operator (allow minus for negative, allow ( )
            ch = self._char_before_cursor()
            if ch and value in ["*", "/", "%", "^"] and ch in "+-*/^(%":
                return
            self._insert_at_cursor(value)

        self._clear_answer_preview()
        self.update_display()

    # ============================================================
    # SCIENTIFIC INPUT
    # ============================================================

    def scientific_press(self, value):

        if value == "MC":
            self.memory = 0
            self._update_memory_indicator()
            return

        if value == "MR":
            self._clear_answer_preview()
            ch = self._char_before_cursor()
            if ch and (ch.isdigit() or ch in ")!"):
                self._insert_at_cursor("*")
            self._insert_at_cursor(str(self.memory))
            self.update_display()
            return

        if value == "M+":
            try:
                if self.expression.strip():
                    self.memory += self.evaluate(self.expression)
                    self._update_memory_indicator()
            except Exception:
                pass
            return

        if value == "M−":
            try:
                if self.expression.strip():
                    self.memory -= self.evaluate(self.expression)
                    self._update_memory_indicator()
            except Exception:
                pass
            return

        if value == "RAND":
            import random
            self._clear_answer_preview()
            ch = self._char_before_cursor()
            if ch and (ch.isdigit() or ch in ")!"):
                self._insert_at_cursor("*")
            self._insert_at_cursor(f"{random.random():.10g}")
            self.update_display()
            return

        if value == "ANS":
            self._clear_answer_preview()
            ch = self._char_before_cursor()
            if ch and (ch.isdigit() or ch in ")!"):
                self._insert_at_cursor("*")
            self._insert_at_cursor("ANS")
            self.update_display()
            return

        if value == "+/-":
            self.toggle_sign()
            return

        if value == "EE":
            ch = self._char_before_cursor()
            if not ch or ch in "+-*/(^":
                return
            self._clear_answer_preview()
            self._insert_at_cursor("E")
            self.update_display()
            return

        mappings = {
            "sin": "sin(",
            "cos": "cos(",
            "tan": "tan(",

            "sec": "sec(",
            "csc": "csc(",
            "cot": "cot(",

            "sin⁻¹": "asin(",
            "cos⁻¹": "acos(",
            "tan⁻¹": "atan(",
            # aliases for old labels / history compat
            "asin": "asin(",
            "acos": "acos(",
            "atan": "atan(",

            "sinh": "sinh(",
            "cosh": "cosh(",
            "tanh": "tanh(",

            "log": "log(",
            "ln": "ln(",
            "log2": "log2(",
            "exp": "exp(",
            "eˣ": "exp(",
            "EXP": "exp(",
            "2ˣ": "2^(",
            "10ˣ": "10^(",
            "10^x": "10^(",

            "√": "sqrt(",
            "cbrt": "cbrt(",
            "x²": "^2",
            "x³": "^3",
            "xʸ": "^",
            "x^y": "^",

            "π": "pi",
            "e": "e",

            "n!": "!",
            "abs": "abs(",
            "mod": "%",
            "1/x": "inv("
        }

        if value not in mappings:
            return

        mapped = mappings[value]

        # Guard postfix operators with empty expression / cursor at start
        if self.cursor_pos == 0 and mapped in ["^2", "^3", "^", "!", "%"]:
            return
        # Guard: ^ after operator or '(' (check char before cursor)
        ch = self._char_before_cursor()
        if mapped in ["^2", "^3", "^", "!", "%"] and ch:
            if ch in "+-*/^(%":
                # Allow "!"/"%" after ")" or digit, else ignore
                if not (ch in ")!" or ch.isdigit()):
                    if mapped in ["^2", "^3", "^"]:
                        return

        self._clear_answer_preview()
        # Prefix functions/constants need explicit × after operand: 2sin(->2*sin(
        prefix_funcs = ("sin(", "cos(", "tan(", "sec(", "csc(", "cot(",
                        "asin(", "acos(", "atan(",
                        "sinh(", "cosh(", "tanh(", "log(", "ln(", "log2(",
                        "exp(", "sqrt(", "cbrt(", "abs(", "inv(",
                        "10^(", "2^(", "pi", "e")
        if mapped in prefix_funcs:
            if mapped in ("pi", "e"):
                # 2pi -> 2*pi, )pi -> )*pi ; but don't break exp( -> e is start of exp
                if ch and (ch.isdigit() or ch in ")!"):
                    self._insert_at_cursor("*")
                elif self.expression[:self.cursor_pos].endswith("pi") and mapped == "e":
                    self._insert_at_cursor("*")
            else:
                self._maybe_insert_mult()
        self._insert_at_cursor(mapped)
        self.update_display()

    def toggle_sign(self):
        if not self.expression:
            self.expression = "-"
            self.cursor_pos = 1
        elif self.expression.startswith("-"):
            self.expression = self.expression[1:]
            self.cursor_pos = max(0, self.cursor_pos - 1)
        else:
            self.expression = "-" + self.expression
            self.cursor_pos += 1
        self._clear_answer_preview()
        self.update_display()

    # ============================================================
    # DISPLAY
    # ============================================================

    def update_display(self):

        text = self._pretty(self.expression) if self.expression else "0"

        self.display.configure(state="normal")
        self.display.delete(0, tk.END)
        self.display.insert(0, text)
        # clamp + restore cursor (pretty same length as internal)
        self.cursor_pos = max(0, min(len(self.expression), self.cursor_pos))
        try:
            if self.expression:
                self.display.icursor(self.cursor_pos)
            else:
                self.display.icursor(0)
            self.display.xview_moveto(1.0)
        except Exception:
            pass
        self.display.configure(state="readonly")

    # ============================================================
    # CALCULATION
    # ============================================================

    def calculate(self):

        if not self.expression.strip():
            return

        try:
            result = self.evaluate(self.expression)

            self.answer = result

            formatted = self.format_result(result)

            original = self.expression

            self.history.append(
                (original, formatted)
            )

            self.history_list.insert(
                0,
                f"{original} = {formatted}"
            )

            self.answer_label.configure(text="")

            self.expression = formatted
            self._move_cursor_to_end()
            self.update_display()

        except ZeroDivisionError as e:
            msg = str(e).lower()
            if any(k in msg for k in ("sec", "csc", "cot", "undefined")):
                self.answer_label.configure(text="Undefined (e.g. sec 90°)")
            else:
                self.answer_label.configure(text="Error: division by zero")
        except (ValueError, SyntaxError, NameError, TypeError, OverflowError):
            self.answer_label.configure(text="Invalid expression")
        except Exception:
            self.answer_label.configure(
                text="Invalid expression"
            )

    # ============================================================
    # EVALUATION ENGINE
    # ============================================================

    @staticmethod
    def _safe_factorial(n):
        try:
            f = float(n)
        except Exception:
            raise ValueError("Invalid factorial")
        if f < 0:
            raise ValueError("Factorial of negative")
        if f.is_integer():
            ni = int(f)
            if ni > 170:
                raise OverflowError("Factorial too large")
            return math.factorial(ni)
        if f > 170:
            raise OverflowError("Factorial too large")
        # Non-integer >= 0 via gamma
        return math.gamma(f + 1)

    @staticmethod
    def _cbrt(x):
        try:
            if hasattr(math, "cbrt"):
                return math.cbrt(x)
        except Exception:
            pass
        if x >= 0:
            return x ** (1 / 3)
        return -((-x) ** (1 / 3))

    def _insert_implicit_mult(self, expr):
        # Protect function names ending in digit: log2(, pow10(
        expr = expr.replace("log2(", "__LOG2__(")
        expr = expr.replace("pow10(", "__POW10__")
        # digit -> protected fn: 2log2( -> 2*log2(
        expr = re.sub(r'(?<=\d)(?=__LOG2__|__POW10__)', '*', expr)
        # 2( -> 2*(
        expr = re.sub(r'(?<=\d)(?=\()', '*', expr)
        # ) -> digit / letter / ( : )(, )2, )sin
        expr = re.sub(r'(?<=\))(?=[\d\w\(])', '*', expr)
        # ! -> digit / letter / (
        expr = re.sub(r'(?<=!)(?=[\d\w\(])', '*', expr)
        # digit -> letter except e/E (scientific handled separately)
        # 2pi, 2sin(, 2sqrt( ...
        expr = re.sub(r'(?<=\d)(?=[a-df-zA-DF-Z\(])', '*', expr)
        # digit -> e (Euler) when e NOT part of scientific (not followed by digit/+/-)
        expr = re.sub(r'(?<=\d)(?=e(?![\d\+\-]))', '*', expr)
        # pi -> digit / ( : pi2, pi(
        expr = re.sub(r'(?<=pi)(?=[\d\(])', '*', expr)
        # digit -> pi : 2pi (already covered but explicit)
        expr = re.sub(r'(?<=\d)(?=pi\b)', '*', expr)
        expr = expr.replace("__LOG2__", "log2(")
        expr = expr.replace("__POW10__", "pow10(")
        return expr

    def evaluate(self, expression):

        expression = expression.replace(" ", "")

        expression = expression.replace("×", "*")
        expression = expression.replace("÷", "/")
        expression = expression.replace("−", "-")

        # Symbolic ANS -> last answer value, so display shows ANS but eval uses number
        try:
            ans_val = f"({self.answer})"
        except Exception:
            ans_val = "(0)"
        expression = re.sub(r"\bANS\b", ans_val, expression)

        # EE notation: 2E3, 2.5E-2 -> (2*10**3), also (2+3)E3
        expression = re.sub(
            r"(\d+(?:\.\d+)?)E([+-]?\d+)",
            r"(\1*10**\2)",
            expression
        )
        expression = re.sub(
            r"(\))E([+-]?\d+)",
            r"\1*10**\2",
            expression
        )

        expression = expression.replace("^", "**")

        # Percentage: only when % is NOT followed by operand (digit/./(/letter)
        # so "5%3" stays as mod, "50%" / "50+10%" become /100
        expression = re.sub(
            r"(\d+(?:\.\d+)?)%(?![\d\.\(a-zA-Z])",
            r"(\1/100)",
            expression
        )
        expression = re.sub(
            r"(\))%(?![\d\.\(a-zA-Z])",
            r"\1/100",
            expression
        )

        # Factorial: support number, parens, and nested factorial() calls
        # e.g. 5! -> factorial(5), (3+2)! -> factorial((3+2)),
        # factorial(5)! -> factorial(factorial(5)) (no NameError, no hang)
        for _ in range(20):
            if "!" not in expression:
                break
            new_expr = re.sub(
                r"(factorial\([^()]*\)|\((?:[^()]*|\([^()]*\))*\)|\d+(?:\.\d+)?)!",
                r"factorial(\1)",
                expression
            )
            if new_expr == expression:
                raise ValueError("Invalid factorial use")
            expression = new_expr
        if "!" in expression:
            raise ValueError("Invalid factorial use")

        expression = self._insert_implicit_mult(expression)

        # Parenthesis balance: auto-close missing ")", error on extra ")"
        if expression.count("(") < expression.count(")"):
            raise SyntaxError("Mismatched parentheses")
        if expression.count("(") > expression.count(")"):
            expression += ")" * (expression.count("(") - expression.count(")"))

        # Mathematical environment
        env = {
            "pi": math.pi,
            "e": math.e,

            "sin": self.sin,
            "cos": self.cos,
            "tan": self.tan,

            "sec": self.sec,
            "csc": self.csc,
            "cot": self.cot,

            "asin": self.asin,
            "acos": self.acos,
            "atan": self.atan,

            "sinh": math.sinh,
            "cosh": math.cosh,
            "tanh": math.tanh,

            "sqrt": math.sqrt,
            "cbrt": self._cbrt,

            "log": math.log10,
            "ln": math.log,
            "log2": math.log2,

            "exp": math.exp,
            "pow10": lambda x: 10 ** x,

            "abs": abs,

            "factorial": self._safe_factorial,

            "inv": lambda x: 1 / x
        }

        return eval(
            expression,
            {"__builtins__": {}},
            env
        )

    # ============================================================
    # TRIGONOMETRY (DEG / RAD only)
    # ============================================================

    def convert_angle(self, x):
        if self.angle_mode == "DEG":
            return math.radians(x)
        return x

    def convert_result(self, x):
        if self.angle_mode == "DEG":
            return math.degrees(x)
        return x

    def sin(self, x):
        return math.sin(
            self.convert_angle(x)
        )

    def cos(self, x):
        return math.cos(
            self.convert_angle(x)
        )

    def tan(self, x):
        return math.tan(
            self.convert_angle(x)
        )

    def sec(self, x):
        c = math.cos(self.convert_angle(x))
        if math.isclose(c, 0.0, abs_tol=1e-12):
            raise ZeroDivisionError("sec undefined")
        return 1 / c

    def csc(self, x):
        s = math.sin(self.convert_angle(x))
        if math.isclose(s, 0.0, abs_tol=1e-12):
            raise ZeroDivisionError("csc undefined")
        return 1 / s

    def cot(self, x):
        t = math.tan(self.convert_angle(x))
        if math.isclose(t, 0.0, abs_tol=1e-12):
            raise ZeroDivisionError("cot undefined")
        return 1 / t

    def asin(self, x):
        return self.convert_result(
            math.asin(x)
        )

    def acos(self, x):
        return self.convert_result(
            math.acos(x)
        )

    def atan(self, x):
        return self.convert_result(
            math.atan(x)
        )

    # ============================================================
    # MODES
    # ============================================================

    def set_degree(self):
        self.angle_mode = "DEG"
        self.mode_label.configure(
            text="DEG"
        )
        self._sync_mode_buttons()

    def set_radian(self):
        self.angle_mode = "RAD"
        self.mode_label.configure(
            text="RAD"
        )
        self._sync_mode_buttons()

    # ============================================================
    # CLEAR / DELETE
    # ============================================================

    def clear(self):
        self.expression = ""
        self.cursor_pos = 0
        self.answer_label.configure(
            text=""
        )
        self.update_display()

    def _smart_delete_before(self):
        # Delete whole token ending at cursor: sin(, ANS, pi, **, etc.
        prefix = self.expression[:self.cursor_pos]
        tokens = [
            "asin(", "acos(", "atan(",
            "sinh(", "cosh(", "tanh(",
            "log2(", "pow10(", "sqrt(", "cbrt(",
            "sin(", "cos(", "tan(", "sec(", "csc(", "cot(",
            "log(", "ln(", "exp(", "abs(", "inv(",
            "10^(", "2^(", "ANS", "pi", "**",
        ]
        for tok in tokens:
            if prefix.endswith(tok):
                self.expression = (
                    self.expression[:self.cursor_pos - len(tok)] + self.expression[self.cursor_pos:]
                )
                self.cursor_pos -= len(tok)
                return
        if self.cursor_pos > 0:
            self.expression = (
                self.expression[:self.cursor_pos - 1] + self.expression[self.cursor_pos:]
            )
            self.cursor_pos -= 1

    def _smart_delete_after(self):
        # Forward Delete: token starting at cursor
        suffix = self.expression[self.cursor_pos:]
        tokens = [
            "asin(", "acos(", "atan(",
            "sinh(", "cosh(", "tanh(",
            "log2(", "pow10(", "sqrt(", "cbrt(",
            "sin(", "cos(", "tan(", "sec(", "csc(", "cot(",
            "log(", "ln(", "exp(", "abs(", "inv(",
            "10^(", "2^(", "ANS", "pi", "**",
        ]
        for tok in tokens:
            if suffix.startswith(tok):
                self.expression = (
                    self.expression[:self.cursor_pos] + self.expression[self.cursor_pos + len(tok):]
                )
                return
        if self.cursor_pos < len(self.expression):
            self.expression = (
                self.expression[:self.cursor_pos] + self.expression[self.cursor_pos + 1:]
            )

    def backspace(self):
        if not self.expression:
            self._clear_answer_preview()
            self.cursor_pos = 0
            self.update_display()
            return

        self._sync_cursor_from_widget_if_focused()
        self._smart_delete_before()

        # Editing result invalidates the shown query preview
        self._clear_answer_preview()
        self.update_display()

    def delete_forward(self):
        if not self.expression:
            return
        self._sync_cursor_from_widget_if_focused()
        self._smart_delete_after()
        self._clear_answer_preview()
        self.update_display()

    def _sync_cursor_from_widget_if_focused(self):
        try:
            if self.display is self.root.focus_get():
                self._sync_cursor_from_widget()
        except Exception:
            pass

    # ============================================================
    # HISTORY
    # ============================================================

    def clear_history(self):
        self.history = []
        self.history_list.delete(0, tk.END)

    def load_history(self, event=None):

        selection = self.history_list.curselection()

        if not selection:
            return

        index = selection[0]

        # Listbox index 0 = most recent = history[-1]
        hist_idx = len(self.history) - 1 - index

        if 0 <= hist_idx < len(self.history):
            expression, _result = self.history[hist_idx]
            self.expression = expression
            self._move_cursor_to_end()
            self._clear_answer_preview()
            self.update_display()

    # ============================================================
    # FORMAT RESULT
    # ============================================================

    def format_result(self, value):

        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                raise OverflowError("Non-finite result")

            if math.isclose(
                value,
                round(value),
                abs_tol=1e-12
            ):
                return str(int(round(value)))

            return f"{value:.12g}"

        return str(value)

    # ============================================================
    # KEYBOARD
    # ============================================================

    def bind_keyboard(self):
        # bind_all so BackSpace/typing works even when History Listbox has focus
        self.root.bind_all("<Key>", self.keyboard_input)
        self.root.bind_all("<KP_Enter>", lambda e: (self.calculate(), "break")[1])
        self.root.bind_all("<Return>", lambda e: (self.calculate(), "break")[1])
        self.root.bind_all("<BackSpace>", lambda e: (self.backspace(), "break")[1])
        self.root.bind_all("<Delete>", lambda e: (self.delete_forward(), "break")[1])
        self.root.bind_all("<Left>", self._arrow_left)
        self.root.bind_all("<Right>", self._arrow_right)
        self.root.bind_all("<Home>", lambda e: self._cursor_home())
        self.root.bind_all("<End>", lambda e: self._cursor_end())

    def _arrow_left(self, event=None):
        # Let Entry move natively when focused, else move our cursor
        try:
            if self.display is self.root.focus_get():
                self.root.after_idle(self._sync_cursor_from_widget)
                return None
        except Exception:
            pass
        self.cursor_pos = max(0, self.cursor_pos - 1)
        self.update_display()
        return "break"

    def _arrow_right(self, event=None):
        try:
            if self.display is self.root.focus_get():
                self.root.after_idle(self._sync_cursor_from_widget)
                return None
        except Exception:
            pass
        self.cursor_pos = min(len(self.expression), self.cursor_pos + 1)
        self.update_display()
        return "break"

    def _cursor_home(self):
        self.cursor_pos = 0
        self.update_display()
        return "break"

    def _cursor_end(self):
        self._move_cursor_to_end()
        self.update_display()
        return "break"

    def keyboard_input(self, event):
        # Ignore navigation keys handled separately (arrows/home/end already bound)
        if event.keysym in ("Left", "Right", "Up", "Down", "Home", "End",
                            "BackSpace", "Delete", "Return", "KP_Enter", "Escape"):
            if event.keysym == "Escape":
                self.clear()
            return None

        key = event.char

        if key in "0123456789.+-*/()%!":
            self._sync_cursor_from_widget_if_focused()
            # cursor-aware guards
            if self.cursor_pos == 0 and key in "*/%)!^":
                return "break"
            ch = self._char_before_cursor()
            if ch and key in "*/%^" and ch in "+-*/^(%":
                return "break"
            self._insert_at_cursor(key)
            self._clear_answer_preview()
            self.update_display()
            return "break"

        if key == "^":
            self._sync_cursor_from_widget_if_focused()
            self._insert_at_cursor("^")
            self._clear_answer_preview()
            self.update_display()
            return "break"

        if key == "=":
            self.calculate()
            return "break"



# ================================================================
# APPLICATION
# ================================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = ScientificCalculator(root)

    root.mainloop()
