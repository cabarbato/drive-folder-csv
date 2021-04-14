## 📁 Drive Contents CSV Maker 

This script uses the Google API to create a csv listing all files within a Drive folder. Each row contains the file id, name and url.

---

### Usage:
1. Create an .env file with your Google Sheets info and destination website url (optional).
2. If using Docker, run `docker-compose up`, then run `docker-compose run drivefoldercsv python script.py url`. Otherwise, run `pip install -r requirements.txt` prior to the script to get all the required dependencies, and make sure you have the chromedriver saved somewhere in your Path. You can either pass the folder url as an argument like with Docker, or you can input it when prompted.
3. After script is complete, you can copy all the files generated using a command like `docker cp container_name:/app/data/output data`. If you opted for using your system's version of Python, the output file will be saved as `./data/output/drive_contents_folder_id.csv`.

---

### This script utilizes:

* [Google Drive API v3](https://developers.google.com/drive/api/v3)