For systemd and related

The systemd service file you've posted looks mostly correct, but there are a couple of inconsistencies that should be addressed to ensure it functions properly. Here's your service file with annotations on what might need adjustment:

```ini
[Unit]
Description=Gunicorn instance to serve app
After=network.target

[Service]
User=gohan
Group=www-data
WorkingDirectory=/home/yourhighnessjohannes_gmail_com/app
Environment="PATH=/home/yourhighnessjohannes_gmail_com/miniconda3/envs/gohan"
ExecStart=/home/user/myprojectenv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 app:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
```
### Updated Version:

Here's an updated version of your service file with assumed corrections:

```ini
[Unit]
Description=Gunicorn instance to serve app
After=network.target

[Service]
User=gohan
Group=www-data
WorkingDirectory=/home/yourhighnessjohannes_gmail_com/app
Environment="PATH=/home/yourhighnessjohannes_gmail_com/miniconda3/envs/gohan/bin"
ExecStart=/home/yourhighnessjohannes_gmail_com/miniconda3/envs/gohan/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 app:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Final Tips:
- **Check Paths**: Double-check all paths in the service file to ensure they accurately reflect your server's directory structure and where the software components are installed.
- **Test the Service**: After making these changes, you can test the service using:
  ```bash
  sudo systemctl start nameofservice.service
  ```
  Check the status using:
  ```bash
  sudo systemctl status nameofservice.service
  ```
  This will show you if there are any errors starting the service.
- **Logs for Debugging**: If the service fails to start, look at the logs for details:
  ```bash
  journalctl -u nameofservice.service
  ```
  This command will give you a detailed output of what went wrong.

Adjusting these paths and settings as necessary based on your server setup should help ensure that your service runs correctly.

4. Disabling the Service
If you don't plan on starting Gunicorn automatically in the future, you might also want to disable the service:

Disable the Service:
sudo systemctl disable gunicorn

---
## Add reverse proxy to run on 8000
Yes, if you intend to serve your website publicly and want users to access it via a standard web browser without specifying a port number in the URL, you should definitely configure your environment to use the standard web ports: **80 for HTTP** 

 **443 for HTTPS**. Here are the steps and considerations to properly set this up:

### 1. **Configure Gunicorn to Serve on Standard Ports**
If Gunicorn is currently set up to serve your application on port 8000, you can either change it to serve directly on ports 80 and 443 or use a reverse proxy setup (recommended). Serving directly on ports 80 and 443 usually requires running Gunicorn with superuser privileges because these are privileged ports (below 1024), which is not recommended for security reasons.

### 2. **Use a Reverse Proxy (Recommended Approach)**
A more secure and common approach is to use a reverse proxy like Nginx or Apache in front of Gunicorn. The proxy server listens on ports 80 and 443 and forwards the traffic to Gunicorn running on a non-privileged port like 8000. This setup enhances security, enables better handling of static files, and supports SSL/TLS termination.

Here’s a basic setup with Nginx:

- **Install Nginx:**
  ```bash
  sudo apt update
  sudo apt install nginx
  ```

- **Configure Nginx:**
  Create a new configuration file in `/etc/nginx/sites-available/` and link it to `sites-enabled`:
  ```bash
  sudo nano /etc/nginx/sites-available/subdomain.example.com
  ```
  Add the following configuration:
  ```nginx
  server {
      listen 80;
      server_name subdomain.example.com;

      location / {
          proxy_pass http://localhost:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
  }
  ```
  Enable the site by linking:
  ```bash
  sudo ln -s /etc/nginx/sites-available/subdomain.example.com /etc/nginx/sites-enabled/
  ```
  Test and reload Nginx:
  ```bash
  sudo nginx -t
  sudo systemctl reload nginx
  ```

### 3. **Setting Up HTTPS**
To set up HTTPS, obtain an SSL/TLS certificate. You can get a free certificate from Let’s Encrypt using Certbot:
- **Install Certbot:**
  ```bash
  sudo apt install certbot python3-certbot-nginx
  ```

- **Obtain and Configure SSL Certificate:**
  ```bash
  sudo certbot --nginx -d subdomain.example.com
  ```
  Follow the prompts, and Certbot will automatically update your Nginx configuration to use HTTPS and redirect HTTP traffic to HTTPS.

### 4. **Open Ports 80 and 443**
Ensure that ports 80 (HTTP) and 443 (HTTPS) are open in your firewall:
- If using `ufw` (Uncomplicated Firewall):
  ```bash
  sudo ufw allow 'Nginx Full'
  sudo ufw reload
  ```

### 5. **DNS Configuration**
Make sure your DNS records are correctly pointing your subdomain to the IP address of your VM where Nginx is set up.

### Conclusion
This setup not only secures your application but also adheres to best practices for deploying web applications. Users can access your site at `http://subdomain.example.com` and `https://subdomain.example.com` without having to specify a port number.
