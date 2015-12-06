需要搭配 ptt-crawler 先抓取資料

1. pip3 install -r requirement

2. sudo apt-get install postgresql postgresql-contrib

3. 先進行前處理 `python3 utils/preprocess.py`

4. 建立 ptt-crawler 的 data 資料夾的軟連結 `ln -s path/data .`

5. python3 app.py

