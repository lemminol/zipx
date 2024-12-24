import os
import zipfile
from tkinter import Tk, filedialog, messagebox, simpledialog
from tqdm import tqdm
import logging

# 로그 설정
logging.basicConfig(filename='compression.log', level=logging.INFO, format='%(asctime)s %(message)s')

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

    # 압축 형식 선택
    compression_type = simpledialog.askstring("압축 형식 선택", "압축 형식을 선택하세요 (zip, gzip):", initialvalue="zip")
    if not compression_type:
        messagebox.showerror("오류", "압축 형식을 선택하지 않았습니다.")
        return

    try:
        # 압축
        total_files = sum(len(files) for root, dirs, files in os.walk(source_folder))
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED if compression_type == 'zip' else zipfile.ZIP_STORED) as zipf:
            with tqdm(total=total_files, desc="압축 진행 중...", unit="파일", ncols=80, dynamic_ncols=True) as pbar:
                for root, _, files in os.walk(source_folder):
                    for file in files:
                        zipf.write(os.path.join(root, file), compress_type=zipfile.ZIP_DEFLATED)
                        pbar.update(1)

        messagebox.showinfo("완료", f"압축이 완료되었습니다. 파일이 {output_file}에 저장되었습니다.")
    except Exception as e:
        messagebox.showerror("오류", f"압축 중 오류 발생: {str(e)}")
        logging.error(f"압축 오류: {str(e)}")

if __name__ == "__main__":
    zip_videos()