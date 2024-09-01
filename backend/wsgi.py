"""
Entry point for running the Digital Document System application.

This script imports the Flask application instance and runs it
when executed directly.
"""

from main import application

if __name__ == "__main__":
    application.run()