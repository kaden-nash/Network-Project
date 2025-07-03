import tkinter as tk
from PIL import Image, ImageTk
import os.path as path
from os import getcwd
import uuid

class Frontend:
    def __init__(self, root: tk.Tk):
        self.root = root
        self._render_background()
        self._init_Textboxes()

        # entry messages
        self.sidebar_Textbox.insert_text("Connected hosts:\n\n")
        self.chatbar_Textbox.insert_text("Enter message here", "chatbar")

        # FIXME: Delete this and configure function once done testing tags
        self.chatbar_Textbox.get_widget().tag_config(tagName=self.chatbar_Textbox.tag_ids[0], font=("Consolas", 10, "italic"), foreground="#9B9696")
        self.chatbar_Textbox.get_widget().tag_bind(tagName=self.chatbar_Textbox.tag_ids[0], sequence="<Button-1>", func=self.configure)
    
    def configure(self, event):
        self.chatbar_Textbox.get_widget().tag_remove(tagName=self.chatbar_Textbox.tag_ids[0], index1="1.0", index2=tk.END)
        self.chatbar_Textbox.clear_text()


    def _render_background(self):
        SCREEN_W = self.root.winfo_screenwidth()
        SCREEN_H = self.root.winfo_screenheight()
        self.WIDTH = int(SCREEN_W/2)
        self.HEIGHT = int(SCREEN_H - 80)

        # define parent window
        self.root.title("ChatApp - A Networking Project")
        self.root.geometry(f"{self.WIDTH}x{self.HEIGHT}+0+0") # +0+0 puts the tab in the top left of the screen
        self.root.resizable(width=True, height=True)

        # establish sizing standards for .grid()
        self.root.grid_columnconfigure(0, weight=1, minsize=50) # weight establishes porportion of size for each col
        self.root.grid_columnconfigure(1, weight=3, minsize=180)
        self.root.grid_rowconfigure(0, weight=10, minsize=180)
        self.root.grid_rowconfigure(1, weight=0, minsize=40) # by setting weight = 0 and minsize = 20, you effectively est the height of this row to be 20 and it will never change

        # setup frames
        self.chatbox_frame = tk.Frame(self.root, bg="#2f2f32")
        self.chatbar_frame = tk.Frame(self.root, bg="#36363a")
        self.sidebar_frame = tk.Frame(self.root, bg="#27272a")
        self.chatbox_frame.grid(row=0, column=1, sticky="NSEW")
        self.chatbar_frame.grid(row=1, column=1, sticky="NSEW")
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="NSEW") # sticky="NSEW" expands frame to all sides of cell in grid (and color on frame)

        root.update_idletasks() # ensures geometry is determined for other calculations to come


    def _init_Textboxes(self) -> None:
        self.chatbox_Textbox = Textbox(self.chatbox_frame)
        self.chatbar_Textbox = Textbox(self.chatbar_frame, state=tk.NORMAL)
        self.sidebar_Textbox = Textbox(self.sidebar_frame)
        self.chatbox_Textbox.pack()
        self.chatbar_Textbox.pack()
        self.sidebar_Textbox.pack()
        h_pad = 15
        v_pad = 25
        send_button = self._add_send_button()
        send_button.pack(padx=h_pad, pady=v_pad)

    def _add_send_button(self) -> tk.Button:
        self.image_path = path.join(getcwd(), "discordSendButtonChatBarColored.png")
        self.pil_image = Image.open(self.image_path)
        self.pil_image = self.pil_image.resize((40, 40))
        self.tk_image = ImageTk.PhotoImage(self.pil_image)
        color = self.chatbar_frame.cget("bg")
        image_button = tk.Button(
            self.chatbar_frame,
            image=self.tk_image,
            bd=0, # removes border of button
            highlightthickness=0, # removes border of button but more?
            activebackground=color,
            activeforeground=color,
            disabledforeground=color,
            background=color,
            fg=color,
            relief=tk.FLAT,
            overrelief=tk.FLAT,
        )
        return image_button

    def add_host_to_sidebar(self, host: str) -> None:
        pass
    
    def add_message_to_chatbox(self, msg: str) -> None:
        pass

    def _on_send_press(self) -> None:
        pass

class Textbox:
    def __init__(self, frame: tk.Frame, **kwargs) -> None:
        self._frame = frame
        self._opts = self.get_opts(**kwargs)
        self._box = tk.Text(self._frame, **self._opts)
        self._tags = []

    def get_opts(self, **kwargs: dict[str,]) -> tuple[dict[str,], dict[str,]]:
        # define default opts
        pad = 3
        color = self._frame.cget("bg") # gets color of frame
        box_w = int(self._frame.winfo_width() / 15) # self._frame_w / 15
        box_h = int(self._frame.winfo_height() / 7)
        default_opts = {
            "width": box_w,
            "height": box_h,
            "wrap": tk.WORD,
            "state": tk.DISABLED,
            "font": ("Consolas", 10),
            "padx": pad,
            "pady": pad,
            "bd": 0,
            "bg": color,
            "fg": "#D3D3D3",
            "insertbackground": "#D3D3D3"
        }
        
        # compile cur_opts
        cur_opts = default_opts.copy()
        cur_opts.update(kwargs)

        return cur_opts

    def pack(self) -> None:
        self._box.pack( 
            side=tk.LEFT, 
            fill=tk.BOTH,
            expand=True,
            padx=5,
            pady=5,
            )

    def insert_text(self, text: str, tag_prefix: str = 'default') -> None:
        tag_id = self._gen_tag(tag_prefix)
        self._tags.append(tag_id)

        orig_state = self._get_state()
        if orig_state == tk.DISABLED:
            self._box.configure(state=tk.NORMAL) # enable editing text of widget
        
        self._box.insert(tk.END, text, tag_id)
        self._box.tag_add(tag_id, tk.INSERT, tk.END)
        self._box.see(tk.END) # scroll to end of text

        if orig_state == tk.DISABLED:
            self._box.configure(state=tk.DISABLED) # Disable the widget

    def _gen_tag(self, prefix: str = 'default') -> str:
        return f"{prefix}_{uuid.uuid4().hex[:8]}" # don't need huge number

    def get_text(self) -> str:
        return self._box.get("1.0", tk.END).strip()

    def clear_text(self) -> None:
        orig_state = self._get_state()

        if orig_state == tk.DISABLED:
            self._box.configure(state=tk.NORMAL) # enable editing text of widget

        self._box.delete("1.0", tk.END)

        if orig_state == tk.DISABLED:
            self._box.configure(state=tk.DISABLED) # Disable the widget


    def _get_state(self) -> any:
        return self._box.cget("state")

    @property
    def tag_ids(self) -> list:
        return self._tags

    def get_widget(self) -> tk.Text:
        return self._box
    
        

if __name__ == "__main__":
    root = tk.Tk()
    front = Frontend(root)
    root.mainloop()
