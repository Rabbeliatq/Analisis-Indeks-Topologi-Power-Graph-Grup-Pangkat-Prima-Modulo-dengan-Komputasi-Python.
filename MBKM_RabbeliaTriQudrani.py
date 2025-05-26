# -*- coding: utf-8 -*-
"""
Created on Mon May 12 20:41:06 2025

@author: rabbe
"""
import tkinter as tk
from tkinter import messagebox, ttk, PanedWindow, HORIZONTAL
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from math import gcd
from itertools import product


FONT_NORMAL = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 11, "bold")
BG_COLOR = "#f5f7fa"
PRIMARY_COLOR = "#2c3e50"
SECONDARY_COLOR = "#34495e"
ACCENT_COLOR = "#3498db"
BUTTON_COLORS = {
    "calculate": "#800000",
    "plot": "#800000",
    "graph": "#800000",
    "default": "#800000",
    "next": "#800000"
}
ENTRY_BG = "white"
FRAME_BG = "#ecf0f1"
BORDER_COLOR = "#bdc3c7"
CARD_PADDING = 10


MAX_K_VALUE = 5

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def modulo_group(p, k):
    mod = p**k
    return [x for x in range(1, mod) if gcd(x, mod) == 1]

def is_power(u, v, mod):
    if u == 1 and v != 1:
        return False
    x = u
    while x != 1:
        x = (x * u) % mod
        if x == v:
            return True
    return v == 1 and u == 1

def power_graph(p, k):
    mod = p**k
    elements = modulo_group(p, k)
    G = nx.Graph()
    G.add_nodes_from(elements)

    for u, v in product(elements, repeat=2):
        if u != v and (is_power(u, v, mod) or is_power(v, u, mod)):
            G.add_edge(u, v)
    return G

def first_zagreb_index(G):
    return sum(d**2 for _, d in G.degree()) if G else 0

def wiener_index(G):
    if not G or not G.edges():
        return 0
    wiener_sum = 0
    nodes = list(G.nodes())
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            try:
                d = nx.shortest_path_length(G, source=nodes[i], target=nodes[j])
                wiener_sum += d
            except nx.NetworkXNoPath:
                continue
    return wiener_sum

def gutman_index(G):
    if not G or not G.edges():
        return 0
    gutman_sum = 0
    for i, u in enumerate(G.nodes()):
        for j, v in enumerate(G.nodes()):
            if i < j:
                try:
                    d = nx.shortest_path_length(G, source=u, target=v)
                    gutman_sum += d * G.degree[u] * G.degree[v]
                except nx.NetworkXNoPath:
                    continue
    return gutman_sum

def compute_indices(p, k_val, selected_indices):
    try:
        # Special case for p=2 and k=1
        if p == 2 and k_val == 1:
            return {"zagreb": 0, "wiener": 0, "gutman": 0}
            
        G = power_graph(p, k_val)
        results = {}
        if "zagreb" in selected_indices:
            results["zagreb"] = first_zagreb_index(G)
        if "wiener" in selected_indices:
            results["wiener"] = wiener_index(G)
        if "gutman" in selected_indices:
            results["gutman"] = gutman_index(G)
        return results
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return None
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while calculating indices: {e}")
        return None

def show_graph_in_tab(parent, G, p, k):
    if p == 2 and k == 1:
        # Special case for p=2 and k=1
        info_label = tk.Label(parent, text="Graph cannot be visualized for p=2 and k=1\nbecause the modulo group Z_(2^1)* is empty", 
                             font=FONT_NORMAL, bg=FRAME_BG)
        info_label.pack(pady=50)
        return
    
    if G and len(G.nodes()) > 0:
        fig = Figure(figsize=(6, 5), dpi=100)
        ax = fig.add_subplot(111)
        pos = nx.circular_layout(G)
        nx.draw(G, pos, with_labels=True, node_color=ACCENT_COLOR, 
                edge_color=PRIMARY_COLOR, node_size=600, 
                font_size=9, ax=ax, width=1.5)
        ax.set_title(f"Power Graph of Z_({p}^{k})*", fontsize=10)
        ax.set_facecolor(FRAME_BG)
        fig.patch.set_facecolor(FRAME_BG)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        canvas.draw()
    else:
        messagebox.showinfo("Info", "Graph cannot be created for this k value because the modulo group is empty.")

def plot_indices_in_tab(parent, p, k_max, selected_indices):
    index_values = {index: [] for index in selected_indices}
    n_values = list(range(1, k_max + 1))

    for i in n_values:
        results = compute_indices(p, i, selected_indices)
        if results:
            for index in selected_indices:
                index_values[index].append(results[index])

    if n_values and any(index_values.values()):
        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
        
        index_styles = {
            "zagreb": {"color": "#e74c3c", "marker": "o", "label": "First Zagreb Index"},
            "wiener": {"color": "#2ecc71", "marker": "s", "label": "Wiener Index"},
            "gutman": {"color": "#f39c12", "marker": "^", "label": "Gutman Index"}
        }
        
        for index in selected_indices:
            if index_values[index]:
                style = index_styles[index]
                ax.plot(n_values, index_values[index], 
                        marker=style["marker"], linestyle='-', 
                        color=style["color"], 
                        label=style["label"])
        
        ax.set_xlabel("k (Prime Exponent)", fontsize=9)
        ax.set_ylabel("Graph Index Value", fontsize=9)
        ax.set_title(f"Index Changes for Power Graph Z_({p}^k)*", fontsize=10)
        ax.legend(fontsize=9)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.set_facecolor(FRAME_BG)
        fig.patch.set_facecolor(FRAME_BG)

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        canvas.draw()
    else:
        messagebox.showinfo("Info", "Not enough data to display index changes graph.")

def calculate_indices_action():
    try:
        p = int(prime_entry.get())
        k = int(exponent_entry.get())
        if not is_prime(p):
            messagebox.showerror("Error", "Prime must be a prime number ≥ 2")
            return
        if k < 1 or k > MAX_K_VALUE:
            messagebox.showerror("Error", f"Exponent (k) must be between 1 and {MAX_K_VALUE}!")
            return

        selected_indices = []
        if zagreb_var.get():
            selected_indices.append("zagreb")
        if wiener_var.get():
            selected_indices.append("wiener")
        if gutman_var.get():
            selected_indices.append("gutman")
            
        if not selected_indices:
            messagebox.showwarning("Warning", "Select at least one index to calculate!")
            return

        results = compute_indices(p, k, selected_indices)

        if results:
            result_text = f"Calculation results for p={p}, k={k}:\n\n"
            
            # Special case handling for p=2 and k=1
            if p == 2 and k == 1:
                result_text += "• Special case: p=2 and k=1\n"
                result_text += "• All indices are 0 because the modulo group Z_(2^1)* is empty\n\n"
            else:
                if "zagreb" in results:
                    result_text += f"• First Zagreb Index: {results['zagreb']}\n"
                if "wiener" in results:
                    result_text += f"• Wiener Index: {results['wiener']}\n"
                if "gutman" in results:
                    result_text += f"• Gutman Index: {results['gutman']}\n"
            
            if k > 1:
                result_text += f"\nCalculation history from k=1 to k={k}:\n"
                for current_k in range(1, k + 1):
                    range_results = compute_indices(p, current_k, selected_indices)
                    if range_results:
                        if p == 2 and current_k == 1:
                            result_text += f"\nk=1 (p=2):\n"
                            result_text += "  • Modulo group is empty, all indices = 0\n"
                            continue
                            
                        result_text += f"\nk={current_k}:\n"
                        if "zagreb" in range_results:
                            result_text += f"  • First Zagreb: {range_results['zagreb']}\n"
                        if "wiener" in range_results:
                            result_text += f"  • Wiener: {range_results['wiener']}\n"
                        if "gutman" in range_results:
                            result_text += f"  • Gutman: {range_results['gutman']}\n"
            
            result_var.set(result_text)
        else:
            result_var.set("Failed to calculate indices.")

    except ValueError:
        messagebox.showerror("Error", "Enter valid Prime and Exponent (k) values!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def show_graph_action():
    try:
        p = int(prime_entry.get())
        k = int(exponent_entry.get())
        if not is_prime(p):
            messagebox.showerror("Error", "Prime number must be ≥ 2")
            return
        if k < 1 or k > MAX_K_VALUE:
            messagebox.showerror("Error", f"Exponent (k) must be between 1 and {MAX_K_VALUE}!")
            return
            
        for widget in graph_tab.winfo_children():
            widget.destroy()
            
        if p == 2 and k == 1:
            info_label = tk.Label(graph_tab, 
                                text="Graph cannot be visualized for p=2 and k=1\nbecause the modulo group Z_(2^1)* is empty", 
                                font=FONT_NORMAL, bg=FRAME_BG)
            info_label.pack(pady=50)
            return
            
        G = power_graph(p, k)
        show_graph_in_tab(graph_tab, G, p, k)
        
    except ValueError as e:
        messagebox.showerror("Error", f"Error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while visualizing graph: {e}")

def plot_indices_action():
    try:
        p = int(prime_entry.get())
        k = int(exponent_entry.get())
        
        if not is_prime(p):
            messagebox.showerror("Error", "Prime number must be ≥ 2")
            return
        if k < 1 or k > MAX_K_VALUE:
            messagebox.showerror("Error", f"Exponent (k) must be between 1 and {MAX_K_VALUE}!")
            return
            
        selected_indices = []
        if zagreb_var.get():
            selected_indices.append("zagreb")
        if wiener_var.get():
            selected_indices.append("wiener")
        if gutman_var.get():
            selected_indices.append("gutman")
            
        if not selected_indices:
            messagebox.showwarning("Warning", "Select at least one index to plot!")
            return

        for widget in index_tab.winfo_children():
            widget.destroy()
        plot_indices_in_tab(index_tab, p, k, selected_indices)
    except ValueError as e:
        messagebox.showerror("Error", f"Error: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while creating plot: {e}")

window = tk.Tk()
window.title("Power Graph Group Modulo With Topological Index Analyzer")
window.geometry("1000x650")
window.configure(bg=BG_COLOR)

style = ttk.Style()
style.theme_use('clam')

style.configure('TFrame', background=FRAME_BG)
style.configure('TLabel', background=FRAME_BG, font=FONT_NORMAL)
style.configure('TLabelFrame', background=FRAME_BG, relief=tk.FLAT, borderwidth=1)
style.configure('TLabelFrame.Label', background=FRAME_BG, font=FONT_BOLD)
style.configure('TNotebook', background=FRAME_BG)
style.configure('TNotebook.Tab', background=BG_COLOR, padding=[8, 4], font=FONT_BOLD)
style.map('TNotebook.Tab', background=[('selected', PRIMARY_COLOR)], foreground=[('selected', 'white')])

style.configure('Calculate.TButton', 
                background=BUTTON_COLORS["calculate"],
                foreground='white',
                font=FONT_BOLD,
                padding=6,
                borderwidth=1)
style.configure('Plot.TButton', 
                background=BUTTON_COLORS["plot"],
                foreground='white',
                font=FONT_BOLD,
                padding=6,
                borderwidth=1)
style.configure('Graph.TButton', 
                background=BUTTON_COLORS["graph"],
                foreground='white',
                font=FONT_BOLD,
                padding=6,
                borderwidth=1)

main_pane = PanedWindow(window, orient=HORIZONTAL, bg=BG_COLOR, sashwidth=3, sashrelief=tk.RAISED)
main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

left_pane = ttk.Frame(main_pane, padding=(15, 15, 10, 15), style='TFrame')
left_pane.grid_rowconfigure(0, weight=1)
left_pane.grid_columnconfigure(0, weight=1)

header_frame = ttk.Frame(left_pane, style='TFrame')
header_frame.pack(fill=tk.X, pady=(0, 15))
ttk.Label(header_frame, text="Power Graph Group Modulo With Topological Index Analyzer", font=FONT_TITLE, 
         foreground=PRIMARY_COLOR).pack(side=tk.LEFT)

input_card = ttk.LabelFrame(left_pane, text="Input Parameters", padding=15)
input_card.pack(fill=tk.BOTH, expand=True)

input_grid = ttk.Frame(input_card)
input_grid.pack(fill=tk.BOTH, expand=True)

ttk.Label(input_grid, text="Prime Number (p):").grid(row=0, column=0, sticky="w", pady=(0, 5))
prime_entry = ttk.Entry(input_grid, width=20, font=FONT_NORMAL)
prime_entry.grid(row=1, column=0, sticky="we", pady=(0, 15))

ttk.Label(input_grid, text=f"Exponent (k) (1-{MAX_K_VALUE}):").grid(row=2, column=0, sticky="w", pady=(0, 5))
exponent_entry = ttk.Entry(input_grid, width=20, font=FONT_NORMAL)
exponent_entry.grid(row=3, column=0, sticky="we", pady=(0, 15))

indices_frame = ttk.LabelFrame(input_grid, text="Select Indices", padding=(10, 5, 10, 10))
indices_frame.grid(row=4, column=0, sticky="we", pady=(5, 15))

zagreb_var = tk.BooleanVar(value=True)
wiener_var = tk.BooleanVar(value=True)
gutman_var = tk.BooleanVar(value=True)

ttk.Checkbutton(indices_frame, text="First Zagreb Index", variable=zagreb_var).pack(anchor="w", pady=3)
ttk.Checkbutton(indices_frame, text="Wiener Index", variable=wiener_var).pack(anchor="w", pady=3)
ttk.Checkbutton(indices_frame, text="Gutman Index", variable=gutman_var).pack(anchor="w", pady=3)

button_frame = ttk.Frame(left_pane)
button_frame.pack(fill=tk.X, pady=(10, 0))

calculate_button = ttk.Button(button_frame, text="Calculate Indices", command=calculate_indices_action, style='Calculate.TButton')
calculate_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

graph_button = ttk.Button(button_frame, text="Show Graph", command=show_graph_action, style='Graph.TButton')
graph_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

plot_button = ttk.Button(button_frame, text="Plot Graph", command=plot_indices_action, style='Plot.TButton')
plot_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
main_pane.add(left_pane)

right_pane = ttk.Frame(main_pane, padding=(10, 15, 15, 15), style='TFrame')
notebook_right = ttk.Notebook(right_pane)
notebook_right.pack(fill=tk.BOTH, expand=True)

results_tab = ttk.Frame(notebook_right)
results_container = ttk.Frame(results_tab, padding=10)
results_container.pack(fill=tk.BOTH, expand=True)

result_var = tk.StringVar()
result_label = tk.Label(results_container, textvariable=result_var, relief=tk.FLAT, 
                      padx=15, pady=15, anchor="nw", justify="left",
                      bg="white", font=FONT_NORMAL, wraplength=400,
                      highlightbackground=BORDER_COLOR, highlightthickness=1)
result_label.pack(fill=tk.BOTH, expand=True)

notebook_right.add(results_tab, text='Results')

graph_tab = ttk.Frame(notebook_right)
notebook_right.add(graph_tab, text='Graph Visualization')

index_tab = ttk.Frame(notebook_right)
notebook_right.add(index_tab, text='Index Analysis')
main_pane.add(right_pane)

status_bar = ttk.Frame(window, height=25, relief=tk.SUNKEN)
status_bar.pack(fill=tk.X, side=tk.BOTTOM)
status_label = ttk.Label(status_bar, text="Ready", font=FONT_NORMAL, foreground="#7f8c8d")
status_label.pack(side=tk.LEFT, padx=10)

def show_tooltip(widget, text):
    tooltip = tk.Toplevel(widget)
    tooltip.wm_overrideredirect(True)
    tooltip.wm_geometry(f"+{widget.winfo_rootx()}+{widget.winfo_rooty() + widget.winfo_height() + 5}")
    label = ttk.Label(tooltip, text=text, background="#ffffe0", relief="solid", 
                     borderwidth=1, padding=(5, 2), font=FONT_NORMAL)
    label.pack()
    widget.tooltip = tooltip
    widget.bind("<Leave>", lambda e: tooltip.destroy())

prime_entry.bind("<Enter>", lambda e: show_tooltip(prime_entry, "Enter a prime number (e.g., 2, 3, 5, 7)"))
exponent_entry.bind("<Enter>", lambda e: show_tooltip(exponent_entry, f"Enter exponent between 1-{MAX_K_VALUE}"))
prime_entry.focus_set()
window.mainloop()