import tkinter as tk
from gui import RBC_GUI

if __name__ == "__main__":
    # Cria a janela principal
    root = tk.Tk()
    
    # Instancia nossa classe da GUI
    app = RBC_GUI(root)
    
    # Inicia o loop principal da aplicação
    root.mainloop()