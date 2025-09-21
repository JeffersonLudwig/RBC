# Sistema de Avaliação de Preços de Veículos com Raciocínio Baseado em Casos (RBC)

## 📝 Descrição do Projeto

Este projeto é uma aplicação desktop desenvolvida em Python que utiliza o método de **Raciocínio Baseado em Casos (RBC)**, uma área da Inteligência Artificial, para sugerir o preço de carros usados. O sistema compara um novo veículo, inserido pelo usuário, com uma base de dados de vendas passadas e, com base nos carros mais similares, calcula um preço estimado.

## 🛠️ Tecnologias e Bibliotecas

  * **Linguagem:** Python 3
  * **Bibliotecas Principais:**
      * **Pandas:** Para manipulação e pré-processamento da base de dados.
      * **Scikit-learn:** Para a normalização dos dados numéricos (`MinMaxScaler`).
      * **Tkinter:** Para a construção de toda a interface gráfica do usuário (GUI).
      * **Numpy:** Para otimização dos cálculos matemáticos.

-----

## 📁 Estrutura do Projeto

O projeto é organizado de forma modular para separar a lógica de negócio da interface.

```bash
projeto_rbc/
├── data/
│   └── car_sales_data.csv      
│
├── rbc_model.py                
├── gui.py                      
├── main.py                     
└── README.md                   
```

-----

## 🚀 Como Rodar o Projeto

### **Pré-requisitos**

  * **Python** (versão 3.8 ou superior)
  * **pip** (gerenciador de pacotes do Python)

### **1. Configuração do Ambiente**

```bash

python -m venv venv

.\venv\Scripts\activate

pip install pandas scikit-learn numpy
```

### **2. Base de Dados**

  * Certifique-se de que o arquivo `car_sales_data.csv` está localizado dentro de uma pasta chamada `data` na raiz do projeto.
  * Link Base de Dados: https://www.kaggle.com/datasets/msnbehdani/mock-dataset-of-second-hand-car-sales

### **3. Executando a Aplicação**

  * Com o ambiente virtual ativado e as dependências instaladas, execute o seguinte comando no terminal:

<!-- end list -->

```bash
python main.py
```
-----

## 👨‍💻 Estudantes

<table>
  <tr>
    <td align="center">
      <a href="#">
        <img src="https://avatars.githubusercontent.com/u/165969703?v=4" width="100px;" alt="Iraê"/><br>
        <sub>
          <b>Iraê Ervin Gruber da Silva</b>
        </sub>
      </a>
    </td>
    <td align="center">
      <a href="#">
        <img src="https://avatars.githubusercontent.com/u/165967253?s=96&v=4" width="100px;" alt="Jefferson"/><br>
        <sub>
          <b>Jefferson Alan Schmidt Ludwig</b>
        </sub>
      </a>
    </td>
    <td align="center">
      <a href="#">
        <img src="https://avatars.githubusercontent.com/u/166339825?v=4" width="100px;" alt="Lucas"/><br>
        <sub>
          <b>Lucas Maciel Delvalle Kesler</b>
        </sub>
      </a>
    </td>
  </tr>
</table>
