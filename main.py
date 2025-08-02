import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, date, timedelta
import threading
import time
from database import CRMDatabase
from typing import Optional
from main_methods import CRMAppMethods

class CRMApp(CRMAppMethods):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("سیستم مدیریت ارتباط با مشتری (CRM)")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize database
        self.db = CRMDatabase()
        
        # Current selected customer
        self.current_customer_id = None
        
        # Setup GUI
        self.setup_styles()
        self.create_main_interface()
        
        # Start alarm checker
        self.start_alarm_checker()
    
    def setup_styles(self):
        """Setup custom styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), background='#f0f0f0')
        style.configure('Custom.Treeview.Heading', font=('Arial', 10, 'bold'))
    
    def create_main_interface(self):
        """Create the main interface"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="سیستم مدیریت ارتباط با مشتری", 
                               style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_customers_tab()
        self.create_reports_tab()
        self.create_followups_tab()
        
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def create_dashboard_tab(self):
        """Create dashboard tab"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="داشبورد")
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(dashboard_frame, text="آمار کلی", padding=20)
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Statistics labels
        self.stats_labels = {}
        stats_info = [
            ("total_customers", "تعداد کل مشتریان:"),
            ("total_reports", "تعداد کل گزارش‌ها:"),
            ("pending_follow_ups", "پیگیری‌های در انتظار:"),
            ("overdue_follow_ups", "پیگیری‌های عقب‌افتاده:")
        ]
        
        for i, (key, text) in enumerate(stats_info):
            row = i // 2
            col = i % 2
            
            label_frame = ttk.Frame(stats_frame)
            label_frame.grid(row=row, column=col, padx=20, pady=10, sticky='w')
            
            ttk.Label(label_frame, text=text, font=('Arial', 11)).pack(side=tk.LEFT)
            self.stats_labels[key] = ttk.Label(label_frame, text="0", 
                                             font=('Arial', 11, 'bold'), 
                                             foreground='blue')
            self.stats_labels[key].pack(side=tk.LEFT, padx=(10, 0))
        
        # Today's follow-ups
        today_frame = ttk.LabelFrame(dashboard_frame, text="پیگیری‌های امروز", padding=10)
        today_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Today's follow-ups treeview
        columns = ('customer', 'title', 'description')
        self.today_tree = ttk.Treeview(today_frame, columns=columns, show='headings', height=8)
        
        self.today_tree.heading('customer', text='مشتری')
        self.today_tree.heading('title', text='عنوان')
        self.today_tree.heading('description', text='توضیحات')
        
        self.today_tree.column('customer', width=200)
        self.today_tree.column('title', width=200)
        self.today_tree.column('description', width=300)
        
        # Scrollbar for today's follow-ups
        today_scrollbar = ttk.Scrollbar(today_frame, orient=tk.VERTICAL, command=self.today_tree.yview)
        self.today_tree.configure(yscrollcommand=today_scrollbar.set)
        
        self.today_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        today_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons frame
        buttons_frame = ttk.Frame(today_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="تکمیل پیگیری", 
                  command=self.complete_today_followup).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="بروزرسانی", 
                  command=self.refresh_dashboard).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="بررسی یادآوری‌ها", 
                  command=self.manual_alarm_check).pack(side=tk.LEFT)
        
        # Load initial data
        self.refresh_dashboard()
    
    def create_customers_tab(self):
        """Create customers management tab"""
        customers_frame = ttk.Frame(self.notebook)
        self.notebook.add(customers_frame, text="مشتریان")
        
        # Search frame
        search_frame = ttk.Frame(customers_frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="جستجو:").pack(side=tk.LEFT, padx=(0, 10))
        self.customer_search_var = tk.StringVar()
        self.customer_search_var.trace('w', self.search_customers)
        search_entry = ttk.Entry(search_frame, textvariable=self.customer_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # Buttons
        ttk.Button(search_frame, text="مشتری جدید", 
                  command=self.add_customer).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(search_frame, text="ویرایش", 
                  command=self.edit_customer).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(search_frame, text="حذف", 
                  command=self.delete_customer).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(search_frame, text="بروزرسانی", 
                  command=self.refresh_customers).pack(side=tk.LEFT)
        
        # Customers treeview
        columns = ('id', 'name', 'company', 'phone', 'email')
        self.customers_tree = ttk.Treeview(customers_frame, columns=columns, show='headings')
        
        self.customers_tree.heading('id', text='شناسه')
        self.customers_tree.heading('name', text='نام')
        self.customers_tree.heading('company', text='شرکت')
        self.customers_tree.heading('phone', text='تلفن')
        self.customers_tree.heading('email', text='ایمیل')
        
        self.customers_tree.column('id', width=60)
        self.customers_tree.column('name', width=200)
        self.customers_tree.column('company', width=200)
        self.customers_tree.column('phone', width=150)
        self.customers_tree.column('email', width=200)
        
        # Scrollbar for customers
        customers_scrollbar = ttk.Scrollbar(customers_frame, orient=tk.VERTICAL, 
                                          command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=customers_scrollbar.set)
        
        self.customers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 10))
        customers_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
        
        # Bind double click
        self.customers_tree.bind('<Double-1>', self.on_customer_double_click)
        
        # Load customers
        self.refresh_customers()
    
    def create_reports_tab(self):
        """Create work reports tab"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="گزارش‌های کار")
        
        # Top frame for customer selection and buttons
        top_frame = ttk.Frame(reports_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Customer selection
        ttk.Label(top_frame, text="مشتری:").pack(side=tk.LEFT, padx=(0, 10))
        self.selected_customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(top_frame, textvariable=self.selected_customer_var, 
                                         state='readonly', width=30)
        self.customer_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.customer_combo.bind('<<ComboboxSelected>>', self.on_customer_selected)
        
        # Buttons
        ttk.Button(top_frame, text="گزارش جدید", 
                  command=self.add_work_report).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(top_frame, text="ویرایش", 
                  command=self.edit_work_report).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(top_frame, text="حذف", 
                  command=self.delete_work_report).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(top_frame, text="بروزرسانی", 
                  command=self.refresh_reports).pack(side=tk.LEFT)
        
        # Reports treeview
        columns = ('id', 'customer', 'date', 'title', 'status')
        self.reports_tree = ttk.Treeview(reports_frame, columns=columns, show='headings')
        
        self.reports_tree.heading('id', text='شناسه')
        self.reports_tree.heading('customer', text='مشتری')
        self.reports_tree.heading('date', text='تاریخ')
        self.reports_tree.heading('title', text='عنوان')
        self.reports_tree.heading('status', text='وضعیت')
        
        self.reports_tree.column('id', width=60)
        self.reports_tree.column('customer', width=200)
        self.reports_tree.column('date', width=100)
        self.reports_tree.column('title', width=300)
        self.reports_tree.column('status', width=100)
        
        # Scrollbar for reports
        reports_scrollbar = ttk.Scrollbar(reports_frame, orient=tk.VERTICAL, 
                                        command=self.reports_tree.yview)
        self.reports_tree.configure(yscrollcommand=reports_scrollbar.set)
        
        self.reports_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 10))
        reports_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
        
        # Load data
        self.refresh_customer_combo()
        self.refresh_reports()
    
    def create_followups_tab(self):
        """Create follow-ups tab"""
        followups_frame = ttk.Frame(self.notebook)
        self.notebook.add(followups_frame, text="پیگیری‌ها")
        
        # Top frame
        top_frame = ttk.Frame(followups_frame)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Customer selection
        ttk.Label(top_frame, text="مشتری:").pack(side=tk.LEFT, padx=(0, 10))
        self.followup_customer_var = tk.StringVar()
        self.followup_customer_combo = ttk.Combobox(top_frame, textvariable=self.followup_customer_var, 
                                                  state='readonly', width=30)
        self.followup_customer_combo.pack(side=tk.LEFT, padx=(0, 20))
        self.followup_customer_combo.bind('<<ComboboxSelected>>', self.on_followup_customer_selected)
        
        # Filter options
        self.show_completed_var = tk.BooleanVar()
        ttk.Checkbutton(top_frame, text="نمایش تکمیل شده‌ها", 
                       variable=self.show_completed_var,
                       command=self.refresh_followups).pack(side=tk.LEFT, padx=(20, 0))
        
        # Buttons frame
        buttons_frame = ttk.Frame(followups_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(buttons_frame, text="پیگیری جدید", 
                  command=self.add_followup).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="تکمیل", 
                  command=self.complete_followup).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="حذف", 
                  command=self.delete_followup).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="بروزرسانی", 
                  command=self.refresh_followups).pack(side=tk.LEFT)
        
        # Follow-ups treeview
        columns = ('id', 'customer', 'date', 'title', 'completed')
        self.followups_tree = ttk.Treeview(followups_frame, columns=columns, show='headings')
        
        self.followups_tree.heading('id', text='شناسه')
        self.followups_tree.heading('customer', text='مشتری')
        self.followups_tree.heading('date', text='تاریخ پیگیری')
        self.followups_tree.heading('title', text='عنوان')
        self.followups_tree.heading('completed', text='وضعیت')
        
        self.followups_tree.column('id', width=60)
        self.followups_tree.column('customer', width=200)
        self.followups_tree.column('date', width=120)
        self.followups_tree.column('title', width=300)
        self.followups_tree.column('completed', width=100)
        
        # Scrollbar for follow-ups
        followups_scrollbar = ttk.Scrollbar(followups_frame, orient=tk.VERTICAL, 
                                          command=self.followups_tree.yview)
        self.followups_tree.configure(yscrollcommand=followups_scrollbar.set)
        
        self.followups_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=(0, 10))
        followups_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 10))
        
        # Load data
        self.refresh_followup_customer_combo()
        self.refresh_followups()
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        # Update statistics
        stats = self.db.get_statistics()
        for key, value in stats.items():
            if key in self.stats_labels:
                self.stats_labels[key].config(text=str(value))
                # Color code overdue follow-ups
                if key == 'overdue_follow_ups' and value > 0:
                    self.stats_labels[key].config(foreground='red')
                else:
                    self.stats_labels[key].config(foreground='blue')
        
        # Update today's follow-ups
        self.today_tree.delete(*self.today_tree.get_children())
        today_followups = self.db.get_today_follow_ups()
        for followup in today_followups:
            self.today_tree.insert('', 'end', values=(
                followup['customer_name'],
                followup['title'],
                followup['description'] or ''
            ), tags=(followup['id'],))
    
    def refresh_customers(self):
        """Refresh customers list"""
        search_term = self.customer_search_var.get()
        customers = self.db.get_customers(search_term)
        
        self.customers_tree.delete(*self.customers_tree.get_children())
        for customer in customers:
            self.customers_tree.insert('', 'end', values=(
                customer['id'],
                customer['name'],
                customer['company'] or '',
                customer['phone'] or '',
                customer['email'] or ''
            ))
    
    def search_customers(self, *args):
        """Search customers as user types"""
        self.refresh_customers()
    
    def on_customer_double_click(self, event):
        """Handle customer double click"""
        selection = self.customers_tree.selection()
        if selection:
            item = self.customers_tree.item(selection[0])
            customer_id = item['values'][0]
            self.current_customer_id = customer_id
            # Switch to reports tab
            self.notebook.select(2)  # Reports tab
            # Update customer combo
            customer = self.db.get_customer_by_id(customer_id)
            if customer:
                self.selected_customer_var.set(f"{customer['name']} ({customer['id']})")
                self.refresh_reports()
    
    def on_tab_changed(self, event):
        """Handle tab change"""
        selected_tab = event.widget.tab('current')['text']
        if selected_tab == "داشبورد":
            self.refresh_dashboard()
        elif selected_tab == "مشتریان":
            self.refresh_customers()
        elif selected_tab == "گزارش‌های کار":
            self.refresh_customer_combo()
            self.refresh_reports()
        elif selected_tab == "پیگیری‌ها":
            self.refresh_followup_customer_combo()
            self.refresh_followups()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = CRMApp()
    app.run()