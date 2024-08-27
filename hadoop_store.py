from hdfs import InsecureClient
import pyarrow.parquet as pq
import pyarrow as pa
from io import BytesIO
import pandas as pd
import os
import glob

# CSV 파일이 저장된 디렉토리 경로 지정
directory_path = r'C:\Users\USER\YU\YU_python\test_data'

# 디렉토리 경로에서 모든 CSV 파일을 불러옴
all_file_list = glob.glob(os.path.join(directory_path, '*.csv'))

# HDFS 클라이언트 초기화
client_hdfs = InsecureClient('http://10.10.20.134:9870', user='itcous')

for file_path in all_file_list:
    # 파일명 추출
    filename = os.path.basename(file_path)
    filename_without_ext = os.path.splitext(filename)[0]  # 확장자 제거

    # DataFrame을 읽어서 Parquet 형식으로 변환
    df = pd.read_csv(file_path, sep=",", encoding='utf-8')
    table = pa.Table.from_pandas(df)
    
    # BytesIO 객체에 Parquet 데이터 저장
    buffer = BytesIO()
    pq.write_table(table, buffer, compression='snappy') # 
    buffer.seek(0)

    # snappy 검증
    output_dir = r'./test'
    df.to_parquet(os.path.join(output_dir, f'{filename_without_ext}_1.snappy.parquet'), compression='snappy')
    
    # HDFS에 저장
    hdfs_path = f'/test/{filename_without_ext}.snappy.parquet'
    with client_hdfs.write(hdfs_path, overwrite=True) as writer:
        writer.write(buffer.getvalue())