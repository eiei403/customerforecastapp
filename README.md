0.download ODBC version 17
https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

1.แก้ ในไฟล์ config.py 
Authentication : SQL Server Authentication
conn_str = create_engine(
        "mssql+pyodbc://username:password@IP:Port/Database"
        "?driver=ODBC+Driver+17+for+SQL+Server"
    )

2.ติดตั้งไลบรารี
  pip install -r requirements.txt
  
3.รัน Streamlit App
  streamlit run app.py
  
