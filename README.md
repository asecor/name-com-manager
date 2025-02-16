# Domain Manager

A Flask-based application generated by Claude.ai for managing name.com DNS records and monitoring SSL certificates.

## Features
- Add, update, and delete DNS records.
- Check SSL certificates for multiple domains.
- Persistent SSL check results across browser refreshes.

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/asecor/name-com-manager.git

2. Build and run the container
    sudo docker build -t domain-manager . && sudo docker run -p 5000:5000 --env-file .env --name domain-manager domain-manager

3. Add your name.com API info to .env
    nano .env #for the api token etc.
```
    API_TOKEN=
    API_USERNAME=
    DOMAIN_NAME=
```
4. Run container 
docker run -d -p 3575:5000 --env-file .env --restart unless-stopped domain-manager

#### Misc
```
export the container
sudo docker save domain-manager > domain-manager.tar

restore/import container 
docker load < domain-manager.tar

stop and delete the container
sudo docker stop domain-manager && sudo docker rm -f $(sudo docker ps -a -q) && sudo docker rmi domain-manager
```
## Structure
```
domain-manager/
│
├── app.py                   # Flask backend (main application file)
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (API_TOKEN, API_USERNAME, etc.)
├── .gitignore               # Files/folders to ignore in version control
│
├── static/                  # Static files (CSS, JS, images, etc.)
│   └── styles.css           # Custom CSS (if needed)
│
├── templates/               # HTML templates
│   └── index.html           # Main frontend template
│
└── README.md                # Project documentation
```