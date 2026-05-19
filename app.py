"""
Programa de Formulación de Recetas Médicas
Genera PDFs con el diseño de mateouribe
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import sys
from datetime import datetime
from pdf_generator import generate_prescription_pdf


class MedicationFrame(tk.Frame):
    """Frame para un medicamento individual."""

    def __init__(self, parent, index, on_remove):
        super().__init__(parent, bg="#F8F9FA", bd=1, relief="solid")
        self.index = index
        self.on_remove = on_remove
        self._build()

    def _build(self):
        header = tk.Frame(self, bg="#EEF0FF")
        header.pack(fill="x", padx=1, pady=(1, 0))

        tk.Label(
            header, text=f"  Medicamento {self.index + 1}",
            bg="#EEF0FF", fg="#3D2FB5", font=("Helvetica", 10, "bold")
        ).pack(side="left", pady=6)

        tk.Button(
            header, text="✕ Eliminar", command=self.on_remove,
            bg="#EEF0FF", fg="#888", relief="flat", cursor="hand2",
            font=("Helvetica", 9)
        ).pack(side="right", padx=8)

        body = tk.Frame(self, bg="#F8F9FA")
        body.pack(fill="x", padx=12, pady=8)

        fields = [
            ("Nombre genérico*", "generic_var", True),
            ("Nombre comercial", "brand_var", False),
            ("Presentación", "form_var", False),
            ("Instrucciones*", "instructions_var", True),
        ]

        for label_text, attr, required in fields:
            row = tk.Frame(body, bg="#F8F9FA")
            row.pack(fill="x", pady=3)

            lbl = tk.Label(
                row, text=label_text, width=18, anchor="w",
                bg="#F8F9FA", fg="#555", font=("Helvetica", 10)
            )
            lbl.pack(side="left")

            var = tk.StringVar()
            setattr(self, attr, var)

            entry = ttk.Entry(row, textvariable=var, font=("Helvetica", 10))
            entry.pack(side="left", fill="x", expand=True)

    def get_data(self):
        return {
            "generic": self.generic_var.get().strip(),
            "brand": self.brand_var.get().strip(),
            "form": self.form_var.get().strip(),
            "instructions": self.instructions_var.get().strip(),
        }

    def validate(self):
        d = self.get_data()
        if not d["generic"]:
            return False, f"Medicamento {self.index + 1}: el nombre genérico es obligatorio."
        if not d["instructions"]:
            return False, f"Medicamento {self.index + 1}: las instrucciones son obligatorias."
        return True, ""


class PrescriptionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Formulación de Recetas — mateouribe")
        self.geometry("680x780")
        self.resizable(True, True)
        self.configure(bg="#FFFFFF")
        self.medication_frames = []
        self._build_ui()
        self._add_medication()

    # ── Layout ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_patient_section()
        self._build_medications_section()
        self._build_actions()

    def _build_header(self):
        header = tk.Frame(self, bg="#2B1FA8", height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="mateouribe", bg="#2B1FA8", fg="white",
            font=("Helvetica", 20, "bold")
        ).pack(side="left", padx=20, pady=12)

        tk.Label(
            header, text="Formulación de Recetas", bg="#2B1FA8", fg="#AABFFF",
            font=("Helvetica", 11)
        ).pack(side="left", padx=4, pady=12)

    def _build_patient_section(self):
        frame = tk.LabelFrame(
            self, text="  Datos del paciente (opcional)  ",
            bg="#FFFFFF", fg="#2B1FA8", font=("Helvetica", 10, "bold"),
            bd=1, relief="groove"
        )
        frame.pack(fill="x", padx=20, pady=(16, 8))

        row1 = tk.Frame(frame, bg="#FFFFFF")
        row1.pack(fill="x", padx=12, pady=(8, 4))

        tk.Label(row1, text="Paciente:", width=12, anchor="w",
                 bg="#FFFFFF", fg="#555", font=("Helvetica", 10)).pack(side="left")
        self.patient_var = tk.StringVar()
        ttk.Entry(row1, textvariable=self.patient_var,
                  font=("Helvetica", 10)).pack(side="left", fill="x", expand=True)

        row2 = tk.Frame(frame, bg="#FFFFFF")
        row2.pack(fill="x", padx=12, pady=(4, 8))

        tk.Label(row2, text="Fecha:", width=12, anchor="w",
                 bg="#FFFFFF", fg="#555", font=("Helvetica", 10)).pack(side="left")
        self.date_var = tk.StringVar(value=datetime.today().strftime("%d/%m/%Y"))
        ttk.Entry(row2, textvariable=self.date_var,
                  font=("Helvetica", 10), width=16).pack(side="left")

        tk.Label(row2, text="  Diagnóstico:", anchor="w",
                 bg="#FFFFFF", fg="#555", font=("Helvetica", 10)).pack(side="left")
        self.diagnosis_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.diagnosis_var,
                  font=("Helvetica", 10)).pack(side="left", fill="x", expand=True)

    def _build_medications_section(self):
        outer = tk.Frame(self, bg="#FFFFFF")
        outer.pack(fill="both", expand=True, padx=20, pady=4)

        toolbar = tk.Frame(outer, bg="#FFFFFF")
        toolbar.pack(fill="x")

        tk.Label(
            toolbar, text="Medicamentos", bg="#FFFFFF", fg="#2B1FA8",
            font=("Helvetica", 11, "bold")
        ).pack(side="left")

        tk.Button(
            toolbar, text="+ Agregar medicamento",
            command=self._add_medication,
            bg="#2B1FA8", fg="white", relief="flat", cursor="hand2",
            font=("Helvetica", 9, "bold"), padx=10, pady=4
        ).pack(side="right")

        # Scrollable container
        canvas_frame = tk.Frame(outer, bg="#FFFFFF")
        canvas_frame.pack(fill="both", expand=True, pady=6)

        self.canvas = tk.Canvas(canvas_frame, bg="#FFFFFF", highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical",
                                  command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg="#FFFFFF")

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>",
                             lambda e: self.canvas.yview_scroll(-1 * (e.delta // 120), "units"))

    def _build_actions(self):
        bar = tk.Frame(self, bg="#F0F0F0", height=56)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        tk.Button(
            bar, text="Generar PDF",
            command=self._generate,
            bg="#2B1FA8", fg="white", relief="flat", cursor="hand2",
            font=("Helvetica", 11, "bold"), padx=24, pady=8
        ).pack(side="right", padx=20, pady=10)

        tk.Button(
            bar, text="Limpiar todo",
            command=self._clear_all,
            bg="#E0E0E0", fg="#444", relief="flat", cursor="hand2",
            font=("Helvetica", 10), padx=16, pady=8
        ).pack(side="right", padx=4, pady=10)

    # ── Medication management ────────────────────────────────────────────────

    def _add_medication(self):
        idx = len(self.medication_frames)
        frame = MedicationFrame(
            self.scroll_frame, idx,
            on_remove=lambda f=None, i=idx: self._remove_medication(i)
        )
        frame.pack(fill="x", pady=4, padx=2)
        self.medication_frames.append(frame)
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def _remove_medication(self, index):
        if len(self.medication_frames) <= 1:
            messagebox.showwarning("Aviso", "Debe haber al menos un medicamento.")
            return
        frame = self.medication_frames.pop(index)
        frame.destroy()
        # Re-index remaining frames
        for i, f in enumerate(self.medication_frames):
            f.index = i
            for child in f.winfo_children():
                if isinstance(child, tk.Frame):
                    for lbl in child.winfo_children():
                        if isinstance(lbl, tk.Label) and "Medicamento" in str(lbl.cget("text")):
                            lbl.config(text=f"  Medicamento {i + 1}")
                            break

    def _clear_all(self):
        if messagebox.askyesno("Limpiar", "¿Limpiar todos los campos?"):
            for f in self.medication_frames:
                f.destroy()
            self.medication_frames.clear()
            self.patient_var.set("")
            self.date_var.set(datetime.today().strftime("%d/%m/%Y"))
            self.diagnosis_var.set("")
            self._add_medication()

    # ── PDF generation ───────────────────────────────────────────────────────

    def _generate(self):
        # Validate
        medications = []
        for frame in self.medication_frames:
            ok, msg = frame.validate()
            if not ok:
                messagebox.showerror("Validación", msg)
                return
            medications.append(frame.get_data())

        if not medications:
            messagebox.showwarning("Aviso", "Agregue al menos un medicamento.")
            return

        # Ask where to save
        MESES = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",
                 7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
        now = datetime.now()
        nombre = data["patient"].replace(" ", "") if data["patient"] else "Paciente"
        fecha = f"{now.day:02d}{MESES[now.month]}{now.year}_{now.strftime('%H%M')}"
        default_name = f"receta_{nombre}_{fecha}.pdf"
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=default_name,
            title="Guardar receta como..."
        )
        if not path:
            return

        data = {
            "patient": self.patient_var.get().strip(),
            "date": self.date_var.get().strip(),
            "diagnosis": self.diagnosis_var.get().strip(),
            "medications": medications,
        }

        try:
            generate_prescription_pdf(path, data)
            if messagebox.askyesno("Éxito", f"PDF generado.\n\n¿Abrir ahora?\n{path}"):
                self._open_file(path)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF:\n{e}")

    @staticmethod
    def _open_file(path):
        if sys.platform == "darwin":
            subprocess.call(["open", path])
        elif sys.platform.startswith("win"):
            os.startfile(path)
        else:
            subprocess.call(["xdg-open", path])


if __name__ == "__main__":
    app = PrescriptionApp()
    app.mainloop()
