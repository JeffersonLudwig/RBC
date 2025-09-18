import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class RBCModel:
    def __init__(self, data_path=r'projeto_rbc\data\car_sales_data.csv'):
        """
        Inicializa o modelo RBC, carrega e pré-processa a base de dados de carros.
        """
        # --- 1. Carregar a Base de Casos ---
        try:
            self.case_base = pd.read_csv(data_path)
        except FileNotFoundError:
            print(f"Erro: O arquivo '{data_path}' não foi encontrado.")
            print("Certifique-se de que o arquivo CSV está no caminho correto.")
            exit()

        # Tratamento de valores ausentes (simplesmente removendo as linhas)
        self.case_base.dropna(inplace=True)

        # --- 2. Mapeamento e Pré-processamento dos Dados ---
        # Separar os atributos entre numéricos e categóricos
        self.numerical_features = ['Engine size', 'Year of manufacture', 'Mileage']
        self.categorical_features = ['Manufacturer', 'Model', 'Fuel type']
        self.solution_feature = 'Price' # O que queremos "prever"

        # Guardar os dados originais para exibição
        self.original_case_base_features = self.case_base[self.categorical_features + self.numerical_features]
        
        # a) Normalização dos dados numéricos
        self.scaler = MinMaxScaler()
        normalized_numerical = self.scaler.fit_transform(self.case_base[self.numerical_features])
        
        # b) Conversão de dados categóricos (One-Hot Encoding)
        # Esta técnica cria novas colunas para cada categoria, com valor 0 ou 1.
        # É a forma mais comum de tratar dados categóricos para cálculos de distância.
        dummies = pd.get_dummies(self.case_base[self.categorical_features])
        self.dummies_columns = dummies.columns # Guardar a ordem e nome das colunas
        
        # c) Combinar os dados pré-processados numa única matriz de características
        self.processed_case_base = np.hstack([normalized_numerical, dummies.values])

    def _preprocess_new_case(self, new_case):
        """
        Pré-processa um novo caso para que tenha o mesmo formato da base de casos.
        """
        # Separar dados numéricos e categóricos do novo caso
        numerical_values = pd.DataFrame([new_case])[self.numerical_features]
        categorical_values = pd.DataFrame([new_case])[self.categorical_features]

        # Normalizar os dados numéricos (usando o mesmo scaler)
        normalized_numerical = self.scaler.transform(numerical_values)

        # Aplicar One-Hot Encoding (usando as mesmas colunas da base original)
        new_case_dummies = pd.get_dummies(categorical_values)
        # Reindexar para garantir que o novo caso tenha exatamente as mesmas colunas
        # que a base de casos, preenchendo com 0 as categorias não presentes.
        new_case_processed_cat = new_case_dummies.reindex(columns=self.dummies_columns, fill_value=0)
        
        # Combinar e retornar
        return np.hstack([normalized_numerical, new_case_processed_cat.values])

    def euclidean_distance(self, x1, x2):
        """
        Calcula a Distância Euclidiana entre dois vetores.
        """
        return np.sqrt(np.sum((x1 - x2)**2))

    def retrieve(self, new_case, k=5):
        """
        Recupera os 'k' casos mais similares ao novo caso.
        
        Args:
            new_case (dict): Um dicionário com os valores do novo problema.
            k (int): O número de vizinhos mais próximos a retornar.

        Returns:
            DataFrame: Um DataFrame do Pandas com os k casos mais similares.
        """
        # 1. Pré-processar o novo caso
        processed_new_case = self._preprocess_new_case(new_case)

        # 2. Calcular a distância para todos os casos na base
        distances = []
        for i, case_features in enumerate(self.processed_case_base):
            dist = self.euclidean_distance(processed_new_case, case_features)
            distances.append((i, dist))

        # 3. Ordenar os casos pela distância
        distances.sort(key=lambda x: x[1])

        # 4. Selecionar os 'k' casos mais similares
        similar_indices = [index for index, dist in distances[:k]]
        
        # Retorna as linhas correspondentes da base de casos original (com todas as colunas)
        return self.case_base.iloc[similar_indices]

# Exemplo de como usar a classe (para testes)
if __name__ == '__main__':
    model = RBCModel()
    
    # Criando um novo problema (um novo carro para avaliar o preço)
    new_car = {
        'Manufacturer': 'Ford',
        'Model': 'Fiesta',
        'Fuel type': 'Petrol',
        'Engine size': 1.0,
        'Year of manufacture': 2017,
        'Mileage': 30000
    }

    similar_cases = model.retrieve(new_car, k=5)

    print("--- Novo Problema (Carro para Avaliar) ---")
    print(pd.DataFrame([new_car]))
    print("\n--- Casos Mais Similares Encontrados (e seus preços) ---")
    print(similar_cases)