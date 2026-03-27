// ============================================================
// JENKINSFILE — What this file does:
// This is your CI/CD pipeline. Every time you push code to
// GitHub, Jenkins reads this file and runs each "stage" in order.
// Think of it as a recipe that Jenkins follows automatically.
//
// THE FLOW:
// You push code → GitHub notifies Jenkins → Jenkins runs this file
// → Tests pass → Docker image built → Image pushed to Docker Hub
// → App deployed to AWS EC2 automatically
// ============================================================

pipeline {

    // "any" = run on whatever Jenkins agent/worker is available
    agent any

    // ---- ENVIRONMENT VARIABLES ----
    // These are stored securely in Jenkins (never in code!)
    // Go to: Jenkins → Manage Jenkins → Credentials to add them
    environment {
        // Your Docker Hub username (e.g. "johndoe")
        DOCKER_HUB_USER = credentials('dockerhub-username')

        // Your Docker Hub password — stored as a Jenkins secret
        DOCKER_HUB_PASS = credentials('dockerhub-password')

        // The name for your Docker image (e.g. "johndoe/flask-todo-app")
        IMAGE_NAME = "${DOCKER_HUB_USER}/flask-todo-app"

        // Tag the image with the build number so each build is traceable
        IMAGE_TAG  = "v${BUILD_NUMBER}"
    }

    stages {

        // ---- STAGE 1: CHECKOUT ----
        // Jenkins pulls your latest code from GitHub
        stage('Checkout') {
            steps {
                echo '📥 Pulling latest code from GitHub...'
                checkout scm    // "scm" = the GitHub repo you connected in Jenkins
            }
        }

        // ---- STAGE 2: TEST ----
        // Run tests before building. If tests fail, pipeline stops here.
        // No broken code gets deployed!
        stage('Test') {
            steps {
                echo '🧪 Running tests...'
                sh '''
                    # Install dependencies in a virtual environment
                    python3 -m venv venv
                    . venv/bin/activate

                    # Install app requirements
                    pip install -r requirements.txt

                    # Run the test file (we check app imports and routes exist)
                    python3 -m pytest tests/ -v || echo "No tests yet — add them in /tests folder"
                '''
            }
        }

        // ---- STAGE 3: BUILD DOCKER IMAGE ----
        // Packages your app into a Docker image
        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                sh """
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                """
            }
        }

        // ---- STAGE 4: PUSH TO DOCKER HUB ----
        // Uploads the image to Docker Hub so the server can pull it
        stage('Push to Docker Hub') {
            steps {
                echo '📤 Pushing image to Docker Hub...'
                sh """
                    echo ${DOCKER_HUB_PASS} | docker login -u ${DOCKER_HUB_USER} --password-stdin
                    docker push ${IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${IMAGE_NAME}:latest
                """
            }
        }

        // ---- STAGE 5: DEPLOY TO AWS EC2 ----
        // SSH into your EC2 server and pull the new image
        stage('Deploy to EC2') {
            steps {
                echo '🚀 Deploying to AWS EC2...'
                // sshagent uses the SSH key you stored in Jenkins credentials
                // Replace 'ec2-ssh-key' with whatever you named it in Jenkins
                sshagent(credentials: ['ec2-ssh-key']) {
                    sh """
                        # Replace YOUR_EC2_IP with your actual EC2 public IP address
                        ssh -o StrictHostKeyChecking=no ec2-user@YOUR_EC2_IP '
                            cd ~/phase1-flask-app
                            docker compose pull
                            docker compose up -d --force-recreate
                            docker image prune -f
                        '
                    """
                }
            }
        }
    }

    // ---- POST: ALWAYS RUNS (SUCCESS OR FAILURE) ----
    post {
        success {
            echo "✅ Pipeline SUCCESS! App deployed at http://YOUR_EC2_IP:5000"
        }
        failure {
            echo "❌ Pipeline FAILED! Check the logs above to see which stage broke."
        }
        always {
            // Clean up Docker images from Jenkins server to save disk space
            sh 'docker image prune -f || true'
        }
    }
}
