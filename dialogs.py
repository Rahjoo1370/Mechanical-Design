import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime, timedelta
from tkcalendar import DateEntry
import re

class CustomerDialog:
    def __init__(self, parent, title="مشتری جدید", customer_data=None):
        self.result = None
        self.parent = parent
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
        
        # Fill data if editing
        if customer_data:
            self.fill_data(customer_data)
        
        # Focus on name field
        self.name_entry.focus()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Name
        ttk.Label(main_frame, text="نام *:").grid(row=0, column=0, sticky='w', pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=40)
        self.name_entry.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Company
        ttk.Label(main_frame, text="شرکت:").grid(row=1, column=0, sticky='w', pady=5)
        self.company_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.company_var, width=40).grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Phone
        ttk.Label(main_frame, text="تلفن:").grid(row=2, column=0, sticky='w', pady=5)
        self.phone_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.phone_var, width=40).grid(row=2, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Email
        ttk.Label(main_frame, text="ایمیل:").grid(row=3, column=0, sticky='w', pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.email_var, width=40).grid(row=3, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Address
        ttk.Label(main_frame, text="آدرس:").grid(row=4, column=0, sticky='nw', pady=5)
        self.address_text = tk.Text(main_frame, width=30, height=3)
        self.address_text.grid(row=4, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Notes
        ttk.Label(main_frame, text="یادداشت:").grid(row=5, column=0, sticky='nw', pady=5)
        self.notes_text = tk.Text(main_frame, width=30, height=4)
        self.notes_text.grid(row=5, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="ذخیره", command=self.save).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="انصراف", command=self.cancel).pack(side=tk.LEFT)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self.save())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def fill_data(self, customer_data):
        """Fill form with existing customer data"""
        self.name_var.set(customer_data.get('name', ''))
        self.company_var.set(customer_data.get('company', ''))
        self.phone_var.set(customer_data.get('phone', ''))
        self.email_var.set(customer_data.get('email', ''))
        
        if customer_data.get('address'):
            self.address_text.insert('1.0', customer_data['address'])
        
        if customer_data.get('notes'):
            self.notes_text.insert('1.0', customer_data['notes'])
    
    def validate_data(self):
        """Validate form data"""
        if not self.name_var.get().strip():
            messagebox.showerror("خطا", "نام مشتری الزامی است.")
            return False
        
        email = self.email_var.get().strip()
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messagebox.showerror("خطا", "فرمت ایمیل صحیح نیست.")
            return False
        
        return True
    
    def save(self):
        """Save customer data"""
        if not self.validate_data():
            return
        
        self.result = {
            'name': self.name_var.get().strip(),
            'company': self.company_var.get().strip(),
            'phone': self.phone_var.get().strip(),
            'email': self.email_var.get().strip(),
            'address': self.address_text.get('1.0', tk.END).strip(),
            'notes': self.notes_text.get('1.0', tk.END).strip()
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()


class WorkReportDialog:
    def __init__(self, parent, customers, title="گزارش کار جدید", report_data=None, selected_customer_id=None):
        self.result = None
        self.parent = parent
        self.customers = customers
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
        
        # Set selected customer
        if selected_customer_id:
            for customer in self.customers:
                if customer['id'] == selected_customer_id:
                    self.customer_var.set(f"{customer['name']} ({customer['id']})")
                    break
        
        # Fill data if editing
        if report_data:
            self.fill_data(report_data)
        
        # Focus on title field
        self.title_entry.focus()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Customer selection
        ttk.Label(main_frame, text="مشتری *:").grid(row=0, column=0, sticky='w', pady=5)
        self.customer_var = tk.StringVar()
        customer_combo = ttk.Combobox(main_frame, textvariable=self.customer_var, state='readonly', width=40)
        customer_combo['values'] = [f"{c['name']} ({c['id']})" for c in self.customers]
        customer_combo.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Report date
        ttk.Label(main_frame, text="تاریخ گزارش:").grid(row=1, column=0, sticky='w', pady=5)
        self.date_entry = DateEntry(main_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Title
        ttk.Label(main_frame, text="عنوان *:").grid(row=2, column=0, sticky='w', pady=5)
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=40)
        self.title_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Status
        ttk.Label(main_frame, text="وضعیت:").grid(row=3, column=0, sticky='w', pady=5)
        self.status_var = tk.StringVar(value="در انتظار")
        status_combo = ttk.Combobox(main_frame, textvariable=self.status_var, state='readonly', width=40)
        status_combo['values'] = ["در انتظار", "در حال انجام", "تکمیل شده", "لغو شده"]
        status_combo.grid(row=3, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Description
        ttk.Label(main_frame, text="توضیحات:").grid(row=4, column=0, sticky='nw', pady=5)
        self.description_text = tk.Text(main_frame, width=30, height=10)
        self.description_text.grid(row=4, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Scrollbar for description
        desc_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.description_text.yview)
        self.description_text.configure(yscrollcommand=desc_scrollbar.set)
        desc_scrollbar.grid(row=4, column=2, sticky='ns', pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        ttk.Button(buttons_frame, text="ذخیره", command=self.save).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="انصراف", command=self.cancel).pack(side=tk.LEFT)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Bind keys
        self.dialog.bind('<Return>', lambda e: self.save())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def fill_data(self, report_data):
        """Fill form with existing report data"""
        # Set customer
        for customer in self.customers:
            if customer['id'] == report_data['customer_id']:
                self.customer_var.set(f"{customer['name']} ({customer['id']})")
                break
        
        # Set date
        if report_data.get('report_date'):
            try:
                report_date = datetime.strptime(report_data['report_date'], '%Y-%m-%d').date()
                self.date_entry.set_date(report_date)
            except:
                pass
        
        self.title_var.set(report_data.get('title', ''))
        self.status_var.set(report_data.get('status', 'در انتظار'))
        
        if report_data.get('description'):
            self.description_text.insert('1.0', report_data['description'])
    
    def validate_data(self):
        """Validate form data"""
        if not self.customer_var.get():
            messagebox.showerror("خطا", "انتخاب مشتری الزامی است.")
            return False
        
        if not self.title_var.get().strip():
            messagebox.showerror("خطا", "عنوان گزارش الزامی است.")
            return False
        
        return True
    
    def save(self):
        """Save work report data"""
        if not self.validate_data():
            return
        
        # Extract customer ID
        customer_text = self.customer_var.get()
        customer_id = int(customer_text.split('(')[-1].split(')')[0])
        
        self.result = {
            'customer_id': customer_id,
            'title': self.title_var.get().strip(),
            'description': self.description_text.get('1.0', tk.END).strip(),
            'status': self.status_var.get(),
            'report_date': self.date_entry.get_date().isoformat()
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()


class FollowUpDialog:
    def __init__(self, parent, customers, title="پیگیری جدید", followup_data=None, selected_customer_id=None):
        self.result = None
        self.parent = parent
        self.customers = customers
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
        
        # Set selected customer
        if selected_customer_id:
            for customer in self.customers:
                if customer['id'] == selected_customer_id:
                    self.customer_var.set(f"{customer['name']} ({customer['id']})")
                    break
        
        # Fill data if editing
        if followup_data:
            self.fill_data(followup_data)
        
        # Focus on title field
        self.title_entry.focus()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Customer selection
        ttk.Label(main_frame, text="مشتری *:").grid(row=0, column=0, sticky='w', pady=5)
        self.customer_var = tk.StringVar()
        customer_combo = ttk.Combobox(main_frame, textvariable=self.customer_var, state='readonly', width=40)
        customer_combo['values'] = [f"{c['name']} ({c['id']})" for c in self.customers]
        customer_combo.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Follow-up date
        ttk.Label(main_frame, text="تاریخ پیگیری *:").grid(row=1, column=0, sticky='w', pady=5)
        self.date_entry = DateEntry(main_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd',
                                   mindate=date.today())
        self.date_entry.grid(row=1, column=1, sticky='w', pady=5, padx=(10, 0))
        
        # Quick date buttons
        quick_dates_frame = ttk.Frame(main_frame)
        quick_dates_frame.grid(row=2, column=1, sticky='w', pady=5, padx=(10, 0))
        
        ttk.Button(quick_dates_frame, text="امروز", 
                  command=lambda: self.set_quick_date(0)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_dates_frame, text="فردا", 
                  command=lambda: self.set_quick_date(1)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_dates_frame, text="هفته آینده", 
                  command=lambda: self.set_quick_date(7)).pack(side=tk.LEFT, padx=(0, 5))
        
        # Title
        ttk.Label(main_frame, text="عنوان *:").grid(row=3, column=0, sticky='w', pady=5)
        self.title_var = tk.StringVar()
        self.title_entry = ttk.Entry(main_frame, textvariable=self.title_var, width=40)
        self.title_entry.grid(row=3, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Description
        ttk.Label(main_frame, text="توضیحات:").grid(row=4, column=0, sticky='nw', pady=5)
        self.description_text = tk.Text(main_frame, width=30, height=8)
        self.description_text.grid(row=4, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="ذخیره", command=self.save).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="انصراف", command=self.cancel).pack(side=tk.LEFT)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Bind keys
        self.dialog.bind('<Return>', lambda e: self.save())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def set_quick_date(self, days_ahead):
        """Set date to a quick option"""
        target_date = date.today() + timedelta(days=days_ahead)
        self.date_entry.set_date(target_date)
    
    def fill_data(self, followup_data):
        """Fill form with existing follow-up data"""
        # Set customer
        for customer in self.customers:
            if customer['id'] == followup_data['customer_id']:
                self.customer_var.set(f"{customer['name']} ({customer['id']})")
                break
        
        # Set date
        if followup_data.get('follow_up_date'):
            try:
                followup_date = datetime.strptime(followup_data['follow_up_date'], '%Y-%m-%d').date()
                self.date_entry.set_date(followup_date)
            except:
                pass
        
        self.title_var.set(followup_data.get('title', ''))
        
        if followup_data.get('description'):
            self.description_text.insert('1.0', followup_data['description'])
    
    def validate_data(self):
        """Validate form data"""
        if not self.customer_var.get():
            messagebox.showerror("خطا", "انتخاب مشتری الزامی است.")
            return False
        
        if not self.title_var.get().strip():
            messagebox.showerror("خطا", "عنوان پیگیری الزامی است.")
            return False
        
        return True
    
    def save(self):
        """Save follow-up data"""
        if not self.validate_data():
            return
        
        # Extract customer ID
        customer_text = self.customer_var.get()
        customer_id = int(customer_text.split('(')[-1].split(')')[0])
        
        self.result = {
            'customer_id': customer_id,
            'title': self.title_var.get().strip(),
            'description': self.description_text.get('1.0', tk.END).strip(),
            'follow_up_date': self.date_entry.get_date().isoformat()
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog"""
        self.dialog.destroy()