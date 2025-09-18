import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class RBCModel:
    def __init__(self, data_path=r'projeto_rbc/data/car_sales_data.csv'):
        # ... (código de diagnóstico removido para limpeza) ...
        
        # --- Dicionário de tradução de colunas ---
        self.translation_map = {
            'Manufacturer': 'Fabricante', 'Model': 'Modelo', 'Engine size': 'Motor',
            'Fuel type': 'Combustível', 'Year of manufacture': 'Ano',
            'Mileage': 'Quilometragem', 'Price': 'Preço'
        }
        self.inv_translation_map = {v: k for k, v in self.translation_map.items()}
        
        # --- NOVO: Dicionário para tradução dos DADOS de combustível ---
        self.fuel_translation = {'Petrol': 'Gasolina', 'Diesel': 'Diesel', 'Hybrid': 'Híbrido'}
        self.inv_fuel_translation = {v: k for k, v in self.fuel_translation.items()}

        try:
            self.case_base_original = pd.read_csv(data_path)
        except FileNotFoundError:
            print(f"### ERRO CRÍTICO: O arquivo '{data_path}' não foi encontrado! ###")
            exit()
            
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

    def _preprocess_new_case(self, new_case_en):
        numerical_values = pd.DataFrame([new_case_en])[self.numerical_features_en]
        categorical_values = pd.DataFrame([new_case_en])[self.categorical_features_en]
        normalized_numerical = self.scaler.transform(numerical_values)
        new_case_dummies = pd.get_dummies(categorical_values)
        new_case_processed_cat = new_case_dummies.reindex(columns=self.dummies_columns, fill_value=0)
        return np.hstack([normalized_numerical, new_case_processed_cat.values])

    def euclidean_distance(self, x1, x2):
        return np.sqrt(np.sum((x1 - x2)**2))

    def retrieve(self, new_case_en, k=5):
        manufacturer = new_case_en['Manufacturer']
        filtered_case_base = self.case_base_original[self.case_base_original['Manufacturer'] == manufacturer]
        
        if filtered_case_base.empty:
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
        return result.rename(columns=self.translation_map)