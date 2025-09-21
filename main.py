from main_app import App
from db_manager import DBManager

if __name__ == "__main__":
    # Set the appearance mode
    # Options: "System" (default), "Dark", "Light"
    import customtkinter
    customtkinter.set_appearance_mode("Dark")
    customtkinter.set_default_color_theme("blue")

    db_manager = None
    try:
        # Initialize the database manager
        db_manager = DBManager()
        
        # Create and run the application
        app = App(db_manager=db_manager)
        app.mainloop()

    finally:
        # Ensure the database connection is closed when the app exits
        if db_manager:
            db_manager.close()
