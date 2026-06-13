pipeline {
    agent any

    environment {
        DOCKER_HUB_CREDENTIALS = credentials('dockerhub-credentials')
        DOCKERHUB_USERNAME = 'shamaimm'
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
                    docker build -t ${IMAGE_UNSTABLE} .
                    docker stop sentiment-test || true
                    docker rm sentiment-test || true
                    docker run -d --name sentiment-test -p 5000:5000 ${IMAGE_UNSTABLE}
                    sleep 15
                '''
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                    docker run --rm \
                        --network host \
                        ${IMAGE_UNSTABLE} \
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
                        ${IMAGE_UNSTABLE} \
                        python -m pytest tests/test_ui.py -v
                '''
            }
        }

        stage('Build and Push') {
            steps {
                sh '''
                    echo ${DOCKER_HUB_CREDENTIALS_PSW} | docker login -u ${DOCKER_HUB_CREDENTIALS_USR} --password-stdin
                    docker push ${IMAGE_UNSTABLE}

                    git stash || true
                    git fetch origin stable-fallback
                    git checkout stable-fallback
                    docker build -t ${IMAGE_STABLE} .
                    docker push ${IMAGE_STABLE}
                    git checkout main
                '''
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    export KUBECONFIG=/home/ubuntu/.kube/config
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
