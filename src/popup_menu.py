from customtkinter import CTkToplevel, CTkFrame


class CTkPopupMenu(CTkToplevel):
    def __init__(self, master=None, width=150, height=100, corner_radius=8, border_width=1, **kwargs):
        super().__init__(takefocus=1)

        self.master_window = master
        self.width = width
        self.height = height
        self.corner = corner_radius
        self.border = border_width
        self.hidden = True
        self.focus()

        self.after(100, self._make_transparent())

        self.frame = CTkFrame(self, bg_color=self.transparent_color, corner_radius=self.corner,
                              border_width=self.border, **kwargs)
        self.frame.pack(expand=True, fill="both")

        self.master.bind("<ButtonPress>", lambda event: self._withdraw_off(), add="+")
        self.bind("<Button-1>", lambda event: self._withdraw(), add="+")
        self.master.bind("<Configure>", lambda event: self._withdraw(), add="+")

        self.resizable(False, False)
        self.transient(self.master_window)
        self.withdraw()

    def _make_transparent(self):
        self.overrideredirect(True)
        self.transparent_color = self._apply_appearance_mode(self._fg_color)
        self.attributes("-transparentcolor", self.transparent_color)

    def _withdraw(self):
        self.withdraw()
        self.hidden = True

    def _withdraw_off(self):
        if self.hidden:
            self.withdraw()
        self.hidden = True

    def popup(self, event):
        self.geometry(f'{self.width}x{self.height}+{event.x_root}+{event.y_root}')
        self.deiconify()
        self.focus()
        self.hidden = False

