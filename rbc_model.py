import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class RBCModel:
    # O caminho agora aponta para a pasta 'data' que acabamos de organizar
    def __init__(self, data_path=r'projeto_rbc/data/car_sales_data.csv'):
        print("--- [MODELO] Iniciando o RBCModel ---")
        
        self.translation_map = {
            'Manufacturer': 'Fabricante', 'Model': 'Modelo', 'Engine size': 'Motor',
            'Fuel type': 'Combustível', 'Year of manufacture': 'Ano',
            'Mileage': 'Quilometragem', 'Price': 'Preço'
        }
        self.inv_translation_map = {v: k for k, v in self.translation_map.items()}

        try:
            self.case_base_original = pd.read_csv(data_path)
            print(f"--- [MODELO] Sucesso! Carregado {len(self.case_base_original)} casos do arquivo.")
        except FileNotFoundError:
            print(f"### ERRO CRÍTICO: O arquivo '{data_path}' não foi encontrado! ###")
            print("Verifique se a pasta 'data' existe e se o arquivo CSV está dentro dela.")
            exit()
            
        # Limpeza defensiva: remove espaços extras dos nomes das colunas e dados
        self.case_base_original.columns = self.case_base_original.columns.str.strip()
        for col in ['Manufacturer', 'Model', 'Fuel type']:
            if col in self.case_base_original.columns:
                self.case_base_original[col] = self.case_base_original[col].str.strip()

        self.case_base_original.dropna(inplace=True)

        self.numerical_features_en = ['Engine size', 'Year of manufacture', 'Mileage']
        self.categorical_features_en = ['Manufacturer', 'Model', 'Fuel type']
        self.solution_feature_en = 'Price'
        
        self.numerical_features_pt = [self.translation_map[f] for f in self.numerical_features_en]
        self.categorical_features_pt = [self.translation_map[f] for f in self.categorical_features_en]
        self.solution_feature_pt = self.translation_map[self.solution_feature_en]

        self.scaler = MinMaxScaler()
        normalized_numerical = self.scaler.fit_transform(self.case_base_original[self.numerical_features_en])
        
        dummies = pd.get_dummies(self.case_base_original[self.categorical_features_en])
        self.dummies_columns = dummies.columns
        
        self.processed_case_base = np.hstack([normalized_numerical, dummies.values])
        print("--- [MODELO] Pré-processamento concluído. Modelo pronto. ---")

    def _preprocess_new_case(self, new_case_en):
        # ... (código sem alterações)
        numerical_values = pd.DataFrame([new_case_en])[self.numerical_features_en]
        categorical_values = pd.DataFrame([new_case_en])[self.categorical_features_en]
        normalized_numerical = self.scaler.transform(numerical_values)
        new_case_dummies = pd.get_dummies(categorical_values)
        new_case_processed_cat = new_case_dummies.reindex(columns=self.dummies_columns, fill_value=0)
        return np.hstack([normalized_numerical, new_case_processed_cat.values])

    def euclidean_distance(self, x1, x2):
        return np.sqrt(np.sum((x1 - x2)**2))

    def retrieve(self, new_case_en, k=5):
        print("\n--- [BUSCA] Iniciando nova busca de similaridade ---")
        manufacturer = new_case_en['Manufacturer']
        print(f"--- [BUSCA] Filtro principal: Fabricante = '{manufacturer}'")
        
        filtered_case_base = self.case_base_original[self.case_base_original['Manufacturer'] == manufacturer]
        print(f"--- [BUSCA] Encontrados {len(filtered_case_base)} casos para este fabricante.")
        
        if filtered_case_base.empty:
            print("--- [BUSCA] Nenhum caso encontrado. Retornando vazio.")
            return pd.DataFrame()

        filtered_indices = filtered_case_base.index
        filtered_processed_data = self.processed_case_base[filtered_indices]
        
        processed_new_case = self._preprocess_new_case(new_case_en)

        distances = []
        for i, case_features in enumerate(filtered_processed_data):
            dist = self.euclidean_distance(processed_new_case, case_features)
            original_index = filtered_indices[i]
            distances.append((original_index, dist))

        distances.sort(key=lambda x: x[1])
        similar_indices = [index for index, dist in distances[:k]]
        
        result = self.case_base_original.loc[similar_indices]
        print("--- [BUSCA] Busca concluída. Estes são os resultados:")
        print(result[['Manufacturer', 'Model', 'Year of manufacture', 'Price']])
        
        return result.rename(columns=self.translation_map)