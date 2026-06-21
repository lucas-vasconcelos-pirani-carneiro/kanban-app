import sys
import os
import src.app

print("run_app.py: Iniciando script...")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '')))
print("run_app.py: sys.path configurado. Tentando importar src.app...")

print("run_app.py: Chamando create_app() e mainloop() de src.app...")
if hasattr(src.app, 'create_app') and callable(src.app.create_app):
    app_instance = src.app.create_app()
    app_instance.mainloop()
else:
    print("run_app.py: src.app não expõe create_app diretamente. Tentando importar de interface_manager...")
    from src.views.interface_manager import create_app
    app_instance = create_app()
    app_instance.mainloop()

print("run_app.py: Aplicação finalizada.")
