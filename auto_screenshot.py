import tkinter as tk
from tkinter import ttk
import mss
import numpy as np
from PIL import Image
import time
import os
from datetime import datetime

class AutoScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("自動スクショマン★")
        self.root.geometry("400x300")
        
        # スクリーンショット保存用のディレクトリ作成
        self.save_dir = "screenshots"
        os.makedirs(self.save_dir, exist_ok=True)
        
        # MSS初期化
        self.sct = mss.mss()
        
        # モニター選択用のコンボボックス
        self.monitor_var = tk.StringVar()
        self.setup_ui()
        
        self.is_capturing = False
        self.last_screenshot = None
        
    def setup_ui(self):
        # モニター選択
        monitors_frame = ttk.LabelFrame(self.root, text="モニター選択", padding=10)
        monitors_frame.pack(fill="x", padx=10, pady=5)
        
        monitors = self.get_monitor_list()
        monitor_combo = ttk.Combobox(
            monitors_frame, 
            textvariable=self.monitor_var,
            values=monitors,
            state="readonly"
        )
        monitor_combo.set(monitors[0] if monitors else "モニターが見つかりません")
        monitor_combo.pack(fill="x")
        
        # 開始/停止ボタン
        self.start_button = ttk.Button(
            self.root,
            text="開始",
            command=self.toggle_capture
        )
        self.start_button.pack(pady=20)
        
        # ステータス表示
        self.status_label = ttk.Label(
            self.root,
            text="待機中...",
            wraplength=350
        )
        self.status_label.pack(pady=10)
        
    def get_monitor_list(self):
        return [f"モニター {i+1}" for i in range(len(self.sct.monitors[1:]))]
        
    def toggle_capture(self):
        if not self.is_capturing:
            self.start_capture()
        else:
            self.stop_capture()
            
    def start_capture(self):
        self.is_capturing = True
        self.start_button.config(text="停止")
        self.status_label.config(text="キャプチャ中...")
        self.root.after(100, self.check_screen)
        
    def stop_capture(self):
        self.is_capturing = False
        self.start_button.config(text="開始")
        self.status_label.config(text="待機中...")
        
    def check_screen(self):
        if not self.is_capturing:
            return
            
        try:
            # 選択されたモニターのインデックスを取得
            monitor_idx = int(self.monitor_var.get().split()[1]) # "モニター X" から X を取得
            monitor = self.sct.monitors[monitor_idx]
            
            # スクリーンショットを撮影
            screenshot = self.sct.grab(monitor)
            current_screen = np.array(screenshot)
            
            # 前回のスクリーンショットと比較
            if self.last_screenshot is not None:
                # 画像に変化があるか確認
                if not np.array_equal(current_screen, self.last_screenshot):
                    self.save_screenshot(screenshot)
                    self.status_label.config(text=f"スクリーンショット保存: {time.strftime('%H:%M:%S')}")
            
            self.last_screenshot = current_screen
            
        except Exception as e:
            self.status_label.config(text=f"エラー: {str(e)}")
            
        self.root.after(100, self.check_screen)
        
    def save_screenshot(self, screenshot):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.save_dir, f"screenshot_{timestamp}.png")
            
            # より安全な方法でPIL Imageに変換
            # mssのスクリーンショットを直接PIL Imageに変換
            img = Image.frombytes('RGB', screenshot.size, screenshot.bgra, 'raw', 'BGRX')
            img.save(filename)
            
        except Exception as e:
            # 代替方法：numpy配列経由で保存
            try:
                img_array = np.array(screenshot)
                # BGRAからRGBに変換
                img_rgb = img_array[:, :, [2, 1, 0]]  # BGR -> RGB
                img = Image.fromarray(img_rgb)
                img.save(filename)
            except Exception as e2:
                self.status_label.config(text=f"画像保存エラー: {str(e2)}")
                return
                
        self.status_label.config(text=f"保存完了: {os.path.basename(filename)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoScreenshotApp(root)
    root.mainloop() 