import sqlite3
import os
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple

class CRMDatabase:
    def __init__(self, db_path: str = "crm_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create customers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    company TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    created_date DATE DEFAULT CURRENT_DATE,
                    notes TEXT
                )
            ''')
            
            # Create work reports table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS work_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    report_date DATE DEFAULT CURRENT_DATE,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'در انتظار',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            ''')
            
            # Create follow-ups table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS follow_ups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER NOT NULL,
                    follow_up_date DATE NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            ''')
            
            conn.commit()
    
    def add_customer(self, name: str, company: str = "", phone: str = "", 
                    email: str = "", address: str = "", notes: str = "") -> int:
        """Add a new customer and return the customer ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO customers (name, company, phone, email, address, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, company, phone, email, address, notes))
            conn.commit()
            return cursor.lastrowid
    
    def get_customers(self, search_term: str = "") -> List[Dict]:
        """Get all customers or search by name/company"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if search_term:
                cursor.execute('''
                    SELECT * FROM customers 
                    WHERE name LIKE ? OR company LIKE ?
                    ORDER BY name
                ''', (f'%{search_term}%', f'%{search_term}%'))
            else:
                cursor.execute('SELECT * FROM customers ORDER BY name')
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_customer_by_id(self, customer_id: int) -> Optional[Dict]:
        """Get customer by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
    
    def update_customer(self, customer_id: int, **kwargs) -> bool:
        """Update customer information"""
        if not kwargs:
            return False
        
        set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
        values = list(kwargs.values()) + [customer_id]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE customers SET {set_clause} WHERE id = ?', values)
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_customer(self, customer_id: int) -> bool:
        """Delete customer and all related records"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Delete related records first
            cursor.execute('DELETE FROM work_reports WHERE customer_id = ?', (customer_id,))
            cursor.execute('DELETE FROM follow_ups WHERE customer_id = ?', (customer_id,))
            cursor.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def add_work_report(self, customer_id: int, title: str, description: str = "", 
                       status: str = "در انتظار", report_date: str = None) -> int:
        """Add a work report for a customer"""
        if report_date is None:
            report_date = date.today().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO work_reports (customer_id, title, description, status, report_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (customer_id, title, description, status, report_date))
            conn.commit()
            return cursor.lastrowid
    
    def get_work_reports(self, customer_id: int = None) -> List[Dict]:
        """Get work reports for a specific customer or all customers"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if customer_id:
                cursor.execute('''
                    SELECT wr.*, c.name as customer_name 
                    FROM work_reports wr
                    JOIN customers c ON wr.customer_id = c.id
                    WHERE wr.customer_id = ?
                    ORDER BY wr.report_date DESC
                ''', (customer_id,))
            else:
                cursor.execute('''
                    SELECT wr.*, c.name as customer_name 
                    FROM work_reports wr
                    JOIN customers c ON wr.customer_id = c.id
                    ORDER BY wr.report_date DESC
                ''')
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def update_work_report(self, report_id: int, **kwargs) -> bool:
        """Update work report"""
        if not kwargs:
            return False
        
        set_clause = ', '.join([f'{key} = ?' for key in kwargs.keys()])
        values = list(kwargs.values()) + [report_id]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE work_reports SET {set_clause} WHERE id = ?', values)
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_work_report(self, report_id: int) -> bool:
        """Delete work report"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM work_reports WHERE id = ?', (report_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def add_follow_up(self, customer_id: int, title: str, follow_up_date: str,
                     description: str = "") -> int:
        """Add a follow-up reminder for a customer"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO follow_ups (customer_id, title, follow_up_date, description)
                VALUES (?, ?, ?, ?)
            ''', (customer_id, title, follow_up_date, description))
            conn.commit()
            return cursor.lastrowid
    
    def get_follow_ups(self, customer_id: int = None, pending_only: bool = False) -> List[Dict]:
        """Get follow-ups for a specific customer or all customers"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = '''
                SELECT fu.*, c.name as customer_name 
                FROM follow_ups fu
                JOIN customers c ON fu.customer_id = c.id
            '''
            params = []
            
            conditions = []
            if customer_id:
                conditions.append('fu.customer_id = ?')
                params.append(customer_id)
            
            if pending_only:
                conditions.append('fu.completed = FALSE')
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            query += ' ORDER BY fu.follow_up_date ASC'
            
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_overdue_follow_ups(self) -> List[Dict]:
        """Get overdue follow-ups (past due date and not completed)"""
        today = date.today().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT fu.*, c.name as customer_name 
                FROM follow_ups fu
                JOIN customers c ON fu.customer_id = c.id
                WHERE fu.follow_up_date < ? AND fu.completed = FALSE
                ORDER BY fu.follow_up_date ASC
            ''', (today,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_today_follow_ups(self) -> List[Dict]:
        """Get today's follow-ups"""
        today = date.today().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT fu.*, c.name as customer_name 
                FROM follow_ups fu
                JOIN customers c ON fu.customer_id = c.id
                WHERE fu.follow_up_date = ? AND fu.completed = FALSE
                ORDER BY fu.follow_up_date ASC
            ''', (today,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def complete_follow_up(self, follow_up_id: int) -> bool:
        """Mark follow-up as completed"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE follow_ups SET completed = TRUE WHERE id = ?', (follow_up_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_follow_up(self, follow_up_id: int) -> bool:
        """Delete follow-up"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM follow_ups WHERE id = ?', (follow_up_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_statistics(self) -> Dict:
        """Get CRM statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total customers
            cursor.execute('SELECT COUNT(*) FROM customers')
            total_customers = cursor.fetchone()[0]
            
            # Total work reports
            cursor.execute('SELECT COUNT(*) FROM work_reports')
            total_reports = cursor.fetchone()[0]
            
            # Pending follow-ups
            cursor.execute('SELECT COUNT(*) FROM follow_ups WHERE completed = FALSE')
            pending_follow_ups = cursor.fetchone()[0]
            
            # Overdue follow-ups
            today = date.today().isoformat()
            cursor.execute('SELECT COUNT(*) FROM follow_ups WHERE follow_up_date < ? AND completed = FALSE', (today,))
            overdue_follow_ups = cursor.fetchone()[0]
            
            return {
                'total_customers': total_customers,
                'total_reports': total_reports,
                'pending_follow_ups': pending_follow_ups,
                'overdue_follow_ups': overdue_follow_ups
            }