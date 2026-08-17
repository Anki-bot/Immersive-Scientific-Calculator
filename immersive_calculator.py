import tkinter as tk
from tkinter import messagebox
import math
import re


class ScientificCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Immersive Scientific Calculator")
        self.root.geometry("1100x720")
        self.root.minsize(850, 600)
        self.root.configure(bg="#08090d")

        self.expression = ""
        self.answer = 0
        self.memory = 0
        self.angle_mode = "DEG"
        self.history = []

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
            relwidth=0.92,
            relheight=0.88
        )

        # --------------------------------------------------------
        # LEFT SIDE
        # --------------------------------------------------------

        self.left = tk.Frame(
            self.main,
            bg="#0c0e14"
        )

        self.left.pack(
            side="left",
            fill="both",
            expand=True,
            padx=25,
            pady=25
        )

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

        self.mode_label = tk.Label(
            self.display_frame,
            text="DEG",
            font=("Helvetica", 10, "bold"),
            fg="#65d9ff",
            bg="#10131b"
        )

        self.mode_label.pack(
            anchor="e",
            padx=18,
            pady=(12, 0)
        )

        self.display = tk.Label(
            self.display_frame,
            text="0",
            font=("Helvetica", 32, "bold"),
            fg="#ffffff",
            bg="#10131b",
            anchor="e"
        )

        self.display.pack(
            fill="x",
            padx=18,
            pady=(4, 4)
        )

        self.answer_label = tk.Label(
            self.display_frame,
            text="",
            font=("Helvetica", 14),
            fg="#687185",
            bg="#10131b",
            anchor="e"
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

        self.create_button(
            mode_frame,
            "DEG",
            self.set_degree,
            width=6,
            color="#65d9ff"
        ).pack(side="left", padx=3)

        self.create_button(
            mode_frame,
            "RAD",
            self.set_radian,
            width=6
        ).pack(side="left", padx=3)

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
                    color = "#dce1eb"

                button = self.create_button(
                    keypad,
                    text,
                    lambda value=text: self.button_press(value),
                    color=color
                )

                button.grid(
                    row=r,
                    column=c,
                    sticky="nsew",
                    padx=4,
                    pady=4
                )

        # --------------------------------------------------------
        # RIGHT SCIENTIFIC PANEL
        # --------------------------------------------------------

        self.right = tk.Frame(
            self.main,
            bg="#10131a",
            highlightbackground="#252936",
            highlightthickness=1
        )

        self.right.pack(
            side="right",
            fill="both",
            padx=(0, 25),
            pady=25
        )

        tk.Label(
            self.right,
            text="SCIENTIFIC",
            font=("Helvetica", 11, "bold"),
            fg="#7e879c",
            bg="#10131a"
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 5)
        )

        scientific = tk.Frame(
            self.right,
            bg="#10131a"
        )
        scientific.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=10
        )

        scientific_buttons = [
            ["sin", "cos", "tan"],
            ["asin", "acos", "atan"],
            ["log", "ln", "exp"],
            ["√", "x²", "xʸ"],
            ["π", "e", "n!"],
            ["abs", "mod", "1/x"],
            ["sinh", "cosh", "tanh"],
            ["MC", "MR", "M+"],
            ["M−", "RAND", "ANS"]
        ]

        for r, row in enumerate(scientific_buttons):
            scientific.rowconfigure(r, weight=1)

            for c, text in enumerate(row):
                scientific.columnconfigure(c, weight=1)

                btn = self.create_button(
                    scientific,
                    text,
                    lambda value=text: self.scientific_press(value),
                    color="#c7d2fe"
                )

                btn.grid(
                    row=r,
                    column=c,
                    sticky="nsew",
                    padx=4,
                    pady=4
                )

        # --------------------------------------------------------
        # HISTORY
        # --------------------------------------------------------

        history_frame = tk.Frame(
            self.right,
            bg="#0b0d12",
            highlightbackground="#252936",
            highlightthickness=1
        )

        history_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(5, 15)
        )

        tk.Label(
            history_frame,
            text="HISTORY",
            font=("Helvetica", 9, "bold"),
            fg="#697386",
            bg="#0b0d12"
        ).pack(
            anchor="w",
            padx=12,
            pady=8
        )

        self.history_list = tk.Listbox(
            history_frame,
            bg="#0b0d12",
            fg="#dce1eb",
            selectbackground="#20283a",
            selectforeground="#ffffff",
            borderwidth=0,
            highlightthickness=0,
            font=("Menlo", 10)
        )

        self.history_list.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

        self.history_list.bind(
            "<Double-Button-1>",
            self.load_history
        )

    # ============================================================
    # BUTTON CREATION
    # ============================================================

    def create_button(
        self,
        parent,
        text,
        command,
        width=None,
        color="#dce1eb"
    ):

        bg = "#171b25"

        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Helvetica", 12, "bold"),
            fg=color,
            bg=bg,
            activeforeground="#ffffff",
            activebackground="#272d3c",
            relief="flat",
            bd=0,
            cursor="hand2"
        )

        if width:
            button.configure(width=width)

        button.bind(
            "<Enter>",
            lambda e: button.configure(
                bg="#232938"
            )
        )

        button.bind(
            "<Leave>",
            lambda e: button.configure(
                bg=bg
            )
        )

        return button

    # ============================================================
    # BASIC INPUT
    # ============================================================

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
            self.expression += str(self.answer)
        else:
            self.expression += value

        self.update_display()

    # ============================================================
    # SCIENTIFIC INPUT
    # ============================================================

    def scientific_press(self, value):

        if value == "MC":
            self.memory = 0
            return

        if value == "MR":
            self.expression += str(self.memory)
            self.update_display()
            return

        if value == "M+":
            try:
                self.memory += self.evaluate(self.expression)
            except:
                pass
            return

        if value == "M−":
            try:
                self.memory -= self.evaluate(self.expression)
            except:
                pass
            return

        if value == "RAND":
            import random
            self.expression += str(random.random())
            self.update_display()
            return

        if value == "ANS":
            self.expression += str(self.answer)
            self.update_display()
            return

        mappings = {
            "sin": "sin(",
            "cos": "cos(",
            "tan": "tan(",

            "asin": "asin(",
            "acos": "acos(",
            "atan": "atan(",

            "sinh": "sinh(",
            "cosh": "cosh(",
            "tanh": "tanh(",

            "log": "log(",
            "ln": "ln(",
            "exp": "exp(",

            "√": "sqrt(",
            "x²": "^2",
            "xʸ": "^",

            "π": "pi",
            "e": "e",

            "n!": "!",
            "abs": "abs(",
            "mod": "%",
            "1/x": "inv("
        }

        if value in mappings:
            self.expression += mappings[value]

        self.update_display()

    # ============================================================
    # DISPLAY
    # ============================================================

    def update_display(self):

        text = self.expression if self.expression else "0"

        text = (
            text.replace("*", "×")
            .replace("/", "÷")
            .replace("-", "−")
        )

        self.display.configure(
            text=text
        )

    # ============================================================
    # CALCULATION
    # ============================================================

    def calculate(self):

        if not self.expression:
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

            self.answer_label.configure(
                text=f"= {formatted}"
            )

            self.expression = str(result)

        except Exception:
            self.answer_label.configure(
                text="Invalid expression"
            )

    # ============================================================
    # EVALUATION ENGINE
    # ============================================================

    def evaluate(self, expression):

        expression = expression.replace(" ", "")

        expression = expression.replace("×", "*")
        expression = expression.replace("÷", "/")
        expression = expression.replace("−", "-")

        expression = expression.replace("^", "**")

        # Percentage
        expression = re.sub(
            r"(\d+(?:\.\d+)?)%",
            r"(\1/100)",
            expression
        )

        # Factorial
        while "!" in expression:

            expression = re.sub(
                r"(\d+(?:\.\d+)?)!",
                r"factorial(\1)",
                expression
            )

        # Mathematical environment
        env = {
            "__builtins__": {},

            "pi": math.pi,
            "e": math.e,

            "sin": self.sin,
            "cos": self.cos,
            "tan": self.tan,

            "asin": self.asin,
            "acos": self.acos,
            "atan": self.atan,

            "sinh": math.sinh,
            "cosh": math.cosh,
            "tanh": math.tanh,

            "sqrt": math.sqrt,

            "log": math.log10,
            "ln": math.log,

            "exp": math.exp,

            "abs": abs,

            "factorial": math.factorial,

            "inv": lambda x: 1 / x
        }

        return eval(
            expression,
            env
        )

    # ============================================================
    # TRIGONOMETRY
    # ============================================================

    def convert_angle(self, x):

        if self.angle_mode == "DEG":
            return math.radians(x)

        if self.angle_mode == "GRAD":
            return x * math.pi / 200

        return x

    def convert_result(self, x):

        if self.angle_mode == "DEG":
            return math.degrees(x)

        if self.angle_mode == "GRAD":
            return x * 200 / math.pi

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

    def set_radian(self):
        self.angle_mode = "RAD"
        self.mode_label.configure(
            text="RAD"
        )

    # ============================================================
    # CLEAR / DELETE
    # ============================================================

    def clear(self):
        self.expression = ""
        self.answer_label.configure(
            text=""
        )
        self.update_display()

    def backspace(self):

        if self.expression:
            self.expression = self.expression[:-1]

        self.update_display()

    # ============================================================
    # HISTORY
    # ============================================================

    def load_history(self, event=None):

        selection = self.history_list.curselection()

        if not selection:
            return

        index = selection[0]

        if index < len(self.history):

            expression, result = self.history[index]

            self.expression = expression

            self.update_display()

    # ============================================================
    # FORMAT RESULT
    # ============================================================

    def format_result(self, value):

        if isinstance(value, float):

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

        self.root.bind(
            "<Key>",
            self.keyboard_input
        )

    def keyboard_input(self, event):

        key = event.char

        if key in "0123456789.+-*/()%":

            self.expression += key
            self.update_display()

        elif key == "^":

            self.expression += "^"
            self.update_display()

        elif event.keysym == "Return":

            self.calculate()

        elif event.keysym == "BackSpace":

            self.backspace()

        elif event.keysym == "Escape":

            self.clear()


# ================================================================
# APPLICATION
# ================================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = ScientificCalculator(root)

    root.mainloop()