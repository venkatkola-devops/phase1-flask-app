# 🐍 Two-Tier Flask App — CI/CD with Jenkins & Docker on AWS

> **Phase 1 of my DevOps Portfolio** | A production-style task manager app, containerised with Docker, automated with Jenkins CI/CD, and deployed on AWS EC2.

---

## 📌 What This Project Is

A simple **Task Manager web app** built with Python Flask and MySQL — but the *app itself* is not the point. The point is **how it's built, packaged, and deployed**.

Every time I push code to GitHub:
1. **Jenkins** automatically picks it up
2. Runs **tests**
3. Builds a **Docker image**
4. Pushes it to **Docker Hub**
5. SSHs into my **AWS EC2** server and deploys it live

Zero manual steps. That's CI/CD.

---

## 🏗️ Architecture

```
Developer (You)
      |
      | git push
      ↓
  [ GitHub Repo ]
      |
      | Webhook trigger
      ↓
  [ Jenkins Server ]  ←── runs on a separate EC2 instance
      |
      |── Stage 1: Checkout code
      |── Stage 2: Run tests (pytest)
      |── Stage 3: docker build → creates image
      |── Stage 4: docker push → uploads to Docker Hub
      |── Stage 5: SSH into app server → docker compose up
      ↓
  [ AWS EC2 — App Server ]
      |
      |── Container 1: Flask Web App  (port 5000)
      |── Container 2: MySQL Database (internal, not exposed)
      ↓
  [ User visits http://YOUR_EC2_IP:5000 ]
```

**Why Two-Tier?**
- **Tier 1 (Frontend + App logic):** Flask web server — handles HTTP requests, renders the UI
- **Tier 2 (Data layer):** MySQL database — stores the tasks persistently

---

## 🛠️ Tech Stack

| Tool | What it does in this project |
|------|------------------------------|
| ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) **Python / Flask** | The web application framework |
| ![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat&logo=mysql&logoColor=white) **MySQL 8** | Relational database — stores tasks |
| ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white) **Docker + Compose** | Packages the app into portable containers |
| ![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=flat&logo=jenkins&logoColor=white) **Jenkins** | Automates the build, test, and deploy pipeline |
| ![AWS](https://img.shields.io/badge/AWS_EC2-FF9900?style=flat&logo=amazonaws&logoColor=white) **AWS EC2** | The cloud server that hosts the live app |
| ![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white) **GitHub** | Source code + triggers the pipeline via webhook |

---

## 📋 Prerequisites

Before you start, you need:

- [ ] An **AWS account** (free tier is enough — use `t2.micro`)
- [ ] A **Docker Hub account** (free at hub.docker.com)
- [ ] A **GitHub account**
- [ ] Basic comfort with a **terminal / command line**
- [ ] Git installed on your laptop (`git --version` to check)

---

## 🚀 Getting Started (Local First)

### 1. Clone this repo

```bash
git clone https://github.com/YOUR_USERNAME/phase1-flask-app.git
cd phase1-flask-app
```

### 2. Run locally with Docker Compose

```bash
# Start both containers (Flask app + MySQL database)
docker compose up --build

# Visit http://localhost:5000 in your browser
```

That's it! Docker handles everything. You should see the Task Manager app.

### 3. Stop the app

```bash
# Stop containers (data is preserved in the volume)
docker compose down

# Stop AND wipe the database (fresh start)
docker compose down -v
```

---

## ☁️ Deploying to AWS EC2

### Step 1 — Launch an EC2 Instance

1. Log into AWS Console → EC2 → Launch Instance
2. Choose **Ubuntu 22.04 LTS** (free tier eligible)
3. Instance type: **t2.micro** (free tier)
4. Create or select a key pair — **download the .pem file**
5. Security group — allow inbound:
   - Port **22** (SSH — your IP only for security)
   - Port **5000** (Flask app — Anywhere)

### Step 2 — Install Docker on EC2

```bash
# SSH into your server
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose-plugin

# Allow current user to run Docker without sudo
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
```

### Step 3 — Copy the app to EC2 and run it

```bash
# From your laptop: copy the project files to EC2
scp -i your-key.pem -r ./phase1-flask-app ubuntu@YOUR_EC2_IP:~/

# SSH back in and start it
ssh -i your-key.pem ubuntu@YOUR_EC2_IP
cd phase1-flask-app
docker compose up -d   # -d = run in background (detached mode)

# Visit http://YOUR_EC2_IP:5000
```

---

## 🔄 Setting Up Jenkins CI/CD

> **Goal:** Every `git push` to GitHub automatically deploys to EC2 — no manual steps.

### Step 1 — Install Jenkins (on a separate t2.micro EC2)

```bash
# SSH into your Jenkins EC2 instance
ssh -i your-key.pem ubuntu@YOUR_JENKINS_EC2_IP

# Install Java (Jenkins needs it)
sudo apt update
sudo apt install -y openjdk-17-jdk

# Install Jenkins
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | \
    sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null

echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
    https://pkg.jenkins.io/debian-stable binary/ | \
    sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null

sudo apt update
sudo apt install -y jenkins

# Start Jenkins
sudo systemctl enable jenkins
sudo systemctl start jenkins

# Get the initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

Visit `http://YOUR_JENKINS_IP:8080` and follow the setup wizard.

### Step 2 — Add credentials to Jenkins

In Jenkins → Manage Jenkins → Credentials → Global → Add Credential:

| ID | Kind | What to put |
|----|------|-------------|
| `dockerhub-username` | Secret text | Your Docker Hub username |
| `dockerhub-password` | Secret text | Your Docker Hub password |
| `ec2-ssh-key` | SSH Username with private key | Your .pem file contents |

### Step 3 — Create the Pipeline job

1. Jenkins → New Item → Pipeline
2. Name it `flask-todo-pipeline`
3. Under "Pipeline Definition" → select **Pipeline script from SCM**
4. SCM: Git → paste your GitHub repo URL
5. Script Path: `Jenkinsfile`
6. Save

### Step 4 — Add a GitHub Webhook

In your GitHub repo → Settings → Webhooks → Add webhook:
- Payload URL: `http://YOUR_JENKINS_IP:8080/github-webhook/`
- Content type: `application/json`
- Trigger: "Just the push event"

Now every `git push` triggers the pipeline automatically! ✅

---

## 💰 Cost-Saving Tips (Stay in Free Tier)

| Tip | How |
|-----|-----|
| Use `t2.micro` instances only | Free tier gives you 750 hours/month |
| Stop EC2 when not using it | AWS Console → Instance → Stop (not Terminate!) |
| Set a billing alert | AWS → Billing → Budgets → Create budget at $5 |
| Use `us-east-1` region | Generally cheapest for most services |
| Delete unused EBS volumes | Stopped instances still have volumes that cost money |

**Monthly free tier estimate for this project: $0.00** (if using t2.micro within 750 hours)

---

## 🐛 Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| `Connection refused` on port 5000 | Security group not configured | Add inbound rule for port 5000 in AWS Console |
| `docker: permission denied` | User not in docker group | Run `sudo usermod -aG docker $USER` then log out and back in |
| Flask app can't connect to DB | MySQL not ready yet | Wait 30s and retry, or check `docker compose logs db` |
| Jenkins can't SSH to EC2 | Wrong key or IP | Check the `ec2-ssh-key` credential and update `YOUR_EC2_IP` in Jenkinsfile |
| `Port 5000 already in use` | Another process using it | Run `sudo lsof -i :5000` then kill the process |
| Image build fails | Syntax error in code | Check `docker compose logs web` for the error message |

---

## 📁 Project Structure

```
phase1-flask-app/
├── app.py                  # Flask application (routes + DB logic)
├── requirements.txt        # Python dependencies
├── Dockerfile              # How to package the app into a container
├── docker-compose.yml      # Runs Flask + MySQL together locally
├── init.sql                # Creates the database table on first run
├── Jenkinsfile             # The CI/CD pipeline definition
├── .gitignore              # Files Git should ignore
├── templates/
│   └── index.html          # The web UI
└── tests/
    └── test_app.py         # Basic smoke tests (run by Jenkins)
```

---

## 🧠 What I Learned

- How to **containerise** a Python web app with Docker
- How **Docker Compose** orchestrates multi-container applications
- How to set up a **CI/CD pipeline** that deploys automatically on every push
- How to securely store credentials in Jenkins (not in code!)
- How to provision and configure **AWS EC2** instances
- The difference between a **development** environment (local) and **production** (EC2)

---

## 🔗 Related Projects

- **Phase 2:** [Three-Tier Microservices App with Kubernetes](../phase2-k8s-app) *(coming soon)*
- **Phase 3:** [Cloud Infrastructure with Terraform on Azure](../phase3-terraform) *(coming soon)*
- **Phase 4:** [Prometheus Observability Stack](../phase4-monitoring) *(coming soon)*

---

*Built as part of a DevOps learning portfolio. See the full roadmap [here](https://github.com/YOUR_USERNAME).*
