#!/usr/bin/env python3
"""
Minecraft Coordinates Manager (Tkinter GUI)

Features:
- Profiles (create/delete)
- Each profile can store an optional "seed" string
- Each profile contains any number of named coordinates (name, x, y, z)
- Save/load to cords-data.json (in current directory by default)
- Simple, clean Tkinter UI suitable for Linux

Usage:
    python3 minecraft_coords_manager.py
"""

import json
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog

# Path to save data (current directory). Change if you prefer ~/.config/...
DATA_FILENAME = "cords-data.json"


def load_data(path=DATA_FILENAME):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Validate basic structure
            if not isinstance(data, dict):
                raise ValueError("Top-level JSON not a dict")
            return data
        except Exception as e:
            messagebox.showwarning("Load error", f"Failed to load {path}:\n{e}\nStarting with empty data.")
    return {}  # maps profile_name -> {'seed': str, 'coords': [ {name,x,y,z}, ... ]}


def save_data(data, path=DATA_FILENAME):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Save error", f"Failed to save data:\n{e}")


class CoordManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minecraft Coordinates Manager")
        self.geometry("900x500")
        self.minsize(700, 400)

        # Load
        self.data_path = DATA_FILENAME
        self.data = load_data(self.data_path)

        # UI layout frames
        self.left_frame = ttk.Frame(self, padding=(8, 8))
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.right_frame = ttk.Frame(self, padding=(8, 8))
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._build_left_panel()
        self._build_right_panel()
        self._bind_events()

        # Select first profile if exists
        if self.profile_listbox.size() > 0:
            self.profile_listbox.selection_set(0)
            self.on_profile_select(None)

    # ---------------- Left panel: profiles ----------------
    def _build_left_panel(self):
        lbl = ttk.Label(self.left_frame, text="Profiles", font=("TkDefaultFont", 12, "bold"))
        lbl.pack(anchor=tk.W)

        self.profile_listbox = tk.Listbox(self.left_frame, width=28, activestyle="none")
        self.profile_listbox.pack(fill=tk.Y, expand=True, pady=(6, 6))

        # populate
        self._refresh_profile_listbox()

        btn_frame = ttk.Frame(self.left_frame)
        btn_frame.pack(fill=tk.X, pady=(6, 0))

        self.add_profile_btn = ttk.Button(btn_frame, text="➕ Add", command=self.add_profile)
        self.add_profile_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.delete_profile_btn = ttk.Button(btn_frame, text="🗑️ Delete", command=self.delete_profile)
        self.delete_profile_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Import/Export
        io_frame = ttk.Frame(self.left_frame)
        io_frame.pack(fill=tk.X, pady=(6, 0))

        self.import_btn = ttk.Button(io_frame, text="Import JSON", command=self.import_json)
        self.import_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.export_btn = ttk.Button(io_frame, text="Export JSON", command=self.export_json)
        self.export_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _refresh_profile_listbox(self):
        self.profile_listbox.delete(0, tk.END)
        for name in sorted(self.data.keys(), key=lambda s: s.lower()):
            self.profile_listbox.insert(tk.END, name)

    def add_profile(self):
        name = simpledialog.askstring("New profile", "Enter profile name:", parent=self)
        if not name:
            return
        name = name.strip()
        if name in self.data:
            messagebox.showerror("Error", "Profile already exists.")
            return
        self.data[name] = {"seed": "", "coords": []}
        save_data(self.data, self.data_path)
        self._refresh_profile_listbox()
        # select new one
        idx = list(sorted(self.data.keys(), key=lambda s: s.lower())).index(name)
        self.profile_listbox.selection_clear(0, tk.END)
        self.profile_listbox.selection_set(idx)
        self.profile_listbox.see(idx)
        self.on_profile_select(None)

    def delete_profile(self):
        sel = self._get_selected_profile_name()
        if not sel:
            messagebox.showinfo("No selection", "Select a profile to delete.")
            return
        if not messagebox.askyesno("Confirm", f"Delete profile '{sel}' and all its coordinates?"):
            return
        del self.data[sel]
        save_data(self.data, self.data_path)
        self._refresh_profile_listbox()
        # clear right side
        self.clear_profile_display()

    # ---------------- Right panel: profile details ----------------
    def _build_right_panel(self):
        top = ttk.Frame(self.right_frame)
        top.pack(fill=tk.X)

        self.profile_title_var = tk.StringVar(value="(no profile selected)")
        title_lbl = ttk.Label(top, textvariable=self.profile_title_var, font=("TkDefaultFont", 14, "bold"))
        title_lbl.pack(anchor=tk.W)

        # Seed row
        seed_frame = ttk.Frame(self.right_frame)
        seed_frame.pack(fill=tk.X, pady=(8, 6))

        seed_lbl = ttk.Label(seed_frame, text="World seed (optional):")
        seed_lbl.pack(side=tk.LEFT)

        self.seed_var = tk.StringVar()
        self.seed_entry = ttk.Entry(seed_frame, textvariable=self.seed_var)
        self.seed_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 6))

        self.save_seed_btn = ttk.Button(seed_frame, text="Save Seed", command=self.save_seed)
        self.save_seed_btn.pack(side=tk.LEFT)

        # Coordinates tree
        tree_frame = ttk.Frame(self.right_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 6))

        cols = ("name", "x", "y", "z")
        self.coords_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        self.coords_tree.heading("name", text="Name")
        self.coords_tree.heading("x", text="X")
        self.coords_tree.heading("y", text="Y")
        self.coords_tree.heading("z", text="Z")

        self.coords_tree.column("name", width=200, anchor=tk.W)
        self.coords_tree.column("x", width=100, anchor=tk.E)
        self.coords_tree.column("y", width=100, anchor=tk.E)
        self.coords_tree.column("z", width=120, anchor=tk.E)

        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.coords_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.coords_tree.xview)
        self.coords_tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        self.coords_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # Add / delete coord controls
        add_frame = ttk.Frame(self.right_frame)
        add_frame.pack(fill=tk.X)

        ttk.Label(add_frame, text="Name:").pack(side=tk.LEFT)
        self.coord_name_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.coord_name_var, width=20).pack(side=tk.LEFT, padx=(4, 8))

        ttk.Label(add_frame, text="X:").pack(side=tk.LEFT)
        self.coord_x_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.coord_x_var, width=10).pack(side=tk.LEFT, padx=(4, 8))

        ttk.Label(add_frame, text="Y:").pack(side=tk.LEFT)
        self.coord_y_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.coord_y_var, width=10).pack(side=tk.LEFT, padx=(4, 8))

        ttk.Label(add_frame, text="Z:").pack(side=tk.LEFT)
        self.coord_z_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.coord_z_var, width=12).pack(side=tk.LEFT, padx=(4, 8))

        self.add_coord_btn = ttk.Button(add_frame, text="➕ Add coordinate", command=self.add_coord)
        self.add_coord_btn.pack(side=tk.LEFT, padx=(6, 4))

        self.delete_coord_btn = ttk.Button(add_frame, text="🗑️ Delete selected", command=self.delete_selected_coord)
        self.delete_coord_btn.pack(side=tk.LEFT)

        # Bottom row: quick actions
        bottom = ttk.Frame(self.right_frame)
        bottom.pack(fill=tk.X, pady=(8, 0))

        self.copy_btn = ttk.Button(bottom, text="Copy selected coords text", command=self.copy_selected_coords_text)
        self.copy_btn.pack(side=tk.LEFT)

        self.jump_btn = ttk.Button(bottom, text="Print coord to console", command=self.print_selected_coord)
        self.jump_btn.pack(side=tk.LEFT, padx=(6, 6))

        self.clear_fields_btn = ttk.Button(bottom, text="Clear entry fields", command=self.clear_entry_fields)
        self.clear_fields_btn.pack(side=tk.RIGHT)

    def _bind_events(self):
        self.profile_listbox.bind("<<ListboxSelect>>", self.on_profile_select)
        self.coords_tree.bind("<Double-1>", lambda e: self.edit_selected_coord())
        # Key bindings
        self.bind("<Delete>", lambda e: self.delete_selected_coord())
        self.bind("<Control-s>", lambda e: save_data(self.data, self.data_path))

    # ---------------- Profile selection & display ----------------
    def _get_selected_profile_name(self):
        sel = self.profile_listbox.curselection()
        if not sel:
            return None
        return self.profile_listbox.get(sel[0])

    def on_profile_select(self, event):
        profile = self._get_selected_profile_name()
        if not profile:
            self.clear_profile_display()
            return
        self.profile_title_var.set(f"Profile: {profile}")
        seed = self.data.get(profile, {}).get("seed", "")
        self.seed_var.set(seed)
        # populate coords tree
        self._refresh_coords_tree(profile)

    def clear_profile_display(self):
        self.profile_title_var.set("(no profile selected)")
        self.seed_var.set("")
        for i in self.coords_tree.get_children():
            self.coords_tree.delete(i)

    def _refresh_coords_tree(self, profile_name):
        for i in self.coords_tree.get_children():
            self.coords_tree.delete(i)
        coords = self.data.get(profile_name, {}).get("coords", [])
        for idx, c in enumerate(coords):
            # store index as iid
            self.coords_tree.insert("", tk.END, iid=str(idx), values=(c.get("name", ""),
                                                                      c.get("x", ""),
                                                                      c.get("y", ""),
                                                                      c.get("z", "")))

    def save_seed(self):
        profile = self._get_selected_profile_name()
        if not profile:
            messagebox.showinfo("No profile", "Select or create a profile first.")
            return
        self.data[profile]["seed"] = self.seed_var.get().strip()
        save_data(self.data, self.data_path)
        messagebox.showinfo("Saved", "Seed saved.")

    # ---------------- Coordinates operations ----------------
    def add_coord(self):
        profile = self._get_selected_profile_name()
        if not profile:
            messagebox.showinfo("No profile", "Select or create a profile first.")
            return

        name = self.coord_name_var.get().strip()
        x = self.coord_x_var.get().strip()
        y = self.coord_y_var.get().strip()
        z = self.coord_z_var.get().strip()

        if not name:
            messagebox.showerror("Validation", "Give the coordinate a name.")
            return

        # Try to parse numbers (allow ints, and floats if user entered)
        try:
            x_val = int(x) if x.isdigit() or (x.startswith("-") and x[1:].isdigit()) else float(x)
            y_val = int(y) if y.isdigit() or (y.startswith("-") and y[1:].isdigit()) else float(y)
            z_val = int(z) if z.isdigit() or (z.startswith("-") and z[1:].isdigit()) else float(z)
        except Exception:
            messagebox.showerror("Validation", "X, Y and Z must be numbers.")
            return

        coord = {"name": name, "x": x_val, "y": y_val, "z": z_val}
        self.data[profile]["coords"].append(coord)
        save_data(self.data, self.data_path)
        self._refresh_coords_tree(profile)
        self.clear_entry_fields()

    def delete_selected_coord(self, *_):
        profile = self._get_selected_profile_name()
        if not profile:
            return
        sel = self.coords_tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a coordinate to delete.")
            return
        idx = int(sel[0])
        coords = self.data[profile]["coords"]
        if idx < 0 or idx >= len(coords):
            messagebox.showerror("Error", "Invalid selection index.")
            return
        if not messagebox.askyesno("Confirm", f"Delete coordinate '{coords[idx].get('name')}'?"):
            return
        coords.pop(idx)
        # Re-save and rebuild iids (we use index as iid so rebuild)
        save_data(self.data, self.data_path)
        self._refresh_coords_tree(profile)

    def edit_selected_coord(self):
        profile = self._get_selected_profile_name()
        if not profile:
            return
        sel = self.coords_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        coord = self.data[profile]["coords"][idx]
        # prefill fields
        self.coord_name_var.set(coord.get("name", ""))
        self.coord_x_var.set(str(coord.get("x", "")))
        self.coord_y_var.set(str(coord.get("y", "")))
        self.coord_z_var.set(str(coord.get("z", "")))
        # Ask whether to overwrite (simpler inline edit flow)
        if messagebox.askyesno("Edit", "Fields loaded into the entry boxes. Click 'Add coordinate' to append a new entry.\n\nTo modify existing entry, delete it first then click 'Add coordinate' after changing fields."):
            return

    def clear_entry_fields(self):
        self.coord_name_var.set("")
        self.coord_x_var.set("")
        self.coord_y_var.set("")
        self.coord_z_var.set("")

    def copy_selected_coords_text(self):
        sel = self.coords_tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a coordinate to copy.")
            return
        idx = int(sel[0])
        profile = self._get_selected_profile_name()
        coord = self.data[profile]["coords"][idx]
        text = f"{coord.get('name')}: x={coord.get('x')} y={coord.get('y')} z={coord.get('z')}"
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Coordinate text copied to clipboard.")

    def print_selected_coord(self):
        sel = self.coords_tree.selection()
        if not sel:
            messagebox.showinfo("Select", "Select a coordinate.")
            return
        idx = int(sel[0])
        profile = self._get_selected_profile_name()
        coord = self.data[profile]["coords"][idx]
        print(f"[{profile}] {coord.get('name')}: x={coord.get('x')} y={coord.get('y')} z={coord.get('z')}")
        messagebox.showinfo("Printed", "Coordinate printed to console.")

    # ---------------- Import / Export JSON ----------------
    def import_json(self):
        path = filedialog.askopenfilename(title="Import JSON file", filetypes=[("JSON files","*.json"),("All files","*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                newdata = json.load(f)
            if not isinstance(newdata, dict):
                messagebox.showerror("Import error", "Imported JSON must be an object mapping profile names to profile data.")
                return
            # prompt whether to merge or replace
            if self.data and messagebox.askyesno("Merge or replace?", "Merge imported profiles into existing data? (No -> replace all data)"):
                # merge: imported profiles overwrite existing profiles of same name
                self.data.update(newdata)
            else:
                self.data = newdata
            save_data(self.data, self.data_path)
            self._refresh_profile_listbox()
            messagebox.showinfo("Imported", "Import finished.")
        except Exception as e:
            messagebox.showerror("Import error", f"Failed to import:\n{e}")

    def export_json(self):
        path = filedialog.asksaveasfilename(title="Export JSON file", defaultextension=".json", filetypes=[("JSON files","*.json")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Exported", f"Exported to {path}")
        except Exception as e:
            messagebox.showerror("Export error", f"Failed to export:\n{e}")


def main():
    app = CoordManagerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
