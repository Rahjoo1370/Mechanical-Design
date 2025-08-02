import tkinter as tk
from tkinter import messagebox
from dialogs import CustomerDialog, WorkReportDialog, FollowUpDialog
import threading
import time
import winsound  # For Windows sound alerts
from datetime import date

class CRMAppMethods:
    """Additional methods for CRM Application"""
    
    # Customer Management Methods
    def add_customer(self):
        """Add new customer"""
        dialog = CustomerDialog(self.root)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                customer_id = self.db.add_customer(**dialog.result)
                messagebox.showinfo("موفقیت", f"مشتری جدید با شناسه {customer_id} اضافه شد.")
                self.refresh_customers()
                self.refresh_customer_combo()
                self.refresh_followup_customer_combo()
                self.refresh_dashboard()
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در افزودن مشتری: {str(e)}")
    
    def edit_customer(self):
        """Edit selected customer"""
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("هشدار", "لطفاً یک مشتری را انتخاب کنید.")
            return
        
        item = self.customers_tree.item(selection[0])
        customer_id = item['values'][0]
        
        # Get customer data
        customer_data = self.db.get_customer_by_id(customer_id)
        if not customer_data:
            messagebox.showerror("خطا", "مشتری یافت نشد.")
            return
        
        dialog = CustomerDialog(self.root, "ویرایش مشتری", customer_data)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                success = self.db.update_customer(customer_id, **dialog.result)
                if success:
                    messagebox.showinfo("موفقیت", "اطلاعات مشتری بروزرسانی شد.")
                    self.refresh_customers()
                    self.refresh_customer_combo()
                    self.refresh_followup_customer_combo()
                else:
                    messagebox.showerror("خطا", "خطا در بروزرسانی مشتری.")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در بروزرسانی مشتری: {str(e)}")
    
    def delete_customer(self):
        """Delete selected customer"""
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showwarning("هشدار", "لطفاً یک مشتری را انتخاب کنید.")
            return
        
        item = self.customers_tree.item(selection[0])
        customer_id = item['values'][0]
        customer_name = item['values'][1]
        
        # Confirm deletion
        result = messagebox.askyesno("تأیید حذف", 
                                   f"آیا مطمئن هستید که می‌خواهید مشتری '{customer_name}' و تمام اطلاعات مرتبط را حذف کنید؟")
        
        if result:
            try:
                success = self.db.delete_customer(customer_id)
                if success:
                    messagebox.showinfo("موفقیت", "مشتری حذف شد.")
                    self.refresh_customers()
                    self.refresh_customer_combo()
                    self.refresh_followup_customer_combo()
                    self.refresh_reports()
                    self.refresh_followups()
                    self.refresh_dashboard()
                else:
                    messagebox.showerror("خطا", "خطا در حذف مشتری.")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در حذف مشتری: {str(e)}")
    
    # Work Reports Methods
    def refresh_customer_combo(self):
        """Refresh customer combo box for reports"""
        customers = self.db.get_customers()
        customer_list = ["همه مشتریان"] + [f"{c['name']} ({c['id']})" for c in customers]
        self.customer_combo['values'] = customer_list
        if not self.selected_customer_var.get():
            self.selected_customer_var.set("همه مشتریان")
    
    def on_customer_selected(self, event):
        """Handle customer selection change"""
        self.refresh_reports()
    
    def get_selected_customer_id(self):
        """Get currently selected customer ID"""
        selected = self.selected_customer_var.get()
        if selected == "همه مشتریان" or not selected:
            return None
        try:
            return int(selected.split('(')[-1].split(')')[0])
        except:
            return None
    
    def refresh_reports(self):
        """Refresh work reports list"""
        customer_id = self.get_selected_customer_id()
        reports = self.db.get_work_reports(customer_id)
        
        self.reports_tree.delete(*self.reports_tree.get_children())
        for report in reports:
            self.reports_tree.insert('', 'end', values=(
                report['id'],
                report['customer_name'],
                report['report_date'],
                report['title'],
                report['status']
            ))
    
    def add_work_report(self):
        """Add new work report"""
        customers = self.db.get_customers()
        if not customers:
            messagebox.showwarning("هشدار", "ابتدا باید حداقل یک مشتری اضافه کنید.")
            return
        
        selected_customer_id = self.get_selected_customer_id()
        dialog = WorkReportDialog(self.root, customers, selected_customer_id=selected_customer_id)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                report_id = self.db.add_work_report(**dialog.result)
                messagebox.showinfo("موفقیت", f"گزارش کار جدید با شناسه {report_id} اضافه شد.")
                self.refresh_reports()
                self.refresh_dashboard()
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در افزودن گزارش: {str(e)}")
    
    def edit_work_report(self):
        """Edit selected work report"""
        selection = self.reports_tree.selection()
        if not selection:
            messagebox.showwarning("هشدار", "لطفاً یک گزارش را انتخاب کنید.")
            return
        
        item = self.reports_tree.item(selection[0])
        report_id = item['values'][0]
        
        # Get report data (we need to fetch from database to get all fields)
        reports = self.db.get_work_reports()
        report_data = next((r for r in reports if r['id'] == report_id), None)
        
        if not report_data:
            messagebox.showerror("خطا", "گزارش یافت نشد.")
            return
        
        customers = self.db.get_customers()
        dialog = WorkReportDialog(self.root, customers, "ویرایش گزارش کار", report_data)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                success = self.db.update_work_report(report_id, **dialog.result)
                if success:
                    messagebox.showinfo("موفقیت", "گزارش کار بروزرسانی شد.")
                    self.refresh_reports()
                else:
                    messagebox.showerror("خطا", "خطا در بروزرسانی گزارش.")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در بروزرسانی گزارش: {str(e)}")
    
    def delete_work_report(self):
        """Delete selected work report"""
        selection = self.reports_tree.selection()
        if not selection:
            messagebox.showwarning("هشدار", "لطفاً یک گزارش را انتخاب کنید.")
            return
        
        item = self.reports_tree.item(selection[0])
        report_id = item['values'][0]
        report_title = item['values'][3]
        
        # Confirm deletion
        result = messagebox.askyesno("تأیید حذف", 
                                   f"آیا مطمئن هستید که می‌خواهید گزارش '{report_title}' را حذف کنید؟")
        
        if result:
            try:
                success = self.db.delete_work_report(report_id)
                if success:
                    messagebox.showinfo("موفقیت", "گزارش کار حذف شد.")
                    self.refresh_reports()
                    self.refresh_dashboard()
                else:
                    messagebox.showerror("خطا", "خطا در حذف گزارش.")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در حذف گزارش: {str(e)}")
    
    # Follow-up Methods
    def refresh_followup_customer_combo(self):
        """Refresh customer combo box for follow-ups"""
        customers = self.db.get_customers()
        customer_list = ["همه مشتریان"] + [f"{c['name']} ({c['id']})" for c in customers]
        self.followup_customer_combo['values'] = customer_list
        if not self.followup_customer_var.get():
            self.followup_customer_var.set("همه مشتریان")
    
    def on_followup_customer_selected(self, event):
        """Handle follow-up customer selection change"""
        self.refresh_followups()
    
    def get_selected_followup_customer_id(self):
        """Get currently selected customer ID for follow-ups"""
        selected = self.followup_customer_var.get()
        if selected == "همه مشتریان" or not selected:
            return None
        try:
            return int(selected.split('(')[-1].split(')')[0])
        except:
            return None
    
    def refresh_followups(self):
        """Refresh follow-ups list"""
        customer_id = self.get_selected_followup_customer_id()
        pending_only = not self.show_completed_var.get()
        followups = self.db.get_follow_ups(customer_id, pending_only)
        
        self.followups_tree.delete(*self.followups_tree.get_children())
        for followup in followups:
            status = "تکمیل شده" if followup['completed'] else "در انتظار"
            # Color code overdue items
            tags = []
            if not followup['completed'] and followup['follow_up_date'] < date.today().isoformat():
                tags = ['overdue']
            
            self.followups_tree.insert('', 'end', values=(
                followup['id'],
                followup['customer_name'],
                followup['follow_up_date'],
                followup['title'],
                status
            ), tags=tags)
        
        # Configure overdue tag
        self.followups_tree.tag_configure('overdue', background='#ffcccc')
    
    def add_followup(self):
        """Add new follow-up"""
        customers = self.db.get_customers()
        if not customers:
            messagebox.showwarning("هشدار", "ابتدا باید حداقل یک مشتری اضافه کنید.")
            return
        
        selected_customer_id = self.get_selected_followup_customer_id()
        dialog = FollowUpDialog(self.root, customers, selected_customer_id=selected_customer_id)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            try:
                followup_id = self.db.add_follow_up(**dialog.result)
                messagebox.showinfo("موفقیت", f"پیگیری جدید با شناسه {followup_id} اضافه شد.")
                self.refresh_followups()
                self.refresh_dashboard()
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در افزودن پیگیری: {str(e)}")
    
    def complete_followup(self):
        """Complete selected follow-up"""
        selection = self.followups_tree.selection()
        if not selection:
            messagebox.showwarning("هشدار", "لطفاً یک پیگیری را انتخاب کنید.")
            return
        
        item = self.followups_tree.item(selection[0])
        followup_id = item['values'][0]
        followup_title = item['values'][3]
        
        # Confirm completion
        result = messagebox.askyesno("تأیید تکمیل", 
                                   f"آیا مطمئن هستید که پیگیری '{followup_title}' تکمیل شده است؟")
        
        if result:
            try:
                success = self.db.complete_follow_up(followup_id)
                if success:
                    messagebox.showinfo("موفقیت", "پیگیری تکمیل شد.")
                    self.refresh_followups()
                    self.refresh_dashboard()
                else:
                    messagebox.showerror("خطا", "خطا در تکمیل پیگیری.")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در تکمیل پیگیری: {str(e)}")
    
    def delete_followup(self):
        """Delete selected follow-up"""
        selection = self.followups_tree.selection()
        if not selection:
            messagebox.showwarning("هشدار", "لطفاً یک پیگیری را انتخاب کنید.")
            return
        
        item = self.followups_tree.item(selection[0])
        followup_id = item['values'][0]
        followup_title = item['values'][3]
        
        # Confirm deletion
        result = messagebox.askyesno("تأیید حذف", 
                                   f"آیا مطمئن هستید که می‌خواهید پیگیری '{followup_title}' را حذف کنید؟")
        
        if result:
            try:
                success = self.db.delete_follow_up(followup_id)
                if success:
                    messagebox.showinfo("موفقیت", "پیگیری حذف شد.")
                    self.refresh_followups()
                    self.refresh_dashboard()
                else:
                    messagebox.showerror("خطا", "خطا در حذف پیگیری.")
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در حذف پیگیری: {str(e)}")
    
    def complete_today_followup(self):
        """Complete selected follow-up from today's list"""
        selection = self.today_tree.selection()
        if not selection:
            messagebox.showwarning("هشدار", "لطفاً یک پیگیری را انتخاب کنید.")
            return
        
        item = self.today_tree.item(selection[0])
        followup_id = int(item['tags'][0])  # ID is stored in tags
        
        try:
            success = self.db.complete_follow_up(followup_id)
            if success:
                messagebox.showinfo("موفقیت", "پیگیری تکمیل شد.")
                self.refresh_dashboard()
                if self.notebook.index("current") == 3:  # If on follow-ups tab
                    self.refresh_followups()
            else:
                messagebox.showerror("خطا", "خطا در تکمیل پیگیری.")
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در تکمیل پیگیری: {str(e)}")
    
    # Alarm System
    def start_alarm_checker(self):
        """Start the alarm checking thread"""
        self.alarm_thread = threading.Thread(target=self.alarm_checker, daemon=True)
        self.alarm_thread.start()
    
    def alarm_checker(self):
        """Check for overdue and today's follow-ups periodically"""
        while True:
            try:
                # Check every 30 minutes
                time.sleep(1800)  # 30 minutes
                
                # Get overdue follow-ups
                overdue = self.db.get_overdue_follow_ups()
                today = self.db.get_today_follow_ups()
                
                if overdue or today:
                    # Schedule the alarm in the main thread
                    self.root.after(0, lambda: self.show_alarm(overdue, today))
                    
            except Exception as e:
                print(f"Alarm checker error: {e}")
    
    def show_alarm(self, overdue_followups, today_followups):
        """Show alarm for follow-ups"""
        try:
            # Play system sound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            
            # Create alarm message
            message = "یادآوری پیگیری‌ها:\n\n"
            
            if overdue_followups:
                message += f"پیگیری‌های عقب‌افتاده: {len(overdue_followups)}\n"
                for fu in overdue_followups[:3]:  # Show first 3
                    message += f"• {fu['customer_name']}: {fu['title']}\n"
                if len(overdue_followups) > 3:
                    message += f"و {len(overdue_followups) - 3} مورد دیگر...\n"
                message += "\n"
            
            if today_followups:
                message += f"پیگیری‌های امروز: {len(today_followups)}\n"
                for fu in today_followups[:3]:  # Show first 3
                    message += f"• {fu['customer_name']}: {fu['title']}\n"
                if len(today_followups) > 3:
                    message += f"و {len(today_followups) - 3} مورد دیگر...\n"
            
            # Show alarm dialog
            result = messagebox.showinfo("یادآوری پیگیری‌ها", message)
            
            # Refresh dashboard to update counts
            self.refresh_dashboard()
            
        except Exception as e:
            print(f"Alarm display error: {e}")
    
    def manual_alarm_check(self):
        """Manually check for alarms (for testing)"""
        overdue = self.db.get_overdue_follow_ups()
        today = self.db.get_today_follow_ups()
        
        if overdue or today:
            self.show_alarm(overdue, today)
        else:
            messagebox.showinfo("یادآوری", "هیچ پیگیری فوری‌ای وجود ندارد.")