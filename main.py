from db import init_db
from ui import FinancialApp

if __name__ == "__main__":
    init_db()
    app = FinancialApp()
    app.mainloop()