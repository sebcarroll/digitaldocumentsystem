from app.services.google_drive.core import DriveCore

def get_drive_core(session):
    if 'credentials' not in session:
        raise ValueError("User not authenticated")
    return DriveCore(session['credentials'])