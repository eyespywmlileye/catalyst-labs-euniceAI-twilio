import sqlite3
from datetime import date, datetime
from typing import Optional
from langchain_core.tools import tool

import pytz
from langchain_core.runnables import ensure_config

class BookingManager:
    db: str = None
    def __init__(self, db_path: str):
        global db
        db = db_path

    @tool
    def fetch_user_bookings(self) -> list[dict]:
        """Fetch all bookings for the user along with relevant booking information.

        Returns:
            A list of dictionaries where each dictionary contains the booking details
            such as name, surname, email, phone number, service name, booking date,
            and confirmation status for each booking belonging to the user.
        """
        global db
        config = ensure_config()  # Fetch from the context
        configuration = config.get("configurable", {})
        booking_id = configuration.get("booking_id", None)
        if not booking_id:
            raise ValueError("No passenger ID configured.")

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        query = """
        SELECT 
            booking_id, name, surname, email, phone_number,
            service_name, booking_date, confirmed
        FROM 
            bookings
        WHERE 
            booking_id = ?
        """
        cursor.execute(query, (booking_id,))
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]

        cursor.close()
        conn.close()

        return results
        


    @tool
    def create_booking(
        name: str,
        surname: str,
        email: str,
        phone_number: str,
        service_name: str,
        booking_date: datetime,
    ) -> str:
        """Create a new booking in the business bookings table."""
        global db
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        # check if the values are valid

        if not name:
            raise ValueError("Please provide your name")
        if not surname:
            raise ValueError("Please provide your surname")
        if not email:
            raise ValueError("Please provide your email")
        if not phone_number:
            raise ValueError("Please provide your phone number")
        if not service_name:
            raise ValueError("Please provide the service name")

        cursor.execute(
            """
            INSERT INTO bookings (name, surname, email, phone_number, service_name, booking_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, surname, email, phone_number, service_name, booking_date),
        )
        conn.commit()
        cursor.close()
        conn.close()

        return "Booking created successfully."

    @staticmethod
    @tool
    def fetch_bookings(booking_id: int) -> list[dict]:
        """Fetch all bookings for a user based on passenger ID."""
        global db
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        query = """
        SELECT * FROM bookings WHERE booking_id = ?
        """
        cursor.execute(query, (booking_id,))
        rows = cursor.fetchall()
        column_names = [column[0] for column in cursor.description]
        results = [dict(zip(column_names, row)) for row in rows]

        cursor.close()
        conn.close()

        return results


    @tool
    def update_booking_status(booking_id: int, confirmed: bool) -> str:
        """Update the confirmation status of a booking."""
        global db
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE bookings SET confirmed = ? WHERE booking_id = ?",
            (confirmed, booking_id),
        )
        conn.commit()

        cursor.close()
        conn.close()

        return "Booking status updated successfully."
    
    @tool
    def update_booking_date(booking_id: int, new_date: datetime) -> str:
        """Update the Date of a booking."""
        global db
        
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE bookings SET booking_date = ? WHERE booking_id = ?",
            (new_date, booking_id),
        )
        conn.commit()

        cursor.close()
        conn.close()

        return "Booking Date updated successfully."
    
    @tool
    def update_booking_service(booking_id: int, new_service: str) -> str:
        """Update the Service user has booked for."""

        global db
        

        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE bookings SET service_name = ? WHERE booking_id = ?",
            (new_service, booking_id),
        )
        conn.commit()

        cursor.close()
        conn.close()

        return "Booking Service updated successfully."


    @tool
    def cancel_booking(booking_id: int) -> str:
        """Cancel a booking and remove it from the database."""
        global db
        
        conn = sqlite3.connect(db)
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM bookings WHERE booking_id = ?",
            (booking_id,),
        )
        conn.commit()

        cursor.close()
        conn.close()

        return "Booking successfully cancelled."