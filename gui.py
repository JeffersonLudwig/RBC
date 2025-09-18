import tkinter as tk
from tkinter import ttk, messagebox
from rbc_model import RBCModel
import pandas as pd

class RBC_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema RBC - Avaliação de Preço de Carros")

        # Carrega o modelo RBC
        try:
            self.model = RBCModel()
        except SystemExit as e:
            messagebox.showerror("Erro Crítico", "Não foi possível carregar o modelo. Verifique o console.")
            root.destroy()
            return

        # Frame principal
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # --- Seção de Entrada do Novo Caso ---
        input_frame = ttk.LabelFrame(main_frame, text="Inserir Dados do Carro", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        self.entries = {}
        # Combina todas as features para criar os campos na GUI
        self.feature_columns = self.model.categorical_features + self.model.numerical_features
        
        for i, feature in enumerate(self.feature_columns):
            ttk.Label(input_frame, text=f"{feature}:").grid(row=i, column=0, sticky=tk.W, pady=5, padx=5)
            entry = ttk.Entry(input_frame, width=25)
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
            self.entries[feature] = entry

        # Preencher com valores de exemplo do primeiro caso da base
        self.fill_example_data()

        # Botão para iniciar a busca
        find_button = ttk.Button(main_frame, text="Encontrar Carros Similares e Sugerir Preço", command=self.find_similar_cases)
        find_button.grid(row=1, column=0, columnspan=2, pady=10)

        # --- Seção de Resultados ---
        result_frame = ttk.LabelFrame(main_frame, text="Resultados (Carros Mais Similares)", padding="10")
        result_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Tabela (TreeView) para mostrar os resultados
        columns_to_show = self.feature_columns + [self.model.solution_feature]
        self.tree = ttk.Treeview(result_frame, columns=columns_to_show, show='headings', height=6)
        
        for col in columns_to_show:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110, anchor='center')
        
        # Scrollbar para a tabela
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar.grid(row=0, column=1, sticky='ns')
        result_frame.grid_rowconfigure(0, weight=1)
        result_frame.grid_columnconfigure(0, weight=1)

        # --- Seção de Solução Sugerida ---
        solution_frame = ttk.Frame(main_frame, padding="10")
        solution_frame.grid(row=3, column=0, columnspan=2, sticky="ew")

        self.solution_label = ttk.Label(solution_frame, text="Preço Sugerido:", font=("Helvetica", 12, "bold"))
        self.solution_label.pack()

    def fill_example_data(self):
        """Preenche os campos com o primeiro caso da base para facilitar."""
        example_case = self.model.case_base.iloc[0]
        for feature, entry_widget in self.entries.items():
            entry_widget.insert(0, example_case[feature])

    def find_similar_cases(self):
        # 1. Limpar resultados anteriores
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.solution_label.config(text="Preço Sugerido:")

        # 2. Coletar dados da interface
        new_case = {}
        try:
            for feature, entry in self.entries.items():
                # Tenta converter para float se for numérico, senão mantém como string
                if feature in self.model.numerical_features:
                    new_case[feature] = float(entry.get())
                else:
                    new_case[feature] = entry.get()
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Por favor, insira valores numéricos válidos nos campos de Engine size, Year e Mileage.")
            return

        # 3. Chamar o método retrieve do modelo
        similar_cases = self.model.retrieve(new_case, k=5)

        # 4. Calcular a solução sugerida (média dos preços dos casos similares)
        suggested_price = similar_cases[self.model.solution_feature].mean()
        self.solution_label.config(text=f"Preço Sugerido: ${suggested_price:,.2f}")

        # 5. Exibir os resultados na tabela
        for index, row in similar_cases.iterrows():
            values_to_show = list(row[self.feature_columns + [self.model.solution_feature]])
            self.tree.insert("", "end", values=values_to_show)