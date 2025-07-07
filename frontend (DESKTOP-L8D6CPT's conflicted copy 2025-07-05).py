# ./.venv/Scripts/Activate.ps1

# TODO: Ask gemini: since tkinter's main loop is blocking, how could I handle talking with the client via a queue?

import tkinter as tk
from PIL import Image, ImageTk
import os.path as path
from os import getcwd
import uuid

class CurrentHost:
    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
    
    def __str__(self):
        return f"{self.ip}:{self.port}"

class EventBus:
    def __init__(self):
        self._subscribers = {} # key: event_name, value: list of callbacks
    
    def subscribe(self, event_name: str, callback: callable) -> None:
        if event_name not in self._subscribers.keys():
            self._subscribers[event_name] = []

        self._subscribers[event_name].append(callback)
    
    def unsubscribe(self, event_name: str, callback: callable) -> None:
        if event_name not in self._subscribers.keys():
            raise ValueError("Event does not exist.")
        
        self._subscribers[event_name].remove(callback)
    
    def publish(self, event_name: str, *args, **kwargs) -> None:
        if event_name not in self._subscribers.keys():
            raise ValueError("Event does not exist.")

        for func in list(self._subscribers[event_name]): # a copy of the subscriber list to allow callbacks to unsubscribe themselves
            func(*args, **kwargs)

class ClientHandler:
    def __init__(self, cl_host: CurrentHost, eventbus: EventBus):
        self.eventbus = eventbus
        self.eventbus.subscribe("SEND", self.send)
        self.cl_host = cl_host
    
    
    def send(self, text: str, callback) -> None:
        # attempt to send message to server, display only if message got to server

        callback(text, str(self.cl_host)) # add_message to chatbox_Textbox with current IP and host as tag prefix

        # rest of sending logic
    
    def receive(self, callback) -> None:
        callback() # clear ghost text in chatbox_Textbox


class Frontend:
    def __init__(self, root: tk.Tk, eventbus: EventBus):
        self.eventbus = eventbus
        self.root = root
        self._render_background()
        self._init_Textboxes()

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

        self.chatbar_Textbox.create_ghost_text("Enter message here")
        self.chatbar_Textbox.bind("<Button-1>", self.chatbar_Textbox.delete_ghost_text)

        self.chatbox_Textbox.create_ghost_text("Its a ghost town in here...")
        self.eventbus.subscribe("RECEIVED_MESSAGE", self.chatbox_Textbox.delete_ghost_text)

        self.sidebar_Textbox.insert_text("Connected hosts:\n\n", "default_message")

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
            highlightthickness=0, # removes highlight?
            activebackground=color,
            activeforeground=color,
            disabledforeground=color,
            background=color,
            fg=color,
            relief=tk.FLAT,
            overrelief=tk.FLAT,
            command=self._on_send_press
        )
        return image_button

    def add_host(self, host: str) -> None:
        self.sidebar_Textbox.insert_text(host, f"{host}")
    
    def add_message(self, msg: str, sender: str) -> None:
        self.chatbox_Textbox.insert_text(msg, f"{sender}")

    def _on_send_press(self) -> None:
        text = self.chatbar_Textbox.get_text()
        self.eventbus.publish("SEND", text, self.add_message)

        # NOTE: For testing
        # temp = self.chatbox_Textbox.find_tag("127.0.0.1:59000")
        # print(temp)

        self.chatbar_Textbox.clear_text()
        # send text to client for transfer to server
        

def maintain_orig_state(func):
    def wrapper(self, *args, **kwargs):  # *args, **kwargs so that the wrapper will work regardless of the arguments passed into the function
        original_state = self._box.cget("state")

        if original_state == tk.DISABLED:
            self._box.configure(state=tk.NORMAL)

        func(self, *args, **kwargs)

        if original_state == tk.DISABLED:
            self._box.configure(state=tk.NORMAL)
    return wrapper


class Textbox:
    def __init__(self, frame: tk.Frame, **kwargs) -> None:
        self._frame = frame
        self._opts = self.get_opts(**kwargs)
        self._box = tk.Text(self._frame, **self._opts)
        self._tags = []

    # Box
    def get_opts(self, **kwargs: dict[str,]) -> tuple[dict[str,], dict[str,]]:
        # define default opts
        pad = 3
        color = self._frame.cget("bg") # gets color of frame
        box_w = int(self._frame.winfo_width() / 15)
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

    # Text
    @maintain_orig_state
    def insert_text(self, text: str, tag_prefix: str = 'default') -> None:
        tag_id = self._gen_tag_id(tag_prefix)
        self._tags.append(tag_id)

        modded_text = f"{text}\n\n"

        prev_insertion_point = tk.END
        self._box.insert(tk.END, modded_text, tag_id)
        self._box.tag_add(tag_id, prev_insertion_point, tk.END)
        self._box.see(tk.END) 

    def get_text(self) -> str:
        return self._box.get("1.0", tk.END)
    
    def delete_text(self, tag_id: str) -> None:
        i1, i2 = self.tag_ranges(tag_id)
        self.tag_delete(tag_id) # must be done before clearing text
        self._box.delete(i1, i2)

    @maintain_orig_state
    def clear_text(self) -> None:
        self._box.delete("1.0", tk.END)

    def _gen_tag_id(self, prefix: str = 'default') -> str:
        return f"{prefix}_{uuid.uuid4().hex[:8]}" # don't need huge number

    def _get_state(self) -> any:
        return self._box.cget("state")

    def delete_ghost_text(self, *args) -> None:
        name = self.find_tag("ghost_text") 
        self.tag_delete(name)
        self.clear_text()

    def create_ghost_text(self, text: str) -> None:
        self.insert_text(f"{text}", "ghost_text")
        name = self.find_tag("ghost_text")
        self.tag_configure(tag_id=name, font=("Consolas", 10, "italic"), foreground="#8B8787")

    def bind(self, sequence: str, func, add: str = None) -> None:
        self._box.bind(sequence, func, add)

    # Tag
    @property
    def tag_ids(self) -> list:
        return self._tags
    
    def find_tag(self, contains: str) -> str:
        """
        Finds first tag containing {contains}. 

        Returns "" if no tag was found
        """
        for tag in self._tags:
            if contains in tag:
                return tag
        return ""

    def tag_configure(self, tag_id: str, **options) -> None:
        self._box.tag_configure(tag_id, **options)

    @maintain_orig_state
    def tag_remove(self, tag_id: str, index1: str, index2: str = None) -> None:
        if index2:
            self._box.tag_remove(tag_id, index1, index2)
        else:
            self._box.tag_remove(tag_id, index1)

    def tag_bind(self, tag_id: str, sequence: str, func, add: str = None) -> None:
        self._box.tag_bind(tag_id, sequence, func, add)

    def tag_ranges(self, tag_id: str) -> tuple:
        return self._box.tag_ranges(tag_id)

    def tag_names(self, index: str = None) -> tuple:
        if index:
            return self._box.tag_names(index) # if index not defined, gets all tags in Text
        return self._box.tag_names()

    @maintain_orig_state
    def tag_delete(self, *tag_ids: str) -> None: # *tag_ids will unpack any list given to tag_delete
        self._box.tag_delete(*tag_ids)

    def tag_cget(self, tag_name: str, option: str = None):
        if option:
            return self._box.tag_cget(tag_name, option)
        return self._box.tag_cget(tag_name)
        

if __name__ == "__main__":
    root = tk.Tk()
    bus = EventBus()
    host = CurrentHost("127.0.0.1", 59000)
    handler = ClientHandler(host, bus)
    front = Frontend(root, bus)
    root.mainloop()

    # NOTE: tags need to be removed before text can be deleted. 
