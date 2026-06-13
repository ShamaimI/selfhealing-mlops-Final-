pipeline {
    agent any

    environment {
        DOCKER_HUB_CREDENTIALS = credentials('dockerhub-credentials')
        IMAGE_UNSTABLE = 'shamaimm/sentiment-api:unstable'
        IMAGE_STABLE = 'shamaimm/sentiment-api:stable'
    }

    stages {
        stage('Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                sh '''
                    docker build -t shamaimm/sentiment-api:unstable .
                    docker stop sentiment-test || true
                    docker rm sentiment-test || true
                    docker run -d --name sentiment-test -p 5000:5000 shamaimm/sentiment-api:unstable
                    sleep 15
                '''
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                    docker run --rm \
                        --network host \
                        shamaimm/sentiment-api:unstable \
                        python -m pytest tests/test_api.py -v
                '''
            }
        }

        stage('UI Test') {
            steps {
                sh '''
                    docker run --rm \
                        --network host \
                        -e DISPLAY=:99 \
                        shamaimm/sentiment-api:unstable \
                        python -m pytest tests/test_ui.py -v
                '''
            }
        }

        stage('Build and Push') {
            steps {
                sh '''
                    echo $DOCKER_HUB_CREDENTIALS_PSW | docker login -u $DOCKER_HUB_CREDENTIALS_USR --password-stdin
                    docker push shamaimm/sentiment-api:unstable

                    git fetch origin stable-fallback
                    git checkout stable-fallback

                    cat > Dockerfile.stable << 'DFEOF'
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
RUN mkdir -p /app/logs
EXPOSE 5000
CMD ["python", "app.py"]
DFEOF

                    docker build -t shamaimm/sentiment-api:stable -f Dockerfile.stable .
                    docker push shamaimm/sentiment-api:stable
                    git checkout main
                '''
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    export KUBECONFIG=/var/lib/jenkins/.kube/config
                    kubectl apply -f k8s/pvc.yaml
                    kubectl apply -f k8s/blue-deployment.yaml
                    kubectl apply -f k8s/green-deployment.yaml
                    kubectl apply -f k8s/service.yaml
                '''
            }
        }
    }

    post {
        always {
            sh '''
                docker stop sentiment-test || true
                docker rm sentiment-test || true
            '''
        }
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}
