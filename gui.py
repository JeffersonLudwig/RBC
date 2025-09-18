import tkinter as tk
from tkinter import ttk, messagebox
from rbc_model import RBCModel

class RBC_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema RBC - Avaliação de Preço de Carros")

        try:
            self.model = RBCModel()
        except SystemExit:
            messagebox.showerror("Erro Crítico", "Não foi possível carregar o modelo. Verifique o console.")
            root.destroy()
            return

        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        input_frame = ttk.LabelFrame(main_frame, text="Inserir Dados do Carro", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.entries = {}
        self.feature_columns_pt = self.model.categorical_features_pt + self.model.numerical_features_pt
        
        combobox_fields = ['Fabricante', 'Modelo', 'Combustível', 'Motor']

        for i, feature_pt in enumerate(self.feature_columns_pt):
            ttk.Label(input_frame, text=f"{feature_pt}:").grid(row=i, column=0, sticky=tk.W, pady=5, padx=5)
            
            feature_en = self.model.inv_translation_map[feature_pt]
            
            if feature_pt in combobox_fields:
                unique_values = sorted(self.model.case_base_original[feature_en].unique().tolist())
                combobox = ttk.Combobox(input_frame, values=unique_values, width=23, state='readonly')
                combobox.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
                self.entries[feature_pt] = combobox
            else:
                entry = ttk.Entry(input_frame, width=25)
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
                self.entries[feature_pt] = entry
        
        # --- LÓGICA DOS DROPDOWNS EM CASCATA ---
        # Evento para quando o Fabricante é alterado
        self.entries['Fabricante'].bind('<<ComboboxSelected>>', self.update_models)
        # Evento para quando o Modelo é alterado
        self.entries['Modelo'].bind('<<ComboboxSelected>>', self.update_options_for_model)

        self.fill_example_data()

        find_button = ttk.Button(main_frame, text="Encontrar Carros Similares e Sugerir Preço", command=self.find_similar_cases)
        find_button.grid(row=1, column=0, columnspan=2, pady=10)

        # ... (O resto do código da interface para resultados e solução é o mesmo) ...
        result_frame = ttk.LabelFrame(main_frame, text="Resultados (Carros Mais Similares)", padding="10")
        result_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
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
        solution_frame.grid(row=3, column=0, columnspan=2, sticky="ew")
        self.solution_label = ttk.Label(solution_frame, text="Preço Sugerido:", font=("Helvetica", 12, "bold"))
        self.solution_label.pack()

    def update_models(self, event):
        """Atualiza a lista de MODELOS baseado no Fabricante."""
        manufacturer_en = self.entries['Fabricante'].get()
        models = sorted(self.model.case_base_original[
            self.model.case_base_original['Manufacturer'] == manufacturer_en
        ]['Model'].unique().tolist())
        
        # Atualiza a lista de modelos
        self.entries['Modelo']['values'] = models
        # Limpa as seleções seguintes, pois elas agora são inválidas
        self.entries['Modelo'].set('')
        self.entries['Combustível']['values'] = []
        self.entries['Combustível'].set('')
        self.entries['Motor']['values'] = []
        self.entries['Motor'].set('')

    def update_options_for_model(self, event):
        """Atualiza COMBUSTÍVEL e MOTOR baseado no Modelo."""
        manufacturer_en = self.entries['Fabricante'].get()
        model_en = self.entries['Modelo'].get()

        # Se o modelo estiver vazio, não faz nada
        if not model_en:
            return

        # Filtra a base de dados pelo fabricante E pelo modelo
        filtered_df = self.model.case_base_original[
            (self.model.case_base_original['Manufacturer'] == manufacturer_en) &
            (self.model.case_base_original['Model'] == model_en)
        ]

        # Atualiza a lista de combustíveis disponíveis
        fuels = sorted(filtered_df['Fuel type'].unique().tolist())
        self.entries['Combustível']['values'] = fuels
        self.entries['Combustível'].set('')

        # Atualiza a lista de motores disponíveis
        engines = sorted(filtered_df['Engine size'].unique().tolist())
        self.entries['Motor']['values'] = engines
        self.entries['Motor'].set('')

    def fill_example_data(self):
        """Preenche os campos com o primeiro caso da base e atualiza os dropdowns."""
        example_case = self.model.case_base_original.iloc[0]
        
        # Define o fabricante inicial
        self.entries['Fabricante'].set(example_case['Manufacturer'])
        # Atualiza a lista de modelos
        self.update_models(None)
        
        # Define o modelo inicial
        self.entries['Modelo'].set(example_case['Model'])
        # Atualiza as opções de combustível e motor
        self.update_options_for_model(None)

        # Define as outras opções
        self.entries['Combustível'].set(example_case['Fuel type'])
        self.entries['Motor'].set(example_case['Engine size'])
        self.entries['Ano'].insert(0, example_case['Year of manufacture'])
        self.entries['Quilometragem'].insert(0, example_case['Mileage'])


    def find_similar_cases(self):
        # ... (Esta função continua exatamente a mesma da versão anterior) ...
        for i in self.tree.get_children():
            self.tree.delete(i)
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
        new_case_en = {self.model.inv_translation_map[k]: v for k, v in new_case_pt.items()}
        similar_cases_pt = self.model.retrieve(new_case_en, k=5)
        if not similar_cases_pt.empty:
            suggested_price = similar_cases_pt[self.model.solution_feature_pt].mean()
            self.solution_label.config(text=f"Preço Sugerido: R$ {suggested_price:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            for index, row in similar_cases_pt.iterrows():
                self.tree.insert("", "end", values=list(row))
        else:
            self.solution_label.config(text="Preço Sugerido: N/A (nenhum carro encontrado)")