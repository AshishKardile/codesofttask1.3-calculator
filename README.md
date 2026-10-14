# CI/CD Pipeline Implementation & Deployment on Kubernetes (Minikube)
**Course:** TYCSE · Cloud Computing and DevOps  
**Assignment:** CCA 2 – CI/CD Pipeline Implementation & Deployment of an Existing Project  
**Author:** Ashish Kardile  
**Project:** Premium Skeuomorphic Desktop Calculator  

---

## 1. Project Overview
This project is an interactive, high-fidelity **Premium Skeuomorphic Desktop Calculator** built with HTML5, CSS3, and JavaScript. It features responsive physical key actions, simulated LCD segment display with memory indicators (`M`), and a solar panel aesthetic.

- **Frontend Tech Stack:** HTML5, CSS3, Vanilla JavaScript, Nginx (Alpine Linux)
- **Containerization:** Docker
- **Container Registry:** Docker Hub (`ashishkardile/calculator-app`)
- **CI/CD Automation:** Jenkins (Declarative Pipeline via `Jenkinsfile`)
- **Container Orchestration:** Kubernetes (Minikube cluster on AWS EC2)

---

## 2. CI/CD Architecture Workflow

```
[ Developer ]
      │  git push (source code update)
      ▼
[ GitHub Repository ]
      │  Webhook / Poll SCM trigger
      ▼
[ Jenkins (AWS EC2) ]
   ├── Stage 1: Checkout SCM (Pull latest commit)
   ├── Stage 2: Build & Test (Static asset validation & JS syntax check)
   ├── Stage 3: Docker Build (Containerize with Nginx Alpine)
   ├── Stage 4: Push Image (Publish tagged image to Docker Hub)
   ├── Stage 5: Minikube Deployment (Rolling update of K8s manifests)
   └── Stage 6: Verification (Pod readiness & endpoint health checks)
      │
      ▼
[ Minikube Kubernetes Cluster ]
   ├── Deployment: calculator-deployment (2 Replicas, Zero-Downtime Rolling Update)
   └── Service: calculator-service (NodePort 30080)
      │
      ▼
[ End-User / Browser ] (Access calculator via http://<AWS-Public-IP>:30080)
```

---

## 3. Pipeline Stages Explained

| Stage | Name | Action & Technical Description |
| :--- | :--- | :--- |
| **1** | **Source Code Checkout** | Jenkins pulls the latest source code from the GitHub repository `codesofttask1.3-calculator` via Git SCM plugin. |
| **2** | **Build and Test** | Runs `test/test_app.sh` (or `test/test_app.py`) to validate file integrity, verify essential HTML DOM nodes, check CSS braces, and validate JavaScript syntax before building the image. |
| **3** | **Docker Build** | Uses `Dockerfile` with lightweight `nginx:alpine` to package the web assets into a production container image. Tagged with both `${BUILD_NUMBER}` and `latest`. |
| **4** | **Push Image** | Authenticates securely with Docker Hub using Jenkins credentials (`dockerhub-credentials`) and pushes both tags (`:BUILD_NUMBER` and `:latest`). |
| **5** | **Minikube Deployment** | Applies Kubernetes manifests (`k8s/deployment.yaml` and `k8s/service.yaml`). Uses `kubectl set image` to trigger a rolling update with zero downtime, and verifies rollout status (`kubectl rollout status`). |
| **6** | **Verification** | Inspects running pods (`kubectl get pods -o wide`), deployment replicas, and verifies NodePort service endpoint accessibility. |

---

## 4. Setting up Infrastructure on AWS EC2

### 4.1. Launch EC2 Instance
1. **AMI:** Ubuntu Server 22.04 LTS (HVM), SSD Volume Type
2. **Instance Type:** `t3.medium` (Minimum 2 vCPUs and 4 GiB RAM required for Minikube + Jenkins + Docker)
3. **Storage:** 25–30 GiB gp3
4. **Security Group Inbound Rules:**
   - `SSH` (Port 22) - Your IP
   - `Custom TCP` (Port 8080) - `0.0.0.0/0` (Jenkins Web UI)
   - `Custom TCP` (Port 30080) - `0.0.0.0/0` (Kubernetes NodePort application access)

---

### 4.2. Server Installation Commands

Connect via SSH to your EC2 instance and run:

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# 1. Install Java 17 (Required by Jenkins)
sudo apt install -y openjdk-17-jdk

# 2. Install Docker
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker ubuntu

# 3. Install Jenkins
sudo wget -O /usr/share/keyrings/jenkins-keyring.asc https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/" | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt update
sudo apt install -y jenkins
sudo systemctl enable --now jenkins

# Add jenkins user to docker group (CRUCIAL)
sudo usermod -aG docker jenkins

# 4. Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# 5. Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Start Minikube using Docker driver
minikube start --driver=docker

# Configure kubectl access for jenkins user
sudo mkdir -p /var/lib/jenkins/.kube
sudo cp -r ~/.kube/config /var/lib/jenkins/.kube/
sudo cp -r ~/.minikube /var/lib/jenkins/
sudo chown -R jenkins:jenkins /var/lib/jenkins/.kube /var/lib/jenkins/.minikube

# Restart Jenkins service to apply new permissions
sudo systemctl restart jenkins
```

---

## 5. Jenkins Credentials Configuration
1. Open Jenkins: `http://<EC2-PUBLIC-IP>:8080`.
2. Unlock using initial admin password: `sudo cat /var/lib/jenkins/secrets/initialAdminPassword`.
3. Install suggested plugins (including **Git Plugin**, **Pipeline**, **Credentials Binding Plugin**).
4. Navigate to **Manage Jenkins** $\rightarrow$ **Credentials** $\rightarrow$ **System** $\rightarrow$ **Global credentials (unrestricted)** $\rightarrow$ **Add Credentials**:
   - **Kind:** Username with password
   - **Scope:** Global
   - **Username:** `<Your-DockerHub-Username>`
   - **Password:** `<Your-DockerHub-Password-or-Access-Token>`
   - **ID:** `dockerhub-credentials` (Must match the ID in `Jenkinsfile`)
   - **Description:** Docker Hub Login Credentials

---

## 6. Creating and Running the Jenkins Pipeline
1. In Jenkins dashboard, click **New Item**.
2. Enter item name: `calculator-cicd-pipeline` and select **Pipeline**. Click **OK**.
3. Under **Pipeline** section:
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** `https://github.com/AshishKardile/codesofttask1.3-calculator.git`
   - **Branch Specifier:** `*/main`
   - **Script Path:** `Jenkinsfile`
4. Click **Save**.
5. Click **Build Now** to execute the first run.

---

## 7. Kubernetes Deployment Manifests

### Deployment (`k8s/deployment.yaml`)
- **Replicas:** 2 (High Availability)
- **Strategy:** `RollingUpdate` (`maxSurge: 1`, `maxUnavailable: 0` for 100% uptime during deployments)
- **Container Port:** 80
- **Probes:** Configured `livenessProbe` and `readinessProbe` on `/`

### Service (`k8s/service.yaml`)
- **Type:** `NodePort`
- **NodePort:** `30080` (Directly accessible through Minikube node or forwarded port)

Access command on Minikube:
```bash
# Get service URL
minikube service calculator-service --url

# Port forward to access from outside EC2:
kubectl port-forward --address 0.0.0.0 service/calculator-service 30080:80
```

---

## 8. Second Run: Demonstrating Source Code Change

As required by the assignment guidelines:
1. Make a visible change in the source code (e.g., update the calculator title in `index.html` from *"Premium Off-White Desktop Calculator"* to *"Premium Off-White Desktop Calculator v2.0"* or update a color theme in `style.css`).
2. Commit and push changes:
   ```bash
   git add index.html
   git commit -m "Update calculator banner to v2.0 for 2nd CI/CD deployment"
   git push origin main
   ```
3. Trigger **Build Now** in Jenkins (or auto-triggered via GitHub Webhook).
4. Observe the pipeline:
   - Jenkins builds image with new tag `${BUILD_NUMBER}` (e.g. `:2`).
   - Pushes new image to Docker Hub.
   - Executes `kubectl set image` which replaces pods one-by-one without downtime.
   - Refresh browser at `http://<EC2-PUBLIC-IP>:30080` to verify the updated version!

---

## 9. Submission Checklist & Screenshots Required

| Screenshot # | Description | What to Show |
| :---: | :--- | :--- |
| **1** | GitHub Repository | Codebase containing `Dockerfile`, `Jenkinsfile`, and `k8s/` folder. |
| **2** | Jenkins Configuration | Pipeline job settings pointing to GitHub repository & configured Docker Hub credentials. |
| **3** | Jenkins Pipeline Run 1 | All 6 green stages completed in Jenkins Pipeline Stage View. |
| **4** | Docker Hub Registry | Image repository showing tags `:1` and `:latest` pushed. |
| **5** | Kubernetes Cluster Status | Terminal showing `kubectl get pods,svc -o wide` with 2 Running pods. |
| **6** | Running Web Application | Browser displaying the calculator at port `30080`. |
| **7** | Git Commit (Code Change) | Commit diff showing modification made to source code. |
| **8** | Jenkins Pipeline Run 2 | Successful execution of Build #2 with rolling update output. |
| **9** | Updated Application in Browser | Browser showing updated v2.0 application live. |

---

## 10. Viva & Evaluation Preparation

- **Q: Why use `nginx:alpine` for the base image?**  
  *A:* Alpine Linux is extremely lightweight (~25 MB total container size), has a very small attack surface, fast pull/build times, and high performance for serving static HTML/CSS/JS.

- **Q: What is a Rolling Update in Kubernetes?**  
  *A:* It incrementally replaces old pod instances with new ones without taking down the service. With `maxUnavailable: 0` and `maxSurge: 1`, Kubernetes spins up a new pod first and only terminates an old pod once the new pod passes its `readinessProbe`.

- **Q: How are credentials managed securely in the pipeline?**  
  *A:* Docker credentials are not hardcoded in the repository. They are stored encrypted inside the Jenkins Credentials Store and injected into the pipeline at runtime using `withCredentials([usernamePassword(...)])`.
