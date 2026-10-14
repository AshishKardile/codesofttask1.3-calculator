pipeline {
    agent any

    environment {
        // Change this to your personal Docker Hub username
        DOCKER_HUB_USER = 'ashishkardile'
        IMAGE_NAME      = "${DOCKER_HUB_USER}/calculator-app"
        IMAGE_TAG       = "${BUILD_NUMBER}"
        // Credential ID created in Jenkins -> Manage Jenkins -> Credentials
        DOCKER_CRED_ID  = 'dockerhub-credentials'
    }

    stages {
        stage('Source Code Checkout') {
            steps {
                echo "=========================================================="
                echo "Stage 1: Pulling latest source code from GitHub repository"
                echo "=========================================================="
                checkout scm
            }
        }

        stage('Build and Test') {
            steps {
                echo "=========================================================="
                echo "Stage 2: Building application and running automated tests"
                echo "=========================================================="
                sh '''
                    if [ -f test/test_app.sh ]; then
                        chmod +x test/test_app.sh
                        ./test/test_app.sh
                    elif command -v python3 >/dev/null 2>&1; then
                        python3 test/test_app.py
                    else
                        echo "Warning: Test runners not found, performing fallback sanity check..."
                        test -s index.html && test -s style.css && test -s script.js
                        echo "Core web asset files verified."
                    fi
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo "=========================================================="
                echo "Stage 3: Building Docker container image"
                echo "Tagging: ${IMAGE_NAME}:${IMAGE_TAG} and ${IMAGE_NAME}:latest"
                echo "=========================================================="
                sh """
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest .
                """
            }
        }

        stage('Push Image') {
            steps {
                echo "=========================================================="
                echo "Stage 4: Publishing Docker image to Docker Hub registry"
                echo "=========================================================="
                withCredentials([usernamePassword(
                    credentialsId: "${DOCKER_CRED_ID}",
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        echo "\$DOCKER_PASS" | docker login -u "\$DOCKER_USER" --password-stdin
                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME}:latest
                    """
                }
            }
        }

        stage('Minikube Deployment') {
            steps {
                echo "=========================================================="
                echo "Stage 5: Deploying application to Minikube cluster"
                echo "=========================================================="
                sh """
                    # 1. Apply Kubernetes Deployment and Service manifests
                    kubectl apply -f k8s/deployment.yaml
                    kubectl apply -f k8s/service.yaml

                    # 2. Update deployment to pull newly built Docker image tag
                    kubectl set image deployment/calculator-deployment calculator-app=${IMAGE_NAME}:${IMAGE_TAG} --record=true || \
                    kubectl set image deployment/calculator-deployment calculator-app=${IMAGE_NAME}:${IMAGE_TAG}

                    # 3. Wait for rolling update to complete successfully
                    kubectl rollout status deployment/calculator-deployment --timeout=120s
                """
            }
        }

        stage('Verification') {
            steps {
                echo "=========================================================="
                echo "Stage 6: Verifying running pods, service & application"
                echo "=========================================================="
                sh """
                    echo "--- Kubernetes Pods Status ---"
                    kubectl get pods -l app=calculator -o wide

                    echo "--- Kubernetes Service Status ---"
                    kubectl get svc calculator-service

                    echo "--- Deployment Rollout History ---"
                    kubectl rollout history deployment/calculator-deployment

                    echo "--- Access URL Information ---"
                    if command -v minikube >/dev/null 2>&1; then
                        minikube service calculator-service --url || true
                    fi
                """
            }
        }
    }

    post {
        always {
            echo "Pipeline execution finished."
            sh 'docker logout || true'
        }
        success {
            echo "=========================================================="
            echo "SUCCESS: CI/CD Pipeline executed cleanly!"
            echo "Build #${BUILD_NUMBER} deployed successfully to Minikube."
            echo "=========================================================="
        }
        failure {
            echo "=========================================================="
            echo "FAILURE: Pipeline failed at one of the stages."
            echo "Inspect the console output above to debug."
            echo "=========================================================="
        }
    }
}
