import re
import json
import logging
import traceback

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox
from tkinter import ttk as native_ttk
from tkinter.scrolledtext import ScrolledText

# --- Logging setup ---
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("markdown_json_editor.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)


class CollapsibleSection(ttk.Frame):
    def __init__(self, parent, title="", anchor_tag=None, on_select=None):
        super().__init__(parent)
        self.title = title
        self.anchor_tag = anchor_tag
        self.on_select = on_select
        self._is_collapsed = False

        header = ttk.Frame(self)
        header.pack(fill="x")
        self.toggle_btn = ttk.Button(header, text="▾ " + self.title,
                                     bootstyle=(INFO, "outline"))
        self.toggle_btn.pack(side="left", pady=2, padx=2, fill="x", expand=True)

        self.toggle_btn.bind("<Double-Button-1>", lambda e: self.toggle())
        self.toggle_btn.bind("<Button-1>", self._on_single_click)

        self.content = ttk.Frame(self)
        self.content.pack(fill="both", expand=True)

    def _on_single_click(self, event):
        if self.on_select:
            self.on_select(self)

    def toggle(self):
        if self._is_collapsed:
            self.content.pack(fill="both", expand=True)
            self.toggle_btn.config(text="▾ " + self.title)
            self._is_collapsed = False
        else:
            self.content.forget()
            self.toggle_btn.config(text="▸ " + self.title)
            self._is_collapsed = True

    def expand(self):
        if self._is_collapsed:
            self.toggle()

    def collapse(self):
        if not self._is_collapsed:
            self.toggle()


class MarkdownJSONEditor(ttk.Window):
    def __init__(self, themename="darkly"):
        super().__init__(themename=themename)
        self.title("Markdown ⇄ JSON Editor")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self.sections = []
        self.json_data = []
        self.current_json_index = 0
        self.markdown_lines = []
        self.anchor_to_section_widget = {}
        self.selected_section_widget = None

        self._build_ui()
        self._load_files()

    def _build_ui(self):
        self.main_pane = ttk.PanedWindow(self, orient="horizontal")
        self.main_pane.pack(fill="both", expand=True, padx=10, pady=10)

        # LEFT side: markdown view
        self.left_frame = ttk.Frame(self.main_pane)
        self.main_pane.add(self.left_frame, weight=3)

        self.sec_canvas = ttk.Canvas(self.left_frame)
        self.sec_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.sec_scrollbar = ttk.Scrollbar(self.left_frame, orient="vertical", command=self.sec_canvas.yview)
        self.sec_scrollbar.pack(side="left", fill="y")

        self.sec_canvas.configure(yscrollcommand=self.sec_scrollbar.set)
        self.sec_canvas.bind('<Configure>', lambda e: self.sec_canvas.configure(
            scrollregion=self.sec_canvas.bbox("all")))

        self.sections_container = ttk.Frame(self.sec_canvas)
        self.sec_canvas.create_window((0, 0), window=self.sections_container, anchor="nw")

        # RIGHT side: JSON view + Treeview + Buttons in vertical PanedWindow
        self.right_frame = ttk.Frame(self.main_pane)
        self.main_pane.add(self.right_frame, weight=2)

        ttk.Label(self.right_frame, text="JSON Data", font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 5), padx=5)

        # 🔥 NEW vertical panedwindow inside right_frame
        self.right_pane = ttk.PanedWindow(self.right_frame, orient="vertical")
        self.right_pane.pack(fill="both", expand=True, padx=5, pady=5)

        # Pane 1: JSON display
        self.json_display_frame = ttk.Frame(self.right_pane)
        self.json_display = ScrolledText(self.json_display_frame, wrap="word", height=15,
                                        state="disabled", font=("Consolas", 11))
        self.json_display.pack(fill="both", expand=True)
        self.right_pane.add(self.json_display_frame, weight=2)

        # Pane 2: Treeview
        self.tree_frame = ttk.Frame(self.right_pane)
        ttk.Label(self.tree_frame, text="Contents", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=5, pady=(10, 5))
        self.tree = native_ttk.Treeview(self.tree_frame, show="tree", height=10)
        self.tree.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.right_pane.add(self.tree_frame, weight=1)

        # Pane 3: Buttons
        self.button_frame = ttk.Frame(self.right_pane)
        ttk.Button(self.button_frame, text="Insert into Selected Section", bootstyle=(INFO),
                command=self._insert_json).pack(pady=(10, 5), fill="x", padx=5)
        ttk.Button(self.button_frame, text="Save Markdown", bootstyle=(SUCCESS, "outline"),
                command=self._save_markdown).pack(pady=5, fill="x", padx=5)
        self.right_pane.add(self.button_frame, weight=0)


    def _load_files(self):
        try:
            md_path = filedialog.askopenfilename(title="Select Markdown File", filetypes=[("Markdown files","*.md")])
            if not md_path:
                raise FileNotFoundError("No markdown file selected.")
            json_path = filedialog.askopenfilename(title="Select JSON File", filetypes=[("JSON files","*.json")])
            if not json_path:
                raise FileNotFoundError("No JSON file selected.")

            with open(md_path, "r", encoding="utf-8") as f:
                md_text = f.read()
            with open(json_path, "r", encoding="utf-8") as f:
                jd = json.load(f)

            if not isinstance(jd, list):
                raise ValueError("JSON must be a list.")

            self.json_data = jd
            self.markdown_lines = md_text.splitlines()

            logger.debug(f"Loaded markdown ({len(self.markdown_lines)} lines) and JSON ({len(self.json_data)} items)")

            self._parse_contents_and_sections()
            self._populate_tree()
            self._build_sections_ui()
            self._display_current_json()

        except Exception as e:
            logger.error(f"Error loading files: {e}\n{traceback.format_exc()}")
            messagebox.showerror("Load Error", f"Error loading files:\n{e}")
            self.destroy()

    def _parse_contents_and_sections(self):
        lines = self.markdown_lines
        idx = 0
        in_code = False

        # 1. Locate "# contents" heading outside codeblocks
        while idx < len(lines):
            ln = lines[idx]
            stripped = ln.strip()
            if stripped.startswith("```"):
                in_code = not in_code
            if not in_code and stripped.lower() == "# contents":
                idx += 1
                break
            idx += 1
        else:
            raise ValueError("Could not find '# contents' heading (outside code block)")

        # 2. Parse subsequent bullet list lines for contents
        contents_map = []
        while idx < len(lines):
            ln = lines[idx]
            stripped = ln.strip()
            if stripped.startswith("```"):
                in_code = not in_code
            if not in_code and stripped.startswith("- [") and "](" in stripped:
                try:
                    part = stripped[2:].strip()
                    lb, rest = part.split("](", 1)
                    label = lb.strip("[")
                    anchor = rest.strip(")").lstrip("#")
                    contents_map.append((label, anchor))
                except Exception as e:
                    logger.warning(f"Contents parse failure at line {idx}: {stripped} — {e}")
                idx += 1
                continue
            break  # stop on first non-list (outside code)
        logger.debug(f"Contents map: {contents_map}")

        # 3. Parse the rest into sections, ignoring headings inside code
        self.sections = []
        in_code = False
        current = None

        for li in range(idx, len(lines)):
            ln = lines[li]
            stripped = ln.strip()
            if stripped.startswith("```"):
                in_code = not in_code
                if current:
                    current["content"] += ln + "\n"
                continue

            if not in_code and stripped.startswith("#"):
                # New heading outside code
                count_hash = len(ln) - len(ln.lstrip("#"))
                heading = ln.lstrip("#").strip()
                anchor = None
                for (lbl, anc) in contents_map:
                    if lbl.lower() == heading.lower() or anc.lower() == heading.lower():
                        anchor = anc
                        break
                if current:
                    self.sections.append(current)
                current = {
                    "heading": heading,
                    "level": count_hash,
                    "content": ln + "\n",
                    "anchor_tag": anchor
                }
            else:
                if current:
                    current["content"] += ln + "\n"

        if current:
            self.sections.append(current)

        self.anchor_to_section_widget.clear()
        for sec in self.sections:
            if sec["anchor_tag"] is not None:
                self.anchor_to_section_widget[sec["anchor_tag"]] = None

    def _populate_tree(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        # logger.debug("sections", [s["anchor_tag"] for s in self.sections])
        # self.sections = sorted(self.sections, key=lambda x: x["anchor_tag"] or "")
        for sec in self.sections:
            if sec["anchor_tag"] is not None:
                self.tree.insert("", "end", iid=sec["anchor_tag"], text=sec["heading"])

    def _build_sections_ui(self):
        for child in self.sections_container.winfo_children():
            child.destroy()
        self.anchor_to_section_widget.clear()

        for sec in self.sections:
            widget = CollapsibleSection(self.sections_container,
                                        title=sec["heading"],
                                        anchor_tag=sec["anchor_tag"],
                                        on_select=self._on_section_select)
            widget.pack(fill="x", pady=5, padx=5)
            ttk.Label(widget.content, text=sec["content"].strip(), justify="left", wraplength=600).pack(anchor="w")
            if sec["anchor_tag"]:
                self.anchor_to_section_widget[sec["anchor_tag"]] = widget

    def _on_section_select(self, widget):
        self.selected_section_widget = widget

    def _on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        anchor = selected[0]
        widget = self.anchor_to_section_widget.get(anchor)
        if widget:
            widget.expand()
            self.sec_canvas.yview_moveto(widget.winfo_y() / max(1, self.sections_container.winfo_height()))
            self.selected_section_widget = widget

    def _display_current_json(self):
        self.json_display.configure(state="normal")
        self.json_display.delete("1.0", "end")

        if self.current_json_index < len(self.json_data):
            item = self.json_data[self.current_json_index]
            if isinstance(item, list) and all(isinstance(s, str) for s in item):
                text = "\n".join(item)

                # 🚀 Try to extract a heading from the first line
                first_line = item[0].strip()
                # Remove leading markdown symbols and trailing punctuation
                cleaned = re.sub(r"^[^a-zA-Z0-9]*", "", first_line)
                cleaned = re.sub(r"[^a-zA-Z0-9\s\-]+$", "", cleaned)
                candidate = cleaned.lower().strip()

                logger.debug(f"Trying to auto-match heading from line: '{first_line}' → '{candidate}'")

                for sec in self.sections:
                    heading = sec["heading"].lower().strip()
                    if candidate == heading:
                        widget = self.anchor_to_section_widget.get(sec["anchor_tag"])
                        if widget:
                            logger.info(f"Auto-selected heading: {heading}")
                            widget.expand()
                            self.sec_canvas.yview_moveto(widget.winfo_y() / max(1, self.sections_container.winfo_height()))
                            self.selected_section_widget = widget

                            # ✅ Highlight the Treeview item
                            if sec["anchor_tag"] in self.tree.get_children():
                                self.tree.selection_set(sec["anchor_tag"])
                                self.tree.see(sec["anchor_tag"])

                        break

            else:
                try:
                    text = json.dumps(item, indent=4, ensure_ascii=False)
                except Exception:
                    text = str(item)

            self.json_display.insert("1.0", text)
        else:
            self.json_display.insert("1.0", "✅ All JSON items inserted.")

        self.json_display.configure(state="disabled")



    def _insert_json(self):
        if self.selected_section_widget is None:
            messagebox.showwarning("Select Section", "Please select a section to insert into.")
            return
        if self.current_json_index >= len(self.json_data):
            messagebox.showinfo("Done", "All JSON items have been inserted.")
            return

        anchor = self.selected_section_widget.anchor_tag
        sec_idx = next((i for i, s in enumerate(self.sections) if s["anchor_tag"] == anchor), None)
        if sec_idx is None:
            messagebox.showerror("Error", "Selected section not found.")
            return

        item = self.json_data[self.current_json_index]
        if not (isinstance(item, list) and all(isinstance(s, str) for s in item)):
            messagebox.showerror("Format Error", "Expected JSON item to be a list of markdown strings.")
            return

        section = self.sections[sec_idx]
        # Preserve existing content (after heading) and append new markdown lines
        lines = section["content"].splitlines()
        heading_line = lines[0]
        existing_body = "\n".join(lines[1:]).strip()
        new_body = "\n".join(item).strip()

        if existing_body:
            combined = existing_body + "\n\n" + new_body
        else:
            combined = new_body

        section["content"] = heading_line + "\n\n" + combined + "\n"

        # Update preview label in the UI
        widget = self.anchor_to_section_widget.get(anchor)
        if widget:
            children = widget.content.winfo_children()
            if children:
                lbl = children[0]
                lbl.config(text=section["content"])

        self.current_json_index += 1
        self._display_current_json()

    def _save_markdown(self):
        try:
            contents_lines = ["# contents"]
            for sec in self.sections:
                if sec["anchor_tag"] is not None:
                    contents_lines.append(f"- [{sec['heading']}](#{sec['anchor_tag']})")
            contents_lines.append("")

            section_lines = []
            for sec in self.sections:
                sec_lines = sec["content"].rstrip("\n").splitlines()
                section_lines.extend(sec_lines)
                section_lines.append("")

            full_text = "\n".join(contents_lines + section_lines)
            save_path = filedialog.asksaveasfilename(title="Save Markdown", defaultextension=".md",
                                                     filetypes=[("Markdown files","*.md")])
            if save_path:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(full_text)
                messagebox.showinfo("Saved", f"Markdown saved to:\n{save_path}")
        except Exception as e:
            logger.error(f"Save error: {e}\n{traceback.format_exc()}")
            messagebox.showerror("Save Error", f"Error saving markdown:\n{e}")


if __name__ == "__main__":
    try:
        app = MarkdownJSONEditor(themename="darkly")
        app.mainloop()
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}\n{traceback.format_exc()}")
        messagebox.showerror("Fatal Error", f"An unexpected error occurred:\n{e}")
