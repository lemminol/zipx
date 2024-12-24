import os
import subprocess
import zipfile
from tkinter import Tk, filedialog, messagebox
from tqdm import tqdm
import time
import logging
import psutil
import hashlib

# 로그 설정
logging.basicConfig(filename='compression.log', level=logging.INFO, format='%(asctime)s %(message)s')

def estimate_remaining_time(elapsed_time, files_processed, remaining_files, cpu_usage):
    # CPU 사용률을 고려한 가중치 부여
    weight = 1 / (1 + cpu_usage)
    estimated_time_per_file = elapsed_time / files_processed * weight
    return estimated_time_per_file * remaining_files

def verify_compression(output_file, video_files, source_folder):
    with zipfile.ZipFile(output_file, 'r') as zipf:
        for file in zipf.namelist():
            # 압축 파일 내 파일 이름과 원본 파일 이름 비교
            if file not in video_files:
                return False

            # 압축 파일과 원본 파일의 해시 값 비교 (추가적인 검증)
            with zipf.open(file) as zipinfo, open(os.path.join(source_folder, file), 'rb') as original_file:
                zip_hash = hashlib.sha256(zipinfo.read()).hexdigest()
                original_hash = hashlib.sha256(original_file.read()).hexdigest()
                if zip_hash != original_hash:
                    return False
    return True

def zip_videos():
    root = Tk()
    root.withdraw()

    # 압축할 파일이 있는 폴더 선택
    source_folder = filedialog.askdirectory(title="압축할 폴더 선택")
    if not source_folder:
        messagebox.showerror("오류", "폴더를 선택하지 않았습니다.")
        return
    

    # 생성할 ZIPX 파일 이름 입력
    output_file = filedialog.asksaveasfilename(defaultextension=".zipx", filetypes=[("ZIPX 파일", "*.zipx")])
    if not output_file:
        messagebox.showerror("오류", "파일 이름을 입력하지 않았습니다.")
        return

    # 압축 파일을 저장할 폴더 생성
    zip_folder = os.path.dirname(output_file)
    os.makedirs(zip_folder, exist_ok=True)

    # 동영상 파일 목록 가져오기 및 압축
    video_files = [f for f in os.listdir(source_folder) if f.endswith(('.mp4', '.avi', '.mov'))]

    if len(video_files) >= 30:
        try:
            logging.info("압축 시작")
            start_time = time.time()
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                with tqdm(total=len(video_files), desc="압축 진행 중...", unit="파일", ncols=80, dynamic_ncols=True) as pbar:
                    for i, file in enumerate(video_files):
                        zipf.write(os.path.join(source_folder, file), compress_type=zipfile.ZIP_DEFLATED)
                        pbar.update(1)

                        # 매 파일 처리 시마다 예상 시간 계산
                        current_time = time.time()
                        elapsed_time = current_time - start_time
                        files_processed = i + 1
                        remaining_files = len(video_files) - files_processed
                        cpu_percent = psutil.cpu_percent()
                        estimated_remaining_time = estimate_remaining_time(elapsed_time, files_processed, remaining_files, cpu_percent)
                        pbar.set_description(f"압축 진행 중... 예상 남은 시간: {estimated_remaining_time:.2f}초")

            # 7-Zip을 이용하여 ZIPX로 변환
            result = subprocess.run(["7z", "a", "-tzipx", "-mx9", output_file + ".zipx", output_file], capture_output=True)
            if result.returncode != 0:
                logging.error(f"7-Zip 오류: {result.stderr.decode()}")
                messagebox.showerror("오류", "7-Zip을 이용한 변환 중 오류가 발생했습니다.")
            os.remove(output_file)

            # 압축된 파일을 ZIP 폴더로 이동
            new_file = os.path.join(zip_folder, os.path.basename(output_file))
            os.rename(output_file + ".zipx", new_file)

            messagebox.showinfo("완료", "압축이 완료되었으며, 파일이 지정된 폴더로 이동되었습니다.")
        except KeyboardInterrupt:
            logging.warning("압축이 취소되었습니다.")
    else:
        messagebox.showerror("오류", "동영상 파일이 30개 미만입니다.")

    # 압축 결과 검증
    if verify_compression(output_file + ".zipx", video_files, source_folder):
        messagebox.showinfo("완료", "압축이 성공적으로 완료되었습니다.")
    else:
        messagebox.showerror("오류", "압축 과정에서 오류가 발생했습니다.")

if __name__ == "__main__":
    zip_videos()