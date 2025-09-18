import tkinter as tk
from tkinter import ttk, messagebox
from rbc_model import RBCModel

class RBC_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema RBC - Avaliação de Preço de Carros")
        self.root.minsize(800, 600)

        try:
            self.model = RBCModel()
        except SystemExit:
            messagebox.showerror("Erro Crítico", "Não foi possível carregar o modelo. Verifique o console.")
            root.destroy()
            return

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Centralização Horizontal
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        
        # --- ALTERAÇÃO 1: Centralização Vertical ---
        # Adicionamos uma linha vazia no topo (0) e no fundo (5)
        # para empurrar o conteúdo para o centro vertical.
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(5, weight=1)

        # O conteúdo agora começa na linha 1
        input_frame = ttk.LabelFrame(main_frame, text="Inserir Dados do Carro", padding=10, labelanchor="n")
        input_frame.grid(row=1, column=1, sticky=(tk.W, tk.E))
        
        inner_input_frame = ttk.Frame(input_frame)
        inner_input_frame.pack(pady=10, padx=10)
        
        self.entries = {}
        self.feature_columns_pt = self.model.categorical_features_pt + self.model.numerical_features_pt
        combobox_fields = ['Fabricante', 'Modelo', 'Combustível', 'Motor']

        for i, feature_pt in enumerate(self.feature_columns_pt):
            ttk.Label(inner_input_frame, text=f"{feature_pt}:").grid(row=i, column=0, sticky=tk.W, pady=5, padx=5)
            feature_en = self.model.inv_translation_map[feature_pt]
            
            if feature_pt in combobox_fields:
                # O dropdown de Fabricante será populado, mas os outros começarão vazios
                values_for_display = []
                if feature_pt == 'Fabricante':
                    values_for_display = sorted(self.model.case_base_original[feature_en].unique().tolist())

                combobox = ttk.Combobox(inner_input_frame, values=values_for_display, width=23, state='readonly')
                combobox.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
                self.entries[feature_pt] = combobox
            else:
                entry = ttk.Entry(inner_input_frame, width=25)
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
                self.entries[feature_pt] = entry
        
        self.entries['Fabricante'].bind('<<ComboboxSelected>>', self.update_models)
        self.entries['Modelo'].bind('<<ComboboxSelected>>', self.update_options_for_model)
        
        # --- ALTERAÇÃO 2: Iniciar com campos em branco ---
        # A linha abaixo foi comentada para que o programa não preencha os dados iniciais.
        # self.fill_example_data()

        button_frame = ttk.Frame(main_frame)
        # O botão agora fica na linha 2
        button_frame.grid(row=2, column=1, pady=10, sticky='ew')
        find_button = ttk.Button(button_frame, text="Encontrar Carros Similares e Sugerir Preço", command=self.find_similar_cases)
        find_button.pack()

        result_frame = ttk.LabelFrame(main_frame, text="Resultados (Carros Mais Similares)", padding=10, labelanchor="n")
        # O frame de resultados agora fica na linha 3
        result_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=10)
        
        columns_to_show = self.feature_columns_pt + [self.model.solution_feature_pt]
        self.tree = ttk.Treeview(result_frame, columns=columns_to_show, show='headings', height=6)
        for col in columns_to_show:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor='center')
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

        solution_frame = ttk.Frame(main_frame, padding="10")
        # O frame de solução agora fica na linha 4
        solution_frame.grid(row=4, column=1, sticky='ew')
        self.solution_label = ttk.Label(solution_frame, text="Preço Sugerido:", font=("Helvetica", 12, "bold"))
        self.solution_label.pack()

    # A função fill_example_data ainda existe, mas não é mais chamada no início.
    def fill_example_data(self):
        example_case = self.model.case_base_original.iloc[0]
        self.entries['Fabricante'].set(example_case['Manufacturer'])
        self.update_models(None)
        self.entries['Modelo'].set(example_case['Model'])
        self.update_options_for_model(None)
        fuel_en = example_case['Fuel type']
        fuel_pt = self.model.fuel_translation.get(fuel_en, fuel_en)
        self.entries['Combustível'].set(fuel_pt)
        self.entries['Motor'].set(example_case['Engine size'])
        self.entries['Ano'].insert(0, example_case['Year of manufacture'])
        self.entries['Quilometragem'].insert(0, example_case['Mileage'])

    # Nenhuma outra alteração é necessária nas funções restantes
    def update_models(self, event):
        manufacturer_en = self.entries['Fabricante'].get()
        models = sorted(self.model.case_base_original[self.model.case_base_original['Manufacturer'] == manufacturer_en]['Model'].unique().tolist())
        self.entries['Modelo']['values'] = models
        self.entries['Modelo'].set('')
        self.entries['Combustível']['values'] = []
        self.entries['Combustível'].set('')
        self.entries['Motor']['values'] = []
        self.entries['Motor'].set('')
    def update_options_for_model(self, event):
        manufacturer_en = self.entries['Fabricante'].get()
        model_en = self.entries['Modelo'].get()
        if not model_en: return
        filtered_df = self.model.case_base_original[(self.model.case_base_original['Manufacturer'] == manufacturer_en) & (self.model.case_base_original['Model'] == model_en)]
        fuels_en = filtered_df['Fuel type'].unique().tolist()
        fuels_pt = sorted([self.model.fuel_translation.get(val, val) for val in fuels_en])
        self.entries['Combustível']['values'] = fuels_pt
        self.entries['Combustível'].set('')
        engines = sorted(filtered_df['Engine size'].unique().tolist())
        self.entries['Motor']['values'] = engines
        self.entries['Motor'].set('')
    def find_similar_cases(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        self.solution_label.config(text="Preço Sugerido:")
        new_case_pt = {}
        try:
            for feature_pt, widget in self.entries.items():
                value = widget.get()
                if not value:
                    messagebox.showerror("Erro de Entrada", f"O campo '{feature_pt}' não pode estar vazio.")
                    return
                if feature_pt in self.model.numerical_features_pt:
                    new_case_pt[feature_pt] = float(value)
                else:
                    new_case_pt[feature_pt] = value
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Por favor, insira valores numéricos válidos nos campos de Ano e Quilometragem.")
            return
        new_case_en = {}
        for feature_pt, value_pt in new_case_pt.items():
            feature_en = self.model.inv_translation_map[feature_pt]
            if feature_pt == 'Combustível':
                value_en = self.model.inv_fuel_translation.get(str(value_pt), str(value_pt))
            else:
                value_en = value_pt
            new_case_en[feature_en] = value_en
        similar_cases_pt = self.model.retrieve(new_case_en, k=5)
        if not similar_cases_pt.empty:
            suggested_price = similar_cases_pt[self.model.solution_feature_pt].mean()
            self.solution_label.config(text=f"Preço Sugerido: R$ {suggested_price:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            for index, row in similar_cases_pt.iterrows():
                row['Combustível'] = self.model.fuel_translation.get(row['Combustível'], row['Combustível'])
                self.tree.insert("", "end", values=list(row))
        else:
            self.solution_label.config(text="Preço Sugerido: N/A (nenhum carro encontrado)")