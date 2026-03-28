import customtkinter as ctk
import torch
from transformers import pipeline
import sqlite3
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import psutil
import threading
import time
import os
import warnings
import re
warnings.filterwarnings('ignore')

# ==========================================
# 1. THE BRAIN: AI DECISION ENGINE
# ==========================================
class ClathSQL_Brain:
    def __init__(self, update_ui_callback):
        self.update_ui = update_ui_callback
        self.device = 0 if torch.cuda.is_available() else -1
        
        self.update_ui("Booting ClathSQL Brain...", "yellow")
        # Using a fast, local model
        model_id = "TinyLlama/TinyLlama-1.1B-Chat-v1.0" 
        
        try:
            self.agent = pipeline(
                "text-generation", 
                model=model_id, 
                device=self.device,
                torch_dtype=torch.float16 if self.device == 0 else torch.float32,
                max_new_tokens=5
            )
            self.model_warmed_up = False
            self.update_ui("Brain Online. Ready to Clutch.", "green")
        except Exception as e:
            self.update_ui(f"Brain Error: {e}", "red")
            self.agent = None

    def warmup_model(self):
        """Pre-warm model weights to reduce first inference latency"""
        if not self.model_warmed_up and self.agent:
            try:
                self.update_ui("Warming up neural pathways...", "yellow")
                _ = self.clutch_logic("WARMUP_SEQUENCE_123")
                self.model_warmed_up = True
                self.update_ui("Neural Pathways Optimized. Full Speed Ahead.", "green")            except Exception as e:
                self.update_ui(f"Warmup Failed: {e}, Operating in fallback mode", "orange")

    def clutch_logic(self, raw_input):
        """Minimalist Agent Prompting for 'Song-like' rhythm"""
        
        # === HYBRID ROUTING LOGIC (Bypass AI when possible) ===
        if self._is_obvious_nosql(raw_input):
            return "NOSQL"
        elif self._is_obvious_sql(raw_input):
            return "SQL"
        elif self._has_numerical_sequences(raw_input):
            return "PLOT"
        
        # === AI DECISION FALLBACK ===
        prompt = f"<|system|>\nYou are ClathSQL. Route data to SQL, NOSQL, or PLOT. Answer with 1 word only.</s>\n<|user|>\nData: {raw_input[:200]}</s>\n<|assistant|>\n"
        
        try:
            if self.agent is None:
                raise Exception("AI Agent not initialized")
                
            result = self.agent(prompt, max_new_tokens=5, temperature=0.1)[0]['generated_text']
            output = result.split("<|assistant|>")[-1].strip().upper()
            
            if "PLOT" in output:
                return "PLOT"
            elif "SQL" in output and "NOSQL" not in output:
                return "SQL"
            else:
                return "NOSQL"
        except Exception as e:
            # Fallback based on structure if model is busy
            self.update_ui(f"AI Routing Fallback Active: {type(e).__name__}", "orange")
            return "NOSQL" if "{" in raw_input else "SQL"

    def _is_obvious_nosql(self, text):
        """Detect JSON-like structures without AI"""
        patterns = [
            r'^\s*\{',
            r'"key"\s*:',
            r'\[.*\]',
            r'document|documentdb|nosql',
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)

    def _is_obvious_sql(self, text):
        """Detect SQL keywords"""
        patterns = [
            r'\bSELECT\b',
            r'\bINSERT\b',            r'\bUPDATE\b',
            r'\bDELETE\b',
            r'\bFROM\b',
            r'\bWHERE\b',
            r'\bTABLE\b',
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)

    def _has_numerical_sequences(self, text):
        """Detect numerical data suitable for plotting"""
        numbers = [x.strip() for x in text.split('\n') if re.match(r'^[\d.]+$', x.strip())]
        return len(numbers) >= 2

# ==========================================
# 2. THE VAULT: STORAGE ENGINE
# ==========================================
class ClathSQL_Vault:
    def __init__(self):
        self.sql_db = "hjk_clath_vault.db"
        self.nosql_db = "hjk_clath_docs.json"
        self.init_databases()

    def init_databases(self):
        """Initialize databases and create necessary indexes"""
        with sqlite3.connect(self.sql_db) as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS clath_stream (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, content TEXT)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON clath_stream(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_content ON clath_stream(content)")
            conn.commit()

    def store_sql(self, data):
        """Thread-safe SQLite storage with error handling"""
        try:
            with sqlite3.connect(self.sql_db) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO clath_stream (content) VALUES (?)", (data,))
                conn.commit()
            return True
        except Exception as e:
            print(f"SQL Storage Error: {e}")
            return False

    def store_nosql(self, data):
        """Safe append-only JSON document storage"""
        try:
            doc = {"timestamp": time.time(), "data": data}
            
            # Lock mechanism for concurrent writes
            lock_file = self.nosql_db + ".lock"            os.makedirs(os.path.dirname(self.nosql_db) if os.path.dirname(self.nosql_db) else '.', exist_ok=True)
            
            with open(lock_file, 'w') as lf:
                lf.write(str(os.getpid()))
                
            with open(self.nosql_db, "a") as f:
                f.write(json.dumps(doc) + "\n")
            
            os.remove(lock_file)
            return True
        except Exception as e:
            print(f"NoSQL Storage Error: {e}")
            if os.path.exists(lock_file):
                os.remove(lock_file)
            return False

    def get_stats(self):
        """Retrieve vault statistics"""
        sql_count = 0
        nosql_count = 0
        
        try:
            with sqlite3.connect(self.sql_db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM clath_stream")
                sql_count = cursor.fetchone()[0]
        except:
            pass
        
        try:
            if os.path.exists(self.nosql_db):
                with open(self.nosql_db, 'r') as f:
                    nosql_count = sum(1 for _ in f)
        except:
            pass
            
        return {"sql_entries": sql_count, "nosql_entries": nosql_count}

# ==========================================
# 3. THE GUI: ENTERPRISE DASHBOARD
# ==========================================
class ClathSQL_App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("HJK-INC: ClathSQL Pro Ultimate v2")
        self.geometry("1400x900")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.vault = ClathSQL_Vault()        self.brain = None
        self.canvas_widget = None
        self.shutdown_event = threading.Event()

        self.setup_ui()
        self.start_system_monitor()
        
        # Load AI in background to prevent UI freeze
        threading.Thread(target=self.init_brain, daemon=True).start()
        
        # Register close handler
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#1a1a1a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="ClathSQL", font=("Arial", 28, "bold"), text_color="#00a8ff").pack(pady=(30, 5))
        ctk.CTkLabel(self.sidebar, text="HJK-INC Core", font=("Arial", 12)).pack(pady=(0, 30))

        self.cpu_label = ctk.CTkLabel(self.sidebar, text="CPU: 0%", font=("Arial", 14))
        self.cpu_label.pack(pady=10)
        self.ram_label = ctk.CTkLabel(self.sidebar, text="RAM: 0%", font=("Arial", 14))
        self.ram_label.pack(pady=10)
        
        # Vault Statistics
        self.vault_frame = ctk.CTkFrame(self.sidebar, fg_color="#2b2b2b", corner_radius=8)
        self.vault_frame.pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(self.vault_frame, text="📊 Vault Stats", font=("Arial", 12, "bold"), text_color="#00a8ff").pack(pady=5)
        self.sql_stat_label = ctk.CTkLabel(self.vault_frame, text="SQL Entries: 0", font=("Arial", 11), text_color="gray")
        self.sql_stat_label.pack(pady=2)
        self.nosql_stat_label = ctk.CTkLabel(self.vault_frame, text="NoSQL Docs: 0", font=("Arial", 11), text_color="gray")
        self.nosql_stat_label.pack(pady=2)

        self.status_indicator = ctk.CTkLabel(self.sidebar, text="● Initializing...", text_color="yellow", font=("Arial", 14, "bold"))
        self.status_indicator.pack(pady=40)

        # --- Main Workspace ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(anchor="w", fill="x")
        ctk.CTkLabel(header_frame, text="Data Ingestion Lattice", font=("Arial", 18, "bold")).pack(side="left")        
        stats_btn = ctk.CTkButton(header_frame, text="⟳ Refresh Stats", command=self.refresh_stats, width=120, height=28)
        stats_btn.pack(side="right", padx=10)
        export_btn = ctk.CTkButton(header_frame, text="📤 Export", command=self.export_data, width=120, height=28)
        export_btn.pack(side="right")

        self.input_box = ctk.CTkTextbox(self.main_frame, height=150, font=("Consolas", 14))
        self.input_box.pack(fill="x", pady=10)
        self.input_box.insert("0.0", "Paste unstructured data, JSON, or numerical sequences here...")

        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        self.clutch_btn = ctk.CTkButton(
            self.main_frame, 
            text="⚡ CLUTCH DATA (AI ROUTE)", 
            command=self.trigger_clutch,
            font=("Arial", 16, "bold"),
            height=45,
            fg_color="#0066cc",
            hover_color="#004c99"
        )
        self.clutch_btn.pack(pady=10)

        clear_btn = ctk.CTkButton(
            self.main_frame,
            text="🗑️ Clear Input",
            command=self.clear_input,
            width=150,
            height=35,
            fg_color="#333333",
            hover_color="#444444"
        )
        clear_btn.pack()

        # --- Visualization Frame ---
        self.viz_frame = ctk.CTkFrame(self.main_frame, corner_radius=10, fg_color="#2b2b2b")
        self.viz_frame.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(self.viz_frame, text="Autonomous Visualization Engine", text_color="gray").pack(pady=10)

        # --- Status Log ---
        self.log_frame = ctk.CTkFrame(self, fg_color="#1a1a1a")
        self.log_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.log_frame.pack_propagate(False)
        self.log_frame.configure(height=100)
        
        self.log_box = ctk.CTkTextbox(self.log_frame, height=75, fg_color="#2b2b2b", text_color="gray")
        self.log_box.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_box.configure(state="disabled")
    def log_message(self, message):
        """Append message to status log"""
        self.after(0, lambda: self.add_to_log(message))

    def add_to_log(self, message):
        """Thread-safe log update"""
        try:
            current = self.log_box.get("1.0", "end-1c").strip()
            timestamp = time.strftime("%H:%M:%S")
            new_line = f"[{timestamp}] {message}"
            content = f"{current}\n{new_line}" if current else new_line
            self.log_box.configure(state="normal")
            self.log_box.delete("1.0", "end")
            self.log_box.insert("1.0", content)
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        except Exception as e:
            print(f"Log Error: {e}")

    def refresh_stats(self):
        """Refresh vault statistics display"""
        stats = self.vault.get_stats()
        self.sql_stat_label.configure(text=f"SQL Entries: {stats['sql_entries']}")
        self.nosql_stat_label.configure(text=f"NoSQL Docs: {stats['nosql_entries']}")
        self.log_message("Vault statistics refreshed")

    def export_data(self):
        """Export vault contents to CSV"""
        try:
            stats = self.vault.get_stats()
            if stats['sql_entries'] == 0 and stats['nosql_entries'] == 0:
                self.update_status("No data to export", "yellow")
                return
            
            df_list = []
            
            # Export SQL data
            if stats['sql_entries'] > 0:
                query = "SELECT * FROM clath_stream ORDER BY id DESC LIMIT 100"
                df_sql = pd.read_sql_query(query, sqlite3.connect(self.vault.sql_db))
                df_sql['source'] = 'SQL'
                df_list.append(df_sql)
            
            # Export NoSQL data
            if stats['nosql_entries'] > 0:
                with open(self.vault.nosql_db, 'r') as f:
                    records = [json.loads(line) for line in f.readlines()]
                df_nosql = pd.DataFrame(records)
                df_nosql['source'] = 'NoSQL'                df_list.append(df_nosql)
            
            if df_list:
                df_combined = pd.concat(df_list, ignore_index=True)
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                output_file = f"hjk_clath_export_{timestamp}.csv"
                df_combined.to_csv(output_file, index=False)
                self.update_status(f"Exported to {output_file}", "green")
                self.log_message(f"Exported data to {output_file}")
            
        except Exception as e:
            self.update_status(f"Export failed: {e}", "red")
            self.log_message(f"Export error: {e}")

    def clear_input(self):
        """Clear input box"""
        self.input_box.delete("1.0", "end")
        self.log_message("Input cleared")

    def update_status(self, text, color):
        self.status_indicator.configure(text=f"● {text}", text_color=color)
        self.log_message(text)

    def init_brain(self):
        """Initialize AI brain with warmup sequence"""
        self.brain = ClathSQL_Brain(self.update_status)
        time.sleep(2)  # Allow UI to settle
        self.brain.warmup_model()

    def start_system_monitor(self):
        def monitor():
            while not self.shutdown_event.is_set():
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory().percent
                
                self.after(0, lambda c=cpu: self.cpu_label.configure(text=f"CPU POWER: {c}%"))
                self.after(0, lambda r=ram: self.ram_label.configure(text=f"RAM USAGE: {r}%"))
                
                # Auto-refresh stats every 30 seconds
                if hasattr(self, '_stats_counter'):
                    self._stats_counter += 1
                    if self._stats_counter >= 30:
                        self.refresh_stats()
                        self._stats_counter = 0
                else:
                    self._stats_counter = 0
                    
                time.sleep(1)
        
        thread = threading.Thread(target=monitor, daemon=True)        thread.start()

    def trigger_clutch(self):
        if not self.brain:
            self.update_status("Brain still loading...", "red")
            return
            
        data = self.input_box.get("1.0", "end-1c").strip()
        if not data or data == "Paste unstructured data, JSON, or numerical sequences here...":
            self.update_status("Please enter data to process", "yellow")
            return

        self.clutch_btn.configure(state="disabled")
        self.update_status("Sensing Data...", "yellow")
        
        # Run in background
        threading.Thread(target=self.process_data, args=(data,), daemon=True).start()

    def process_data(self, data):
        try:
            # 1. AI Agent Decides
            decision = self.brain.clutch_logic(data)
            
            # 2. Action Execution
            if decision == "SQL":
                success = self.vault.store_sql(data)
                if success:
                    self.update_status("Trapped in SQL Lattice", "#00ff00")
                else:
                    self.update_status("SQL Storage Failed", "red")
                    
            elif decision == "NOSQL":
                success = self.vault.store_nosql(data)
                if success:
                    self.update_status("Trapped in NoSQL Document", "#ff9900")
                else:
                    self.update_status("NoSQL Storage Failed", "red")
                    
            elif decision == "PLOT":
                self.update_status("Empowering Plot...", "#00ffff")
                self.after(0, self.plot_data, data)
                
            # Update statistics after processing
            self.after(1000, self.refresh_stats)
            
            # Reset UI
            self.after(1000, lambda: self.clutch_btn.configure(state="normal"))
            
        except Exception as e:
            self.update_status(f"Processing Error: {e}", "red")            self.after(0, lambda: self.clutch_btn.configure(state="normal"))

    def plot_data(self, data):
        """Dynamic plotting inside the ClathSQL GUI"""
        try:
            # Clear previous plot
            if self.canvas_widget:
                self.canvas_widget.destroy()
                self.canvas_widget = None

            # Parse basic numerical data
            lines = data.split('\n')
            numbers = []
            for line in lines:
                stripped = line.strip()
                if stripped and re.match(r'^[\d.-]+$', stripped):
                    try:
                        numbers.append(float(stripped))
                    except ValueError:
                        pass
            
            # Safety check: Need minimum 2 points for valid plot
            if len(numbers) < 2:
                self.update_status("Insufficient numeric data for plotting (min 2 values required)", "red")
                return 

            fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
            
            # Plot with professional styling
            x_vals = list(range(len(numbers)))
            ax.plot(x_vals, numbers, color='#00a8ff', linewidth=2, marker='o', markersize=6, markerfacecolor='white', zorder=3)
            
            # Match dark theme
            fig.patch.set_facecolor('#2b2b2b')
            ax.set_facecolor('#2b2b2b')
            ax.tick_params(colors='white')
            for spine in ax.spines.values():
                spine.set_color('#555555')
                
            ax.set_title("Autonomous Clathrate Data Trend", color='white', pad=15, fontsize=12)
            ax.set_xlabel("Sequence Index", color='gray')
            ax.set_ylabel("Value", color='gray')
            ax.grid(True, color='#444444', linestyle='--', alpha=0.5)
            
            # Add trend analysis
            if len(numbers) >= 2:
                mean_val = sum(numbers) / len(numbers)
                median_val = sorted(numbers)[len(numbers)//2]
                annotation = f'Mean: {mean_val:.2f}\nMedian: {median_val:.2f}'
                ax.text(0.05, 0.95, annotation, transform=ax.transAxes, fontsize=9,                        color='gray', bbox=dict(boxstyle='round', facecolor='#444444', alpha=0.7))

            # Embed in CustomTkinter
            canvas = FigureCanvasTkAgg(fig, master=self.viz_frame)
            canvas.draw()
            self.canvas_widget = canvas.get_tk_widget()
            self.canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)
            
            self.update_status("Plot Complete", "#00ffff")
            
        except Exception as e:
            self.update_status(f"Plot Error: {e}", "red")
            self.log_message(f"Plotting failed: {str(e)}")

    def on_close(self):
        """Graceful shutdown"""
        self.shutdown_event.set()
        
        # Clean up resources
        if self.canvas_widget:
            try:
                self.canvas_widget.destroy()
            except:
                pass
        
        self.log_message("System shutting down...")
        self.update_status("Shutting Down...", "yellow")
        
        # Give time for final logs
        time.sleep(0.5)
        
        self.destroy()
        return True

# ==========================================
# 4. SYSTEM EXECUTION
# ==========================================
if __name__ == "__main__":
    app = ClathSQL_App()
    app.mainloop()
