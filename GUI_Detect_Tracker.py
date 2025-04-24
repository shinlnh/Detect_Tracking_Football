import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import threading
import time
from yolov5.detect_track import run_tracking_from_gui
import os
from pathlib import Path

class FootballTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Football Player Object Tracker")
        self.root.geometry("1000x750")
        self.root.configure(bg="#ffe6f0")  # Light pink background

        self.video_path = ""
        self.cap = None
        self.is_playing = False

        self.build_gui()

    def build_gui(self):
        header = tk.Label(self.root, text="Football Player Object Tracking",
                          font=("Helvetica", 20, "bold"), bg="#ffe6f0", fg="green")
        header.pack(pady=10)

        # Canvas để hiển thị video
        video_frame = tk.Frame(self.root, bg="#ffe6f0")
        video_frame.pack(pady=10)
        self.canvas = tk.Canvas(video_frame, width=800, height=450, bg="black")
        self.canvas.pack()

        # Các nút điều khiển
        control_frame = tk.Frame(self.root, bg="#ffe6f0")
        control_frame.pack(pady=10)
        tk.Button(control_frame, text="Browse Video", command=self.load_video,
                  bg="#4da6ff", fg="white").grid(row=0, column=0, padx=10)
        tk.Button(control_frame, text="Play", command=self.play_video,
                  bg="#5cd65c", fg="white").grid(row=0, column=1, padx=10)
        tk.Button(control_frame, text="Pause", command=self.pause_video,
                  bg="#ff9933", fg="white").grid(row=0, column=2, padx=10)
        tk.Button(control_frame, text="Stop", command=self.stop_video,
                  bg="#ff6666", fg="white").grid(row=0, column=3, padx=10)

        # Thanh tải video
        self.loading_label = tk.Label(self.root, text="Loading Video",
                                      bg="#ffe6f0", font=("Arial", 10, "bold"))
        self.loading_label.pack()
        self.load_progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL,
                                             length=400, mode='determinate')
        self.load_progress.pack(pady=5)

        # Thanh tiến trình detect + tracking
        self.detect_label = tk.Label(self.root, text="Detecting And Tracking Video",
                                     bg="#ffe6f0", font=("Arial", 10, "bold"))
        self.detect_label.pack()
        self.detect_progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL,
                                               length=400, mode='determinate')
        self.detect_progress.pack(pady=(0, 5))

        # ✅ Label hiển thị frame hiện tại / tổng frame
        self.frame_label = tk.Label(self.root, text="Frame: 0/0",
                                    bg="#ffe6f0", font=("Arial", 10, "italic"))
        self.frame_label.pack(pady=(0, 10))

        # Tuỳ chọn hiển thị bounding box / ID
        option_frame = tk.Frame(self.root, bg="#ffe6f0")
        option_frame.pack(pady=10)
        self.show_boxes_var = tk.BooleanVar(value=True)
        self.show_ids_var = tk.BooleanVar(value=True)
        tk.Checkbutton(option_frame, text="Show Bounding Boxes", variable=self.show_boxes_var,
                       bg="#ffe6f0").pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(option_frame, text="Show Player IDs", variable=self.show_ids_var,
                       bg="#ffe6f0").pack(side=tk.LEFT, padx=10)

        # Nút lưu video
        tk.Button(self.root, text="Save Result", command=self.save_result,
                  bg="#4da6ff", fg="white").pack(pady=10)
    def load_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
        if self.video_path:
            self.load_progress["value"] = 0
            self.root.update_idletasks()
            for i in range(0, 101, 10):
                self.load_progress["value"] = i
                self.root.update_idletasks()
                time.sleep(0.03)

            self.cap = cv2.VideoCapture(self.video_path)

            # 👇 Thêm đoạn này để hiện khung hình đầu tiên
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.resize(frame, (800, 450))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
                self.canvas.image = imgtk

            messagebox.showinfo("Success", "Video loaded successfully!")

    def play_video(self):
        if not self.video_path:
            messagebox.showwarning("Warning", "Please load a video first!")
            return

        self.is_playing = False
        self.detect_progress["value"] = 0
        self.root.update_idletasks()

        def tracking_task():
            for i in range(0, 50, 5):
                self.detect_progress["value"] = i
                self.root.update_idletasks()
                time.sleep(0.03)

            run_tracking_from_gui(self.video_path, self.update_progress)

            for i in range(50, 101, 5):
                self.detect_progress["value"] = i
                self.root.update_idletasks()
                time.sleep(0.03)

            result_path = os.path.join("output", "gui_output", Path(self.video_path).stem, Path(self.video_path).name)
            if not os.path.exists(result_path):
                messagebox.showerror("Error", "Tracking output not found!")
                return

            self.cap = cv2.VideoCapture(result_path)
            self.is_playing = True
            threading.Thread(target=self.video_loop).start()

        threading.Thread(target=tracking_task).start()

    def pause_video(self):
        self.is_playing = False

    def stop_video(self):
        self.is_playing = False
        if self.cap:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def video_loop(self):
        while self.cap.isOpened() and self.is_playing:
            ret, frame = self.cap.read()
            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame = cv2.resize(frame, (800, 450))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            self.canvas.image = imgtk

            self.root.update_idletasks()
            self.root.update()

        self.is_playing = False

    def save_result(self):
        if not self.video_path:
            messagebox.showwarning("Warning", "No video to save!")
            return

        result_name = Path(self.video_path).stem
        result_path = Path("output/gui_output") / result_name / f"{result_name}.mp4"

        print(f"[DEBUG] Expecting result at: {result_path}")  # Debug

        if not result_path.exists():
            messagebox.showerror("Error", f"Trackng output not found at:\n{result_path}")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".mp4",
                                                 filetypes=[("MP4 files", "*.mp4")],
                                                 initialfile=Path(self.video_path).stem + "_tracked.mp4")
        if save_path:
            try:
                import shutil
                shutil.copy(result_path, save_path)
                messagebox.showinfo("Success", f"Result saved to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")

    def update_progress(self, percent, frame=None, total=None):
        self.detect_progress["value"] = percent
        if frame is not None and total is not None:
            self.frame_label.config(text=f"Frame: {frame}/{total}")
        self.root.update_idletasks()
if __name__ == "__main__":
    root = tk.Tk()
    app = FootballTrackerApp(root)
    root.mainloop()
