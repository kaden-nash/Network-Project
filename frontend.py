import tkinter as tk
import tkinter.scrolledtext as scrolledtext

root = tk.Tk()

WIDTH = 628
HEIGHT = 700

# define parent window
root.title("ChatApp - A Networking Project")
root.geometry(f"{WIDTH}x{HEIGHT}")
root.resizable(width=True, height=True)

# establish sizing standards for .grid()
root.grid_columnconfigure(0, weight=1, minsize=30) # weight establishes porportion of size for each col
root.grid_columnconfigure(1, weight=8, minsize=180)
root.grid_columnconfigure(2, weight=1, minsize=30)

root.grid_rowconfigure(0, weight=10, minsize=180)
root.grid_rowconfigure(1, weight=0, minsize=40) # by setting weight = 0 and minsize = 20, you effectively est the height of this row to be 20 and it will never change

# create frames
left_frame = tk.Frame(root, bg="#27272a")
right_frame = tk.Frame(root, bg="#27272a")
top_mid_frame = tk.Frame(root, bg="#2f2f32")
bottom_mid_frame = tk.Frame(root, bg="#2f2f32")

# place frames
left_frame.grid(row=0, column=0, rowspan=2, sticky="NSEW") # stickey="NSEW" frame expand to all sides of cell in grid
right_frame.grid(row=0, column=2, rowspan=2, sticky="NSEW")
top_mid_frame.grid(row=0, column=1, sticky="NSEW")
bottom_mid_frame.grid(row=1, column=1, sticky="NSEW")

# place something in frames so they don't collapse to 1x1
# left_label = tk.Label(left_frame, wraplength=20, text="this is the left frame", bg="white")
# right_label = tk.Label(right_frame, wraplength=20, text="this is the right frame", bg="white")
# top_mid_label = tk.Label(top_mid_frame, wraplength=20,text="this is the top_mid frame", bg="white")
# bottom_mid_label = tk.Label(bottom_mid_frame,text="this is the bottom_mid frame", bg="white", fg="blue")

# # pack widgets
# left_label.pack()
# right_label.pack()
# top_mid_label.pack()
# bottom_mid_label.pack(expand=True, fill="both")
# bottom_mid_label.pack()



root.mainloop()
